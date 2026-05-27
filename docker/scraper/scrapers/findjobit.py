"""
Scraper para findjobit.com
Busca ofertas de trabajo remotas que incluyan Chile.
Usa Playwright para renderizar el sitio (Next.js/SPA).

Sesión: si existe /app/cookies/findjobit_session.json (capturada con setup_session.py),
se usa para autenticar y acceder al formulario de postulación completo.
"""
import re
import time
from pathlib import Path
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BASE_URL = "https://www.findjobit.com"
CHILE_JOBS_URL = f"{BASE_URL}/jobs/country/chile"
SESSION_FILE = Path("/app/cookies/findjobit_session.json")

# Selectores de título en orden de preferencia
TITLE_SELECTORS = ["h1", "h2", "h3", "h4", "h5", "[class*='title']", "[class*='titulo']"]


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _extract_emails(text: str) -> List[str]:
    """Extrae emails del texto de una página."""
    return re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", text)


def _scrape_listing_page(page, url: str, seen_urls: set) -> List[str]:
    """Extrae links únicos de ofertas desde una página de listado."""
    new_links = []
    try:
        page.goto(url, wait_until="networkidle", timeout=30_000)
        page.wait_for_timeout(2000)

        links = page.eval_on_selector_all(
            "a[href^='/jobs/']",
            "els => els.map(e => e.getAttribute('href'))"
        )

        for href in links:
            if re.match(r"^/jobs/[a-f0-9]{24}$", href):
                full_url = BASE_URL + href
                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    new_links.append(full_url)

    except PlaywrightTimeout:
        print(f"[FindJobIT] Timeout en listado {url}")
    except Exception as e:
        print(f"[FindJobIT] Error en listado: {e}")

    return new_links


def _has_session() -> bool:
    """Verifica si existe un archivo de sesión válido para FindJobIT."""
    return SESSION_FILE.exists() and SESSION_FILE.stat().st_size > 100


def _get_apply_info(context_factory, job_id: str) -> tuple[Optional[str], Optional[str], bool]:
    """
    Intenta extraer el email y asunto de la página de aplicación.
    Usa sesión autenticada si está disponible.

    Retorna (email, asunto, form_accessible).
    - email: email del empleador si está expuesto en el formulario
    - asunto: asunto sugerido si aparece en el formulario
    - form_accessible: True si el formulario está accesible (con sesión), False si requiere login
    """
    apply_url = f"{BASE_URL}/job-seekers/job/apply/{job_id}"

    # Crear contexto con sesión si está disponible
    if _has_session():
        try:
            ctx = context_factory(storage_state=str(SESSION_FILE))
            page = ctx.new_page()
        except Exception:
            return None, None, False
    else:
        # Usar la página anónima existente (fallback)
        return None, None, False

    try:
        page.goto(apply_url, wait_until="domcontentloaded", timeout=20_000)
        page.wait_for_timeout(1500)

        # Si redirige al login, la sesión expiró
        if "/login" in page.url or "ingresar" in page.url.lower():
            print("[FindJobIT] ⚠️  Sesión de FindJobIT expirada — capturar de nuevo con setup_session.py findjobit")
            page.close(); ctx.close()
            return None, None, False

        body_text = page.inner_text("body")
        emails = _extract_emails(body_text)

        # Buscar email del empleador en campos del formulario
        email_val = None
        for sel in ["input[type='email']", "input[name*='email']", "input[placeholder*='email' i]",
                    "input[name*='to']", "input[name*='recipient']"]:
            el = page.query_selector(sel)
            if el:
                val = el.get_attribute("value") or ""
                try:
                    val = val or el.input_value()
                except Exception:
                    pass
                if val and "@" in val:
                    email_val = val
                    break

        if not email_val and emails:
            email_val = emails[0]

        # Buscar asunto sugerido
        subject_val = None
        for sel in ["input[name*='subject']", "input[name*='asunto']",
                    "input[placeholder*='asunto' i]", "input[placeholder*='subject' i]"]:
            el = page.query_selector(sel)
            if el:
                val = el.get_attribute("value") or ""
                try:
                    val = val or el.input_value()
                except Exception:
                    pass
                if val:
                    subject_val = val
                    break

        page.close()
        ctx.close()
        return email_val, subject_val, True

    except Exception as e:
        print(f"[FindJobIT] Error extrayendo apply info: {e}")
        try:
            page.close(); ctx.close()
        except Exception:
            pass
        return None, None, False


