"""
Scraper para findjobit.com
Busca ofertas de trabajo remotas que incluyan Chile.
Usa Playwright para renderizar el sitio (Next.js/SPA).
"""
import re
import time
from typing import List, Dict
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BASE_URL = "https://www.findjobit.com"
CHILE_JOBS_URL = f"{BASE_URL}/jobs/country/chile"

# Modalidades aceptadas (en findjobit aparece "Remoto")
REMOTE_KEYWORDS = {"remoto", "remote", "remotamente"}


def _clean_text(text: str) -> str:
    """Limpia espacios extra de un texto."""
    return re.sub(r"\s+", " ", text or "").strip()


def _is_remote(text: str) -> bool:
    """Verifica si el texto menciona modalidad remota."""
    return any(k in text.lower() for k in REMOTE_KEYWORDS)


def _scrape_listing_page(page, url: str) -> List[Dict]:
    """Extrae los links de ofertas desde una página de listado."""
    offers_links = []
    try:
        page.goto(url, wait_until="networkidle", timeout=30_000)
        page.wait_for_timeout(2000)  # dar tiempo al JS

        # Buscar todos los links a ofertas individuales
        # Los links tienen el patrón /jobs/{id}
        links = page.eval_on_selector_all(
            "a[href^='/jobs/']",
            "els => els.map(e => ({href: e.getAttribute('href'), text: e.innerText}))"
        )

        seen = set()
        for link in links:
            href = link.get("href", "")
            # Filtrar: /jobs/{id} donde id no es country, role, etc.
            if re.match(r"^/jobs/[a-f0-9]{24}$", href) and href not in seen:
                seen.add(href)
                offers_links.append(BASE_URL + href)

    except PlaywrightTimeout:
        print(f"[FindJobIT] Timeout en {url}")
    except Exception as e:
        print(f"[FindJobIT] Error en listado: {e}")

    return offers_links


def _extract_offer_detail(page, url: str) -> Dict | None:
    """Extrae el detalle completo de una oferta individual."""
    try:
        page.goto(url, wait_until="networkidle", timeout=30_000)
        page.wait_for_timeout(1500)

        # Título del cargo
        title = ""
        title_el = page.query_selector("h1")
        if title_el:
            title = _clean_text(title_el.inner_text())

        # Empresa
        company = ""
        company_el = page.query_selector("h2, [class*='company'], [class*='empresa']")
        if company_el:
            company = _clean_text(company_el.inner_text())

        # Descripción completa (main content)
        description = ""
        desc_el = page.query_selector("main, article, [class*='description'], [class*='descripcion'], [class*='content']")
        if desc_el:
            description = _clean_text(desc_el.inner_text())[:4000]
        else:
            # Fallback: todo el body
            description = _clean_text(page.inner_text("body"))[:4000]

        # Verificar que la oferta sea remota
        page_text_lower = description.lower() + title.lower()
        if not _is_remote(page_text_lower):
            # Permitir incluso si no dice explícitamente remoto
            # (ya filtramos desde country/chile que tiende a ser remoto)
            pass

        # Verificar que Chile esté en los países aceptados
        chile_keywords = {"chile", "🇨🇱"}
        has_chile = any(k in page_text_lower for k in chile_keywords)
        if not has_chile:
            # El URL ya viene de /jobs/country/chile — asumir Chile incluido
            pass

        # Intentar extraer el email de aplicación (aparece en el formulario de apply)
        apply_email = None
        apply_subject = None

        # Buscar botón "Aplicar" y hacer clic para ver el formulario
        apply_btn = page.query_selector(
            "button:has-text('Aplicar'), a:has-text('Aplicar'), "
            "button:has-text('Apply'), a:has-text('Apply')"
        )
        if apply_btn:
            try:
                apply_btn.click()
                page.wait_for_timeout(2000)

                # Buscar campo email
                email_input = page.query_selector(
                    "input[type='email'], input[name*='email'], input[placeholder*='email' i], "
                    "input[placeholder*='correo' i]"
                )
                if email_input:
                    apply_email = email_input.get_attribute("value") or email_input.input_value()

                # Buscar campo asunto
                subject_input = page.query_selector(
                    "input[name*='subject'], input[name*='asunto'], "
                    "input[placeholder*='asunto' i], input[placeholder*='subject' i]"
                )
                if subject_input:
                    apply_subject = subject_input.get_attribute("value") or subject_input.input_value()

                # Si no hay inputs, buscar texto con email en la página
                if not apply_email:
                    # Buscar patrón de email en el DOM visible
                    body_text = page.inner_text("body")
                    email_match = re.search(
                        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b",
                        body_text
                    )
                    if email_match:
                        apply_email = email_match.group(0)

                # Si no hay asunto, buscar texto que parezca el asunto esperado
                if not apply_subject and title:
                    apply_subject = f"Aplicar a vacante {title} - Findjobit"

            except Exception as e:
                print(f"[FindJobIT] No se pudo extraer formulario apply de {url}: {e}")

        if not title:
            print(f"[FindJobIT] Oferta sin título en {url}, omitiendo")
            return None

        return {
            "portal": "FindJobIT",
            "title": title,
            "company": company or "Empresa en FindJobIT",
            "url": url,
            "description": description,
            "salary_raw": None,
            # Metadatos extra para el aplicador
            "_apply_email": apply_email,
            "_apply_subject": apply_subject,
        }

    except PlaywrightTimeout:
        print(f"[FindJobIT] Timeout extrayendo detalle de {url}")
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

        # Recolectar links de múltiples páginas
        offer_urls = []
        for page_num in range(1, 4):  # páginas 1, 2, 3
            url = f"{CHILE_JOBS_URL}?page={page_num}"
            print(f"[FindJobIT] Scrapeando listado página {page_num}...")
            links = _scrape_listing_page(page, url)
            if not links:
                break
            offer_urls.extend(links)
            time.sleep(1)  # pausa entre páginas

        print(f"[FindJobIT] {len(offer_urls)} ofertas encontradas en listados")

        # Extraer detalle de cada oferta
        for offer_url in offer_urls:
            print(f"[FindJobIT] Extrayendo: {offer_url}")
            offer = _extract_offer_detail(page, offer_url)
            if offer:
                all_offers.append(offer)
            time.sleep(1)

        browser.close()

    print(f"[FindJobIT] Total ofertas válidas: {len(all_offers)}")
    return all_offers
