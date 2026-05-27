from playwright.sync_api import BrowserContext

from .base import BaseApplicator, DEFAULT_TIMEOUT
from .result import ApplyResult, session_expired, captcha_detectado
from . import cover_letter as cl


class GetOnBrdApplicator(BaseApplicator):
    portal_key = "getonbrd"
    portal_name = "GetOnBrd"
    login_url = "https://www.getonbrd.com/sessions/new"

    def _do_apply(self, context: BrowserContext, offer: dict) -> ApplyResult:
        page = context.new_page()
        url = offer.get("url", "")

        # 1. Navegar a la oferta
        page.goto(url, wait_until="domcontentloaded", timeout=DEFAULT_TIMEOUT)

        # 2. Verificar sesión — si hay redirect al login, sesión expirada
        if "sessions/new" in page.url or "login" in page.url:
            return session_expired(url)

        # 3. Buscar botón "Apply" / "Postular"
        apply_btn = page.query_selector(
            "a[href*='/apply'], a[data-cy='apply-button'], "
            "button:has-text('Apply'), button:has-text('Postular'), "
            "a:has-text('Apply'), a:has-text('Postular')"
        )
        if not apply_btn:
            return ApplyResult(
                status="fallido",
                requiere_humano=True,
                motivo="No se encontró el botón de postulación en la página. "
                       "Es posible que la oferta haya sido cerrada o que el portal cambió su estructura.",
                paso_alcanzado="Carga de la oferta",
                url_continuar=url,
            )

        # 4. Hacer click en Apply
        apply_btn.click()
        page.wait_for_load_state("domcontentloaded", timeout=DEFAULT_TIMEOUT)

        if "sessions/new" in page.url or "login" in page.url:
            return session_expired(url)

        # 5. Generar carta de presentación
        letter = cl.generate(offer)

        # 6. Buscar campo de motivación / cover letter
        cover_field = page.query_selector(
            "textarea[name*='cover'], textarea[name*='motivation'], "
            "textarea[placeholder*='cover'], textarea[placeholder*='motivac'], "
            "textarea[id*='cover'], textarea[id*='motivation'], "
            "#application_cover_letter, #application_motivation_letter, "
            "textarea"
        )
        if cover_field:
            cover_field.fill(letter)
            paso = "Carta de presentación rellenada"
        else:
            paso = "Formulario abierto (sin campo de carta detectado)"

        # 7. Detectar CAPTCHA antes de enviar
        if self._has_captcha(page):
            return captcha_detectado(page.url, paso)

        # 8. Buscar y clickear botón de envío
        submit_btn = page.query_selector(
            "button[type='submit'], input[type='submit'], "
            "button:has-text('Apply'), button:has-text('Postular'), "
            "button:has-text('Enviar'), button:has-text('Submit')"
        )
        if not submit_btn:
            return ApplyResult(
                status="parcial",
                requiere_humano=True,
                motivo="No se encontró el botón de envío final del formulario.",
                paso_alcanzado=paso,
                url_continuar=page.url,
                cover_letter=letter,
            )

        submit_btn.click()
        page.wait_for_load_state("domcontentloaded", timeout=DEFAULT_TIMEOUT)

        # 9. Verificar éxito — GetOnBrd redirige o muestra mensaje de confirmación
        success = bool(page.query_selector(
            ".application-success, [data-cy='application-success'], "
            "*:has-text('application received'), *:has-text('postulación recibida'), "
            "*:has-text('successfully applied'), *:has-text('gracias por postular')"
        ))
        if success or "applied" in page.url or "success" in page.url:
            return ApplyResult(
                status="ok",
                requiere_humano=False,
                motivo="",
                paso_alcanzado="Postulación enviada y confirmada",
                url_continuar=url,
                cover_letter=letter,
            )

        # Si no hay confirmación clara, marcar como parcial
        return ApplyResult(
            status="parcial",
            requiere_humano=True,
            motivo="El formulario fue enviado pero no se recibió confirmación explícita de éxito. "
                   "Verifica manualmente si la postulación quedó registrada.",
            paso_alcanzado="Formulario enviado, confirmación no detectada",
            url_continuar=page.url,
            cover_letter=letter,
        )