def _extract_offer_detail(page, url: str) -> Optional[Dict]:
    """Extrae el detalle completo de una oferta individual."""
    try:
        page.goto(url, wait_until="networkidle", timeout=30_000)
        page.wait_for_timeout(2000)

        # ── Título: findjobit usa h4 ──────────────────────────────────────
        title = ""
        for sel in TITLE_SELECTORS:
            el = page.query_selector(sel)
            if el:
                t = _clean(el.inner_text())
                # Ignorar títulos muy cortos o de navegación
                if len(t) > 5 and not any(x in t.lower() for x in ["menú", "menu", "inicio", "home"]):
                    title = t
                    break

        if not title:
            # Último recurso: primera línea con contenido razonable
            body = _clean(page.inner_text("body"))
            for line in body.split("\n"):
                line = line.strip()
                if 8 < len(line) < 120:
                    title = line
                    break

        if not title:
            print(f"[FindJobIT] Sin título en {url}")
            return None

        # ── Empresa ───────────────────────────────────────────────────────
        company = ""
        body_text = page.inner_text("body")

        # findjobit muestra "Empresa: NombreEmpresa" en el detalle
        m = re.search(r"Empresa[:\s]+([^\n]{2,60})", body_text, re.IGNORECASE)
        if m:
            company = _clean(m.group(1))
        else:
            # Buscar h4 o h5 que siga al título
            headings = page.query_selector_all("h4, h5, h6")
            if len(headings) > 1:
                company = _clean(headings[1].inner_text())

        # ── Descripción ───────────────────────────────────────────────────
        description = _clean(body_text)[:4000]

        # ── Job ID ────────────────────────────────────────────────────────
        job_id = url.split("/")[-1]

        # ── Email de aplicación (requiere sesión autenticada) ─────────────
        # _get_apply_info crea su propio contexto con cookies de sesión
        apply_email = None
        apply_subject = None
        form_accessible = False

        # Intentar con sesión guardada
        if _has_session():
            context_factory = page.context.browser.new_context
            apply_email, apply_subject, form_accessible = _get_apply_info(context_factory, job_id)

        # Fallback: buscar email en el cuerpo del aviso (raro, pero por si acaso)
        if not apply_email:
            emails_in_body = _extract_emails(description)
            if emails_in_body:
                apply_email = emails_in_body[0]

        session_status = "con sesión" if _has_session() else "sin sesión"
        print(f"[FindJobIT] ✓ '{title}' — {company} | email: {apply_email or 'no encontrado'} ({session_status})")

        return {
            "portal": "FindJobIT",
            "title": title,
            "company": company or "Empresa en FindJobIT",
            "url": url,
            "description": description,
            "salary_raw": None,
            "_apply_email": apply_email,
            "_apply_subject": apply_subject,
            "_job_id": job_id,
            "_form_accessible": form_accessible,   # True si la sesión es válida y el form cargó
        }

    except PlaywrightTimeout:
        print(f"[FindJobIT] Timeout en {url}")
        return None
    except Exception as e:
        print(f"[FindJobIT] Error extrayendo {url}: {e}")
        return None


def fetch_offers() -> List[Dict]:
    """
    Scraper principal de FindJobIT.
    Retorna lista de ofertas remotas que incluyen Chile.
    """
    all_offers = []
    seen_urls: set = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        # Recolectar links únicos de múltiples páginas
        offer_urls = []
        for page_num in range(1, 4):
            url = f"{CHILE_JOBS_URL}?page={page_num}"
            print(f"[FindJobIT] Listado página {page_num}...")
            new = _scrape_listing_page(page, url, seen_urls)
            if not new:
                print(f"[FindJobIT] Página {page_num} sin ofertas nuevas, deteniendo")
                break
            offer_urls.extend(new)
            print(f"[FindJobIT] +{len(new)} nuevas (total: {len(offer_urls)})")
            time.sleep(1)

        print(f"[FindJobIT] {len(offer_urls)} ofertas únicas a procesar")

        for offer_url in offer_urls:
            offer = _extract_offer_detail(page, offer_url)
            if offer:
                all_offers.append(offer)
            time.sleep(1)

        browser.close()

    print(f"[FindJobIT] Total válidas: {len(all_offers)}")
    return all_offers
