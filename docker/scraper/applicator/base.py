import json
from abc import ABC, abstractmethod
from pathlib import Path
from playwright.sync_api import sync_playwright, BrowserContext, Page

from .result import ApplyResult, session_expired, sin_sesion

COOKIES_DIR = Path("/app/cookies")
DEFAULT_TIMEOUT = 15_000  # 15s


class BaseApplicator(ABC):
    portal_key: str  # clave del archivo de sesión, ej: "getonbrd"
    portal_name: str  # nombre legible, ej: "GetOnBrd"
    login_url: str

    def _session_file(self) -> Path:
        return COOKIES_DIR / f"{self.portal_key}_session.json"

    def _load_context(self, browser) -> BrowserContext | None:
        session_file = self._session_file()
        if not session_file.exists():
            return None
        return browser.new_context(
            storage_state=str(session_file),
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

    def _is_session_valid(self, page: Page) -> bool:
        """Navega a la página de inicio y verifica si sigue logueado."""
        try:
            page.goto(self.login_url, wait_until="domcontentloaded", timeout=DEFAULT_TIMEOUT)
            # Si redirige al login → sesión inválida
            return self.login_url not in page.url
        except Exception:
            return False

    def _has_captcha(self, page: Page) -> bool:
        return bool(page.query_selector(
            "iframe[src*='recaptcha'], iframe[src*='hcaptcha'], .g-recaptcha, .h-captcha"
        ))

    def _save_session(self, context: BrowserContext):
        """Actualiza el archivo de sesión con las cookies actuales."""
        session_file = self._session_file()
        context.storage_state(path=str(session_file))

    def apply(self, offer: dict) -> ApplyResult:
        session_file = self._session_file()
        if not session_file.exists():
            return sin_sesion(self.portal_name, offer.get("url", ""))

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = self._load_context(browser)
            if context is None:
                browser.close()
                return sin_sesion(self.portal_name, offer.get("url", ""))

            try:
                result = self._do_apply(context, offer)
                self._save_session(context)
                return result
            except Exception as e:
                print(f"[{self.portal_name}] Error inesperado: {e}")
                return ApplyResult(
                    status="fallido",
                    requiere_humano=True,
                    motivo=f"Error inesperado: {str(e)[:200]}",
                    paso_alcanzado="Proceso de postulación",
                    url_continuar=offer.get("url", ""),
                )
            finally:
                browser.close()

    @abstractmethod
    def _do_apply(self, context: BrowserContext, offer: dict) -> ApplyResult:
        """Implementación específica por portal."""
        ...
