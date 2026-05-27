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
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
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

BASE_URL = "https://www.findjobit.com"
SESSION_FILE = Path("/app/cookies/findjobit_session.json")

# Ruta al CV — montada en el contenedor desde el proyecto
CV_DIR = Path("/wunen")
CV_ES = CV_DIR / "cv_es.pdf"
CV_EN = CV_DIR / "cv_en.pdf"
CV_FALLBACK = CV_DIR / "cv.pdf"

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


def _send_email(to_email: str, subject: str, body_text: str,
                body_html: str, cv_path: Path | None) -> bool:
    """Envía email via Gmail SMTP con TLS."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("[FindJobIT] GMAIL_USER o GMAIL_APP_PASSWORD no configurados")
        return False

    msg = MIMEMultipart("mixed")
    msg["From"] = f"{GMAIL_FROM_NAME} <{GMAIL_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    alt_part = MIMEMultipart("alternative")
    alt_part.attach(MIMEText(body_text, "plain", "utf-8"))
    alt_part.attach(MIMEText(body_html, "html", "utf-8"))
    msg.attach(alt_part)

    if cv_path and cv_path.exists():
        with open(cv_path, "rb") as f:
            cv_data = f.read()
        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(cv_data)
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", f"attachment; filename={cv_path.name}")
        msg.attach(attachment)
        print(f"[FindJobIT] CV adjunto: {cv_path.name}")
    else:
        print("[FindJobIT] ⚠️ No se encontró CV para adjuntar")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        print(f"[FindJobIT] ✅ Email enviado a {to_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[FindJobIT] ❌ Error de autenticación Gmail. Verifica GMAIL_APP_PASSWORD")
        return False
    except Exception as e:
        print(f"[FindJobIT] ❌ Error al enviar email: {e}")
        return False


def _apply_via_form(offer: dict, cover_letter: str, cv_path: Path | None) -> ApplyResult:
    """
    Envía la postulación rellenando el formulario de FindJobIT via Playwright.
    Requiere sesión activa en SESSION_FILE.
    """
    job_id = offer.get("_job_id", "")
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
            page.goto(apply_url, wait_until="domcontentloaded", timeout=25_000)
            page.wait_for_timeout(2000)

            # Verificar que la sesión sea válida
            if "/login" in page.url or "ingresar" in page.url.lower():
                browser.close()
                return ApplyResult(
                    status="fallido", requiere_humano=True,
                    motivo="Sesión de FindJobIT expirada. Ejecutar: python3 setup/setup_session.py findjobit",
                    paso_alcanzado="Verificación de sesión", url_continuar=url,
                )

            print(f"[FindJobIT] Formulario cargado: {page.url}")

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
    print(f"[FindJobIT] CV en {cv_language.upper()}: {cv_path}")

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
            cv_path=cv_path,
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
        result = _apply_via_form(offer, cover_letter, cv_path)

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
