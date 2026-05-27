from playwright.sync_api import BrowserContext

from .base import BaseApplicator, DEFAULT_TIMEOUT
from .result import ApplyResult, session_expired, captcha_detectado
from . import cover_letter as cl


class ChumiITApplicator(BaseApplicator):
    portal_key = "chumiit"
    portal_name = "Chumi-IT"
    login_url = "https://chumi-it.com/login"

    def _do_apply(self, context: BrowserContext, offer: dict) -> ApplyResult:
        page = context.new_page()
        url = offer.get("url", "")

        page.goto(url, wait_until="domcontentloaded", timeout=DEFAULT_TIMEOUT)

        if "login" in page.url:
            return session_expired(url)

        letter = cl.generate(offer)

        apply_btn = page.query_selector(
            "button:has-text('Apply'), a:has-text('Apply'), "
            "button:has-text('Postular'), a:has-text('Postular'), "
            ".apply-btn, [data-action='apply'], [href*='apply']"
        )
        if not apply_btn:
            return ApplyResult(
                status="fallido",
                requiere_humano=True,
                motivo="No se encontró el botón de postulación en Chumi-IT. "
                       "La oferta puede estar cerrada o ser de aplicación externa.",
                paso_alcanzado="Carga de la oferta",
                url_continuar=url,
            )

        apply_btn.click()
        page.wait_for_load_state("domcontentloaded", timeout=DEFAULT_TIMEOUT)

        if "login" in page.url:
            return session_expired(url)

        if self._has_captcha(page):
            return captcha_detectado(page.url, "Formulario de postulación abierto")

        cover_field = page.query_selector(
            "textarea[name*='cover'], textarea[name*='motivation'], "
            "textarea[name*='message'], textarea[placeholder*='cover'], "
            "textarea"
        )
        if cover_field:
            cover_field.fill(letter)
            paso = "Carta de presentación rellenada"
        else:
            paso = "Formulario abierto (sin campo de carta)"

        submit_btn = page.query_selector("button[type='submit'], input[type='submit']")
        if not submit_btn:
            return ApplyResult(
                status="parcial",
                requiere_humano=True,
                motivo="No se encontró el botón de envío.",
                paso_alcanzado=paso,
                url_continuar=page.url,
                cover_letter=letter,
            )

        submit_btn.click()
        page.wait_for_load_state("domcontentloaded", timeout=DEFAULT_TIMEOUT)

        if self._has_captcha(page):
            return captcha_detectado(page.url, paso + " → intento de envío")

        success = bool(page.query_selector(
            "*:has-text('application sent'), *:has-text('successfully applied'), "
            "*:has-text('postulación enviada'), *:has-text('gracias')"
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
            motivo="Formulario enviado sin confirmación explícita. "
                   "Verifica en tu cuenta de Chumi-IT.",
            paso_alcanzado="Formulario enviado",
            url_continuar=page.url,
            cover_letter=letter,
        )
