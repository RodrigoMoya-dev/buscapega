"""
Aplicador para FindJobIT.

Estrategia de postulación (en orden de preferencia):
1. Email directo via Gmail SMTP — cuando el formulario expone el email del empleador
2. Formulario Playwright — cuando hay sesión activa pero no hay email directo
3. Fallo con aviso WhatsApp — cuando no hay sesión ni email

La sesión se captura con: python3 setup/setup_session.py findjobit
"""
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from .result import ApplyResult
from .cover_letter import generate as generate_cover_letter

# ── Configuración ─────────────────────────────────────────────────────────────
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
GMAIL_FROM_NAME = os.getenv("GMAIL_FROM_NAME", "Rodrigo Moya")
WHATSAPP_URL = os.getenv("WHATSAPP_URL", "http://whatsapp:3001")
# Google Apps Script webhook para enviar emails vía Gmail API (evita bloqueo de SMTP)
GAS_WEBHOOK_URL = os.getenv(
    "GAS_WEBHOOK_URL",
    "https://script.google.com/macros/s/AKfycbzHCRUehm8BUj8_BpVi_ikdeB0xnXbJhKVhClVxjgfwc4jYj-3gzAYiOi-OgqK2DcLwfw/exec"
)

BASE_URL = "https://www.findjobit.com"
SESSION_FILE = Path("/app/cookies/findjobit_session.json")

# Ruta al CV — montada en el contenedor desde el proyecto (usado para formularios con upload)
CV_DIR = Path("/wunen")
CV_ES = CV_DIR / "cv_es.pdf"
CV_EN = CV_DIR / "cv_en.pdf"
CV_FALLBACK = CV_DIR / "cv.pdf"

# URLs públicas del CV (se incluyen como link en emails en lugar de adjuntar el archivo)
CV_URL_ES = "https://moyadev.cl/cv/CV_Rodrigo_Moya_ATS_2026_IA.pdf"
CV_URL_EN = "https://moyadev.cl/cv/CV_Rodrigo_Moya_ATS_2026_EN.pdf"

APPLICANT_NAME = GMAIL_FROM_NAME


def _send_whatsapp(message: str):
    try:
        httpx.post(f"{WHATSAPP_URL}/send", json={"message": message}, timeout=10.0)
    except Exception as e:
        print(f"[FindJobIT] No se pudo enviar WhatsApp: {e}")


def _detect_cv_language(description: str) -> str:
    desc_lower = description.lower()
    english_signals = ["english", "inglés", "ingles", "advanced english",
                       "english required", "fluent in english", "english speaking"]
    spanish_signals = ["español", "spanish", "castellano"]
    en_count = sum(1 for s in english_signals if s in desc_lower)
    es_count = sum(1 for s in spanish_signals if s in desc_lower)
    return "en" if en_count > es_count else "es"


def _get_cv_path(language: str) -> Path | None:
    if language == "en" and CV_EN.exists():
        return CV_EN
    if language == "es" and CV_ES.exists():
        return CV_ES
    if CV_FALLBACK.exists():
        return CV_FALLBACK
    pdfs = list(CV_DIR.glob("*.pdf"))
    return pdfs[0] if pdfs else None


def _get_cv_url(language: str) -> str:
    return CV_URL_EN if language == "en" else CV_URL_ES


