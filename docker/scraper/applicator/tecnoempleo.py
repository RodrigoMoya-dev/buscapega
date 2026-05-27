from playwright.sync_api import BrowserContext

from .base import BaseApplicator, DEFAULT_TIMEOUT
from .result import ApplyResult, session_expired, captcha_detectado
from . import cover_letter as cl


class TecnoempleoApplicator(BaseApplicator):
    portal_key = "tecnoempleo"
    portal_name = "Tecnoempleo"
    login_url = "https://www.tecnoempleo.com/login.php"

    def _do_apply(self, context: BrowserContext, offer: dict) -> ApplyResult:
        page = context.new_page()
        url = offer.get("url", "")

        page.goto(url, wait_until="domcontentloaded", timeout=DEFAULT_TIMEOUT)

        if "login" in page.url:
            return session_expired(url)

        letter = cl.generate(offer)

        # Tecnoempleo: botón "Inscribirme" o "Solicitar empleo"
        apply_btn = page.query_selector(
            "a:has-text('Inscribirme'), a:has-text('Solicitar'), "
            "button:has-text('Inscribirme'), .btn-inscribirse, "
            "a[href*='inscribir'], a[href*='solicitar']"
        )
        if not apply_btn:
            return ApplyResult(
                status="fallido",
                requiere_humano=True,
                motivo="No se encontró el botón de inscripción. "
                       "La oferta puede estar cerrada o requiere CV subido manualmente.",
                paso_alcanzado="Carga de la oferta",
                url_continuar=url,
            )

        apply_btn.click()
        page.wait_for_load_state("domcontentloaded", timeout=DEFAULT_TIMEOUT)

        if "login" in page.url:
            return session_expired(url)

        if self._has_captcha(page):
            return captcha_detectado(page.url, "Formulario de inscripción abierto")

        # Rellenar carta si hay campo de texto libre
        cover_field = page.query_selector("textarea")
        if cover_field:
            cover_field.fill(letter)
            paso = "Carta rellenada"
        else:
            paso = "Formulario abierto (inscripción directa sin carta)"

        submit_btn = page.query_selector("button[type='submit'], input[type='submit']")
        if not submit_btn:
            return ApplyResult(
                status="parcial",
                requiere_humano=True,
                motivo="No se encontró el botón de envío final.",
                paso_alcanzado=paso,
                url_continuar=page.url,
                cover_letter=letter,
            )

        submit_btn.click()
        page.wait_for_load_state("domcontentloaded", timeout=DEFAULT_TIMEOUT)

        if self._has_captcha(page):
            return captcha_detectado(page.url, paso + " → intento de envío")

        success = bool(page.query_selector(
            "*:has-text('inscripción realizada'), *:has-text('candidatura enviada'), "
            "*:has-text('solicitud enviada'), *:has-text('gracias')"
        ))

        if success:
            return ApplyResult(
                status="ok",
                requiere_humano=False,
                motivo="",
                paso_alcanzado="Inscripción enviada y confirmada",
                url_continuar=url,
                cover_letter=letter,
            )

        return ApplyResult(
            status="parcial",
            requiere_humano=True,
            motivo="Formulario enviado pero no se detectó confirmación de inscripción. "
                   "Verifica en tu cuenta de Tecnoempleo.",
            paso_alcanzado="Formulario enviado",
            url_continuar=page.url,
            cover_letter=letter,
        )
