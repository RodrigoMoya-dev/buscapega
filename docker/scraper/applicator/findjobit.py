"""
Aplicador para FindJobIT.
Envía la postulación por email usando Gmail SMTP.
Notifica por WhatsApp el resultado.
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

from .result import ApplyResult
from .cover_letter import generate as generate_cover_letter

# ── Configuración ─────────────────────────────────────────────────────────────
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
GMAIL_FROM_NAME = os.getenv("GMAIL_FROM_NAME", "Rodrigo Moya")
WHATSAPP_URL = os.getenv("WHATSAPP_URL", "http://whatsapp:3001")
WHATSAPP_PHONE = os.getenv("DEFAULT_PHONE", "56962075019")

# Ruta al CV — montada en el contenedor desde el proyecto
CV_DIR = Path("/wunen")
CV_ES = CV_DIR / "cv_es.pdf"   # CV en español
CV_EN = CV_DIR / "cv_en.pdf"   # CV en inglés
CV_FALLBACK = CV_DIR / "cv.pdf"  # Fallback genérico

# Nombre del candidato para el asunto
APPLICANT_NAME = GMAIL_FROM_NAME  # "Rodrigo Moya"


def _send_whatsapp(message: str):
    """Envía un mensaje de WhatsApp via el servicio Baileys."""
    try:
        httpx.post(
            f"{WHATSAPP_URL}/send",
            json={"message": message},
            timeout=10.0
        )
    except Exception as e:
        print(f"[FindJobIT] No se pudo enviar WhatsApp: {e}")


def _detect_cv_language(description: str) -> str:
    """
    Detecta si el CV debe enviarse en inglés o español
    analizando la descripción del trabajo.
    Retorna 'en' o 'es'.
    """
    desc_lower = description.lower()

    # Señales de que piden inglés
    english_signals = [
        "english", "inglés", "ingles",
        "advanced english", "english required",
        "fluent in english", "english speaking",
    ]
    # Señales de que piden español
    spanish_signals = [
        "español", "spanish", "castellano",
        "hablar español", "hablar castellano",
    ]

    en_count = sum(1 for s in english_signals if s in desc_lower)
    es_count = sum(1 for s in spanish_signals if s in desc_lower)

    # Si piden inglés explícitamente, enviar CV en inglés
    if en_count > es_count:
        return "en"
    # Por defecto: español (mayoría de portales Latam)
    return "es"


def _get_cv_path(language: str) -> Path | None:
    """Retorna la ruta al CV en el idioma indicado."""
    if language == "en" and CV_EN.exists():
        return CV_EN
    if language == "es" and CV_ES.exists():
        return CV_ES
    if CV_FALLBACK.exists():
        return CV_FALLBACK
    # Intentar cualquier PDF en el directorio
    pdfs = list(CV_DIR.glob("*.pdf"))
    if pdfs:
        return pdfs[0]
    return None


def _send_email(
    to_email: str,
    subject: str,
    body_text: str,
    body_html: str,
    cv_path: Path | None,
) -> bool:
    """
    Envía el email via Gmail SMTP con TLS.
    Retorna True si fue exitoso.
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("[FindJobIT] GMAIL_USER o GMAIL_APP_PASSWORD no configurados")
        return False

    msg = MIMEMultipart("mixed")
    msg["From"] = f"{GMAIL_FROM_NAME} <{GMAIL_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    # Parte alternativa (texto + HTML)
    alt_part = MIMEMultipart("alternative")
    alt_part.attach(MIMEText(body_text, "plain", "utf-8"))
    alt_part.attach(MIMEText(body_html, "html", "utf-8"))
    msg.attach(alt_part)

    # Adjuntar CV si existe
    if cv_path and cv_path.exists():
        with open(cv_path, "rb") as f:
            cv_data = f.read()
        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(cv_data)
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition",
            f"attachment; filename={cv_path.name}"
        )
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