def _send_email(to_email: str, subject: str, body_text: str,
                body_html: str, cv_url: str | None) -> bool:
    """
    Envía email usando Google Apps Script webhook (HTTPS port 443).
    Fallback: Gmail SMTP si el webhook falla.
    El CV se incluye como link en el cuerpo del email.
    """
    cv_link_text = f"\n\n📎 CV / Currículum: {cv_url}" if cv_url else ""
    cv_link_html = (
        f'<p style="margin-top:16px">📎 <a href="{cv_url}" target="_blank">'
        f"Ver CV / Currículum Vitae</a></p>"
    ) if cv_url else ""

    # ── Método 1: Google Apps Script webhook (evita bloqueo de SMTP) ──────────
    if GAS_WEBHOOK_URL:
        try:
            import json as _json
            payload = _json.dumps({
                "to": to_email,
                "subject": subject,
                "body": body_text + cv_link_text,
            })
            # IMPORTANTE: No enviar Content-Type: application/json (GAS lo rechaza con 405)
            response = httpx.post(
                GAS_WEBHOOK_URL,
                content=payload,
                timeout=30.0,
                follow_redirects=True,
            )
            if response.status_code in (200, 302):
                print(f"[FindJobIT] ✅ Email enviado via GAS webhook a {to_email}")
                return True
            else:
                print(f"[FindJobIT] ⚠️ GAS webhook respondió {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"[FindJobIT] ⚠️ GAS webhook falló: {e} — intentando SMTP")

    # ── Método 2: Gmail SMTP (puede estar bloqueado según proveedor) ──────────
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("[FindJobIT] GMAIL_USER o GMAIL_APP_PASSWORD no configurados")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{GMAIL_FROM_NAME} <{GMAIL_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text + cv_link_text, "plain", "utf-8"))
    msg.attach(MIMEText(body_html + cv_link_html, "html", "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        print(f"[FindJobIT] ✅ Email enviado via SMTP a {to_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[FindJobIT] ❌ Error de autenticación Gmail. Verifica GMAIL_APP_PASSWORD")
        return False
    except Exception as e:
        print(f"[FindJobIT] ❌ Error al enviar email: {e}")
        return False


def _apply_via_form(offer: dict, cover_letter: str, cv_path: Path | None, cv_url: str | None = None) -> ApplyResult:
    """
    Envía la postulación rellenando el formulario de FindJobIT via Playwright.
    Requiere sesión activa en SESSION_FILE.
    """
    job_id = offer.get("_job_id", "")
    if not job_id:
        # Extraer desde la URL de la oferta: https://www.findjobit.com/jobs/{job_id}
        url_parts = offer.get("url", "").rstrip("/").split("/")
        job_id = url_parts[-1] if url_parts else ""
        if job_id:
            print(f"[FindJobIT] job_id extraído de URL: {job_id}")
    apply_url = f"{BASE_URL}/job-seekers/job/apply/{job_id}"
    url = offer.get("url", apply_url)
    title = offer.get("title", "")
    company = offer.get("company", "")

    if not SESSION_FILE.exists():
        return ApplyResult(
            status="fallido", requiere_humano=True,
            motivo="Sin sesión de FindJobIT. Ejecutar: python3 setup/setup_session.py findjobit",
            paso_alcanzado="Carga de sesión", url_continuar=url,
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            storage_state=str(SESSION_FILE),
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        try:
            # 1. Navegar al formulario de postulación
            # Usar networkidle para esperar que React/Next.js termine de hidratar
            page.goto(apply_url, wait_until="load", timeout=30_000)
            try:
                page.wait_for_load_state("networkidle", timeout=10_000)
            except Exception:
                pass  # networkidle puede no llegar; continuar igual
            page.wait_for_timeout(3000)

            # Verificar que la sesión sea válida
            # FindJobIT puede redirigir a /login, /auth/signin, /auth/login, etc.
            current_url = page.url.lower()
            print(f"[FindJobIT] URL tras navegar al formulario: {page.url}")
            if any(kw in current_url for kw in ["/login", "ingresar", "/auth/", "/signin"]):
                browser.close()
                return ApplyResult(
                    status="fallido", requiere_humano=True,
                    motivo=f"Sesión de FindJobIT expirada (redirigido a {page.url}). Ejecutar: python3 setup/setup_session.py findjobit",
                    paso_alcanzado="Verificación de sesión", url_continuar=url,
                )

            print(f"[FindJobIT] Formulario cargado: {page.url}")

            # Esperar a que React hidrate y aparezcan elementos interactivos
            try:
                page.wait_for_selector(
                    "button, textarea, input, [role='button'], form, a[href]",
                    timeout=15_000
                )
                print("[FindJobIT] Elementos interactivos detectados")
                page.wait_for_timeout(1000)  # pequeño buffer extra
            except Exception:
                print("[FindJobIT] ⚠️ Timeout esperando React hydration — continuando igual")

            # Debug: imprimir elementos y texto visible
            try:
                page_text = page.inner_text("body")[:600].replace("\n", " ").strip()
                print(f"[FindJobIT] Texto visible en página: {page_text}")
            except Exception as de:
                print(f"[FindJobIT] Debug error: {de}")

            # Detectar tipo de aplicación según contenido de la página
            try:
                page_body = page.inner_text("body")
                page_body_lower = page_body.lower()

                # ── Tipo 1: vacante externa ────────────────────────────────────
                if ("sitio web externo" in page_body_lower
                        or "web externa" in page_body_lower
                        or "external" in page_body_lower):
                    external_url = apply_url
                    ext_selectors = [
                        "a[target='_blank']",
                        "a[rel='noopener']",
                        "a[href]:has-text('APLICAR')",
                        "a[href]:has-text('Apply')",
                    ]
                    for ext_sel in ext_selectors:
                        el = page.query_selector(ext_sel)
                        if el:
                            href = el.get_attribute("href") or ""
                            if href and href.startswith("http") and "findjobit" not in href:
                                external_url = href
                                print(f"[FindJobIT] URL externa detectada: {external_url}")
                                break
                    browser.close()
                    return ApplyResult(
                        status="parcial", requiere_humano=True,
                        motivo="La vacante requiere postular en sitio web externo",
                        paso_alcanzado="Detección de tipo de aplicación",
                        url_continuar=external_url,
                    )

                # ── Tipo 2: vacante por email ──────────────────────────────────
                if ("enviando tu cv por email" in page_body_lower
                        or "por email" in page_body_lower
                        or "send your cv" in page_body_lower):
                    # Extraer email del formulario (puede estar en input o en texto)
                    email_found = None
                    subject_found = None
                    # Intentar inputs primero
                    for sel in ["input[type='email']", "input[name*='email']",
                                "input[placeholder*='email' i]", "input[value*='@']"]:
                        el = page.query_selector(sel)
                        if el:
                            val = el.get_attribute("value") or ""
                            try:
                                val = val or el.input_value()
                            except Exception:
                                pass
                            if val and "@" in val:
                                email_found = val.strip()
                                break
                    # Fallback: regex en el cuerpo de la página
                    if not email_found:
                        import re as _re
                        emails = _re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", page_body)
                        email_found = emails[0] if emails else None
                    # Intentar asunto
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
                                subject_found = val.strip()
                                break
                    browser.close()

                    if email_found:
                        print(f"[FindJobIT] Aplicación por email detectada: {email_found}")
                        # Enviar email con carta de presentación y link al CV
                        import re as _re
                        subj = subject_found or f"{APPLICANT_NAME} - Aplicar a vacante {title} - Findjobit"
                        subj = _re.sub(r"\[Nombre\]|\{\{Nombre\}\}", APPLICANT_NAME, subj, flags=_re.IGNORECASE)
                        body_html = f"""<html><body style="font-family:Arial,sans-serif;max-width:650px;color:#333;">
<div style="padding:20px;">{cover_letter.replace(chr(10),'<br>')}<br><br>
<p style="color:#666;font-size:12px;"><em>Postulación enviada a través de Findjobit — {url}</em></p>
</div></body></html>"""
                        ok = _send_email(email_found, subj, cover_letter, body_html, cv_url)
                        if ok:
                            return ApplyResult(
                                status="ok", requiere_humano=False,
                                motivo=f"Email enviado a {email_found}",
                                paso_alcanzado="Email enviado", url_continuar=url,
                            )
                        else:
                            return ApplyResult(
                                status="fallido", requiere_humano=True,
                                motivo=f"Error al enviar email a {email_found}",
                                paso_alcanzado="Envío de email", url_continuar=url,
                            )
                    else:
                        print("[FindJobIT] ⚠️ Email no encontrado en formulario email-type")
                        return ApplyResult(
                            status="parcial", requiere_humano=True,
                            motivo="Vacante por email pero no se pudo extraer dirección",
                            paso_alcanzado="Extracción de email", url_continuar=apply_url,
                        )
            except Exception as de:
                print(f"[FindJobIT] Error detectando tipo de aplicación: {de}")

            # 2. Buscar textarea de mensaje/carta
            message_selectors = [
                "textarea[name*='message']",
                "textarea[name*='mensaje']",
                "textarea[name*='cover']",
                "textarea[name*='letter']",
                "textarea[placeholder*='mensaje' i]",
                "textarea[placeholder*='message' i]",
                "textarea[placeholder*='carta' i]",
                "textarea",
            ]
            message_filled = False
            for sel in message_selectors:
                el = page.query_selector(sel)
                if el:
                    el.fill(cover_letter)
                    message_filled = True
                    print(f"[FindJobIT] Mensaje rellenado en: {sel}")
                    break

            if not message_filled:
                print("[FindJobIT] ⚠️ No se encontró campo de mensaje")

            # 3. Adjuntar CV si hay input de archivo
            if cv_path and cv_path.exists():
                file_inputs = page.query_selector_all("input[type='file']")
                for fi in file_inputs:
                    accept = fi.get_attribute("accept") or ""
                    if "pdf" in accept.lower() or accept == "" or "application" in accept.lower():
                        fi.set_input_files(str(cv_path))
                        print(f"[FindJobIT] CV subido: {cv_path.name}")
                        page.wait_for_timeout(1000)
                        break

            # 4. Buscar y hacer click en botón de enviar
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Postular')",
                "button:has-text('Enviar')",
                "button:has-text('Apply')",
                "button:has-text('Submit')",
                "[data-cy*='submit']",
            ]
            submitted = False
            for sel in submit_selectors:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    el.click()
                    page.wait_for_timeout(3000)
                    submitted = True
                    print(f"[FindJobIT] Botón submit clickeado: {sel}")
                    break

            if not submitted:
                browser.close()
                return ApplyResult(
                    status="parcial", requiere_humano=True,
                    motivo="No se encontró botón de envío en el formulario",
                    paso_alcanzado="Búsqueda de botón submit", url_continuar=apply_url,
                )

            # 5. Verificar éxito (redirección o mensaje de confirmación)
            page.wait_for_timeout(2000)
            current_url = page.url
            body_text = page.inner_text("body")

            success_signals = [
                "postulación enviada", "postulacion enviada",
                "application sent", "successfully applied",
                "tu postulación", "gracias por postular",
                "thank you", "enviada correctamente",
            ]
            confirmed = any(s in body_text.lower() for s in success_signals)

            # También considerar éxito si redirigió fuera del formulario
            if not confirmed and apply_url not in current_url and "/apply/" not in current_url:
                confirmed = True

            # Guardar cookies actualizadas
            context.storage_state(path=str(SESSION_FILE))
            browser.close()

            if confirmed:
                print(f"[FindJobIT] ✅ Postulación vía formulario enviada para '{title}'")
                return ApplyResult(
                    status="ok", requiere_humano=False,
                    motivo="Formulario de FindJobIT enviado exitosamente",
                    paso_alcanzado="Formulario enviado", url_continuar=url,
                )
            else:
                print(f"[FindJobIT] ⚠️ No se pudo confirmar el envío para '{title}'")
                return ApplyResult(
                    status="parcial", requiere_humano=True,
                    motivo="Formulario enviado pero no se confirmó el éxito",
                    paso_alcanzado="Envío de formulario", url_continuar=apply_url,
                )

        except PlaywrightTimeout:
            browser.close()
            return ApplyResult(
                status="fallido", requiere_humano=True,
                motivo="Timeout al cargar el formulario de postulación",
                paso_alcanzado="Carga del formulario", url_continuar=apply_url,
            )
        except Exception as e:
            print(f"[FindJobIT] Error en formulario: {e}")
            browser.close()
            return ApplyResult(
                status="fallido", requiere_humano=True,
                motivo=f"Error inesperado en formulario: {str(e)[:200]}",
                paso_alcanzado="Envío de formulario", url_continuar=apply_url,
            )


def apply(offer: dict) -> ApplyResult:
    """
    Aplica a una oferta de FindJobIT.

    Estrategia:
    - Si hay email directo → envío por Gmail SMTP
    - Si hay sesión activa (form_accessible) → formulario Playwright
    - Si ninguno → fallo con aviso WhatsApp
    """
    title = offer.get("title", "")
    company = offer.get("company", "")
    url = offer.get("url", "")
    description = offer.get("description", "")

    to_email = offer.get("_apply_email") or offer.get("apply_email")
    raw_subject = offer.get("_apply_subject") or offer.get("apply_subject")
    form_accessible = offer.get("_form_accessible", False)

    # ── Generar carta de presentación ─────────────────────────────────────────
    print(f"[FindJobIT] Generando carta de presentación para '{title}'...")
    cover_letter = generate_cover_letter({
        "title": title,
        "company": company,
        "portal": "FindJobIT",
        "description": description,
        "technologies": offer.get("technologies", ""),
    })

    cv_language = _detect_cv_language(description)
    cv_path = _get_cv_path(cv_language)
    cv_url = _get_cv_url(cv_language)
    print(f"[FindJobIT] CV en {cv_language.upper()}: {cv_url}")

    # ── Modo 1: Email directo ─────────────────────────────────────────────────
    if to_email:
        if raw_subject:
            subject = re.sub(r"\[Nombre\]|\{\{Nombre\}\}", APPLICANT_NAME,
                             raw_subject, flags=re.IGNORECASE)
        else:
            subject = f"{APPLICANT_NAME} - Aplicar a vacante {title} - Findjobit"

        body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto; color: #333;">
    <div style="padding: 20px;">
        {cover_letter.replace(chr(10), '<br>')}
        <br><br>
        <p style="color: #666; font-size: 12px;">
            <em>Postulación enviada a través de Findjobit — {url}</em>
        </p>
    </div>
</body>
</html>"""

        success = _send_email(
            to_email=to_email,
            subject=subject,
            body_text=cover_letter,
            body_html=body_html,
            cv_url=cv_url,
        )

        if success:
            _send_whatsapp(
                f"✅ *FindJobIT — Postulación enviada*\n"
                f"*Cargo:* {title}\n"
                f"*Empresa:* {company}\n"
                f"*Email enviado a:* {to_email}\n"
                f"*CV:* {'Inglés' if cv_language == 'en' else 'Español'}\n"
                f"*Link:* {url}"
            )
            return ApplyResult(
                status="ok", requiere_humano=False,
                motivo=f"Email enviado a {to_email}",
                paso_alcanzado="Email enviado", url_continuar=url,
            )
        else:
            # Si falla el email, intentar por formulario si hay sesión
            if not form_accessible:
                motivo = "Error al enviar email y sin sesión de FindJobIT"
                _send_whatsapp(
                    f"❌ *FindJobIT — Error al postular*\n"
                    f"*Cargo:* {title}\n"
                    f"*Empresa:* {company}\n"
                    f"*Motivo:* {motivo}\n"
                    f"*Link:* {url}"
                )
                return ApplyResult(
                    status="fallido", requiere_humano=True,
                    motivo=motivo, paso_alcanzado="Envío de email", url_continuar=url,
                )
            print("[FindJobIT] Email falló, intentando por formulario...")

    # ── Modo 2: Formulario Playwright ─────────────────────────────────────────
    if form_accessible or (not to_email and SESSION_FILE.exists()):
        print(f"[FindJobIT] Aplicando vía formulario Playwright para '{title}'...")
        result = _apply_via_form(offer, cover_letter, cv_path, cv_url)

        if result.status == "ok":
            _send_whatsapp(
                f"✅ *FindJobIT — Postulación enviada (formulario)*\n"
                f"*Cargo:* {title}\n"
                f"*Empresa:* {company}\n"
                f"*CV:* {'Inglés' if cv_language == 'en' else 'Español'}\n"
                f"*Link:* {url}"
            )
        elif result.status == "parcial":
            _send_whatsapp(
                f"⚠️ *FindJobIT — Postulación parcial*\n"
                f"*Cargo:* {title}\n"
                f"*Empresa:* {company}\n"
                f"*Motivo:* {result.motivo}\n"
                f"*Link:* {result.url_continuar}"
            )
        else:
            _send_whatsapp(
                f"❌ *FindJobIT — Error al postular*\n"
                f"*Cargo:* {title}\n"
                f"*Empresa:* {company}\n"
                f"*Motivo:* {result.motivo}\n"
                f"*Link:* {url}"
            )
        return result

    # ── Sin email ni sesión ───────────────────────────────────────────────────
    motivo = "Sin email de contacto y sin sesión de FindJobIT"
    print(f"[FindJobIT] {motivo} → {url}")
    _send_whatsapp(
        f"⚠️ *FindJobIT — Requiere revisión manual*\n"
        f"*Cargo:* {title}\n"
        f"*Empresa:* {company}\n"
        f"*Motivo:* Sin sesión activa. Ejecutar: python3 setup/setup_session.py findjobit\n"
        f"*Link:* {url}"
    )
    return ApplyResult(
        status="fallido", requiere_humano=True,
        motivo=motivo, paso_alcanzado="Selección de estrategia", url_continuar=url,
    )
