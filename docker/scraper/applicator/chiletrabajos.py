import os
import httpx
from playwright.sync_api import BrowserContext

from .base import BaseApplicator, DEFAULT_TIMEOUT
from .result import ApplyResult, session_expired, captcha_detectado
from . import cover_letter as cl

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")


def _fetch_answers() -> list[dict]:
    """Obtiene respuestas activas desde el backend (portal=chiletrabajos + globales)."""
    try:
        r = httpx.get(f"{BACKEND_URL}/api/answers?portal=chiletrabajos", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"[ChileTrabajos] No se pudieron cargar respuestas: {e}")
    return []


def _match_answer(label_text: str, answers: list[dict]) -> str:
    """Devuelve la primera respuesta cuyos keywords aparecen en el texto del label."""
    label_lower = label_text.lower()
    for item in answers:
        for kw in item.get("keywords", []):
            if kw.lower() in label_lower:
                return item["respuesta"]
    return ""


def _get_label_text(page, element) -> str:
    """Busca el texto de la etiqueta asociada a un input/textarea."""
    field_id = element.get_attribute("id") or ""
    if field_id:
        label = page.query_selector(f"label[for='{field_id}']")
        if label:
            return label.inner_text().strip()
    return page.evaluate(
        """(el) => {
            const parent = el.closest('div, p, li, .form-group, .field');
            if (parent) {
                const lbl = parent.querySelector('label');
                if (lbl) return lbl.textContent.trim();
            }
            let sib = el.previousElementSibling;
            while (sib) {
                if (sib.tagName === 'LABEL') return sib.textContent.trim();
                sib = sib.previousElementSibling;
            }
            return '';
        }""",
        element,
    )


class ChileTrabajosApplicator(BaseApplicator):
    portal_key = "chiletrabajos"
    portal_name = "ChileTrabajos"
    login_url = "https://www.chiletrabajos.cl/login"

    def _do_apply(self, context: BrowserContext, offer: dict) -> ApplyResult:
        page = context.new_page()
        url = offer.get("url", "")

        page.goto(url, wait_until="domcontentloaded", timeout=DEFAULT_TIMEOUT)

        if "login" in page.url:
            return session_expired(url)

        letter = cl.generate(offer)

        apply_btn = page.query_selector(
            "button:has-text('Postular'), a:has-text('Postular'), "
            "button:has-text('Inscribirse'), a:has-text('Inscribirse'), "
            ".btn-postular, .postular-btn, [href*='postular']"
        )
        if not apply_btn:
            return ApplyResult(
                status="fallido",
                requiere_humano=True,
                motivo="No se encontró el botón de postulación. La oferta puede estar cerrada.",
                paso_alcanzado="Carga de la oferta",
                url_continuar=url,
            )

        apply_btn.click()
        page.wait_for_load_state("domcontentloaded", timeout=DEFAULT_TIMEOUT)

        if "login" in page.url:
            return session_expired(url)

        if self._has_captcha(page):
            return captcha_detectado(page.url, "Formulario de postulación abierto")

        answers = _fetch_answers()
        paso = self._fill_form(page, letter, answers, offer)

        submit_btn = page.query_selector("button[type='submit'], input[type='submit']")
        if not submit_btn:
            return ApplyResult(
                status="parcial",
                requiere_humano=True,
                motivo="No se encontró el botón de envío del formulario.",
                paso_alcanzado=paso,
                url_continuar=page.url,
                cover_letter=letter,
            )

        submit_btn.click()
        page.wait_for_load_state("domcontentloaded", timeout=DEFAULT_TIMEOUT)

        if self._has_captcha(page):
            return captcha_detectado(page.url, paso + " → intento de envío")

        success = bool(page.query_selector(
            "*:has-text('postulación enviada'), *:has-text('inscripción exitosa'), "
            "*:has-text('candidatura enviada'), *:has-text('gracias')"
        ))

        if success:
            return ApplyResult(
                status="ok",
                requiere_humano=False,
                motivo="",
                paso_alcanzado="Postulación enviada y confirmada",
                url_continuar=url,
                cover_letter=letter,
            )

        return ApplyResult(
            status="parcial",
            requiere_humano=True,
            motivo="Formulario enviado sin confirmación explícita. Verifica en tu cuenta de ChileTrabajos.",
            paso_alcanzado="Formulario enviado",
            url_continuar=page.url,
            cover_letter=letter,
        )

    def _fill_form(self, page, letter: str, answers: list[dict], offer: dict) -> str:
        paso = "Formulario de postulación abierto"
        filled = 0

        # 1. Carta de presentación (selector específico; evita las preguntas custom)
        cover_field = page.query_selector(
            "textarea[name*='carta'], textarea[name*='cover'], textarea[name*='mensaje'], "
            "textarea[id*='carta'], textarea[id*='cover'], textarea[placeholder*='carta']"
        )
        if cover_field:
            cover_field.fill(letter)
            paso = "Carta de presentación rellenada"
            filled += 1

        # 2. Pretensiones de renta
        renta_answer = _match_answer("pretensiones_renta", answers)
        if renta_answer:
            renta_field = page.query_selector(
                "input[name*='renta'], input[id*='renta'], "
                "input[placeholder*='600000'], input[type='number']"
            )
            if renta_field:
                renta_field.fill(renta_answer)
                filled += 1

        # 3. Disponibilidad inmediata
        disp_answer = _match_answer("disponibilidad_inmediata", answers)
        if disp_answer.strip().lower() == "true":
            try:
                checkbox = page.get_by_label("Disponibilidad Inmediata")
                if checkbox.count() > 0 and not checkbox.is_checked():
                    checkbox.check()
                    filled += 1
            except Exception:
                pass

        # 4. Preguntas personalizadas (textareas con label)
        textareas = page.query_selector_all("textarea")
        for textarea in textareas:
            if cover_field and page.evaluate("(a, b) => a === b", textarea, cover_field):
                continue

            label_text = _get_label_text(page, textarea)
            if not label_text:
                continue

            stored = _match_answer(label_text, answers)
            if stored:
                textarea.fill(stored)
                filled += 1
            else:
                generated = cl.generate_answer(label_text, offer)
                if generated:
                    textarea.fill(generated)
                    filled += 1

        if filled > 0:
            paso = f"Formulario rellenado ({filled} campo(s) completado(s))"

        return paso