def apply(offer: dict) -> ApplyResult:
    """
    Aplica a una oferta de FindJobIT via email.

    offer debe contener:
    - title, company, url, description
    - _apply_email: email de destino (puede ser None)
    - _apply_subject: asunto sugerido (puede ser None)
    """
    title = offer.get("title", "")
    company = offer.get("company", "")
    url = offer.get("url", "")
    description = offer.get("description", "")

    to_email = offer.get("_apply_email") or offer.get("apply_email")
    raw_subject = offer.get("_apply_subject") or offer.get("apply_subject")

    # ── Validar email ─────────────────────────────────────────────────────────
    if not to_email:
        motivo = "No se encontró email de contacto en la oferta"
        print(f"[FindJobIT] {motivo} → {url}")
        _send_whatsapp(
            f"⚠️ *FindJobIT — No se pudo postular*\n"
            f"*Cargo:* {title}\n"
            f"*Empresa:* {company}\n"
            f"*Motivo:* {motivo}\n"
            f"*Link:* {url}"
        )
        return ApplyResult(
            status="fallido",
            requiere_humano=True,
            motivo=motivo,
            paso_alcanzado="Extracción de email",
            url_continuar=url,
        )

    # ── Detectar idioma del CV ────────────────────────────────────────────────
    cv_language = _detect_cv_language(description)
    cv_path = _get_cv_path(cv_language)
    print(f"[FindJobIT] CV en {cv_language.upper()}: {cv_path}")

    # ── Construir asunto ──────────────────────────────────────────────────────
    if raw_subject:
        # Reemplazar [Nombre] o {{Nombre}} si aparece
        subject = re.sub(r"\[Nombre\]|\{\{Nombre\}\}", APPLICANT_NAME, raw_subject, flags=re.IGNORECASE)
        # Si el asunto ya tiene el nombre correcto, mantenerlo
    else:
        subject = f"{APPLICANT_NAME} - Aplicar a vacante {title} - Findjobit"

    # ── Generar carta de presentación ─────────────────────────────────────────
    print(f"[FindJobIT] Generando carta de presentación para '{title}'...")
    cover_letter_text = generate_cover_letter({
        "title": title,
        "company": company,
        "portal": "FindJobIT",
        "description": description,
        "technologies": offer.get("technologies", ""),
    })

    # ── Construir HTML del email ──────────────────────────────────────────────
    body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto; color: #333;">
    <div style="padding: 20px;">
        {cover_letter_text.replace(chr(10), '<br>')}
        <br><br>
        <p style="color: #666; font-size: 12px;">
            <em>Postulación enviada a través de Findjobit — {url}</em>
        </p>
    </div>
</body>
</html>
"""

    # ── Enviar email ──────────────────────────────────────────────────────────
    success = _send_email(
        to_email=to_email,
        subject=subject,
        body_text=cover_letter_text,
        body_html=body_html,
        cv_path=cv_path,
    )

    if success:
        msg = (
            f"✅ *FindJobIT — Postulación enviada*\n"
            f"*Cargo:* {title}\n"
            f"*Empresa:* {company}\n"
            f"*Email enviado a:* {to_email}\n"
            f"*CV:* {'Inglés' if cv_language == 'en' else 'Español'}\n"
            f"*Link:* {url}"
        )
        _send_whatsapp(msg)

        return ApplyResult(
            status="ok",
            requiere_humano=False,
            motivo=f"Email enviado a {to_email}",
            paso_alcanzado="Email enviado",
            url_continuar=url,
        )
    else:
        motivo = "Error al enviar el email via Gmail SMTP"
        _send_whatsapp(
            f"❌ *FindJobIT — Error al postular*\n"
            f"*Cargo:* {title}\n"
            f"*Empresa:* {company}\n"
            f"*Motivo:* {motivo}\n"
            f"*Link:* {url}"
        )
        return ApplyResult(
            status="fallido",
            requiere_humano=True,
            motivo=motivo,
            paso_alcanzado="Envío de email",
            url_continuar=url,
        )
