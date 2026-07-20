import json
import os
import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/api/settings", tags=["settings"])

WUNEN_DIR = os.getenv("WUNEN_DIR", "/wunen")
SETTINGS_PATH = os.path.join(WUNEN_DIR, "documentos", "settings.json")
WHATSAPP_URL = os.getenv("WHATSAPP_URL", "http://whatsapp:3001")
SCRAPER_URL = os.getenv("SCRAPER_URL", "http://scraper:8001")

DEFAULT_SETTINGS = {
    "user_name": "",
    "whatsapp_phone": "",
    "notification_email": "",
    "reply_email": "",
}


def _read() -> dict:
    base = DEFAULT_SETTINGS.copy()
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            base.update(json.load(f))
    return base


def _write(data: dict):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@router.get("")
def get_settings():
    return _read()


@router.post("")
def save_settings(data: dict):
    current = _read()
    current.update({k: v for k, v in data.items() if k in DEFAULT_SETTINGS})
    _write(current)
    return {"status": "ok"}


@router.post("/test-whatsapp")
async def test_whatsapp():
    settings = _read()
    phone = settings.get("whatsapp_phone", "").strip()
    if not phone:
        return {"status": "error", "message": "No hay número de teléfono configurado"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # 1) Comprobar primero que el servicio WhatsApp esté vinculado/activo.
            try:
                health = await client.get(f"{WHATSAPP_URL}/health")
                hdata = health.json() if health.status_code == 200 else {}
            except Exception:
                return {
                    "status": "error",
                    "message": "El servicio de WhatsApp no responde. Verifica que el contenedor "
                               "wunen_whatsapp esté corriendo (docker compose up -d whatsapp).",
                }
            if hdata.get("status") != "ok":
                conexion = hdata.get("connection", "desconocido")
                return {
                    "status": "error",
                    "message": f"WhatsApp no está vinculado (estado: {conexion}). Escanea el código QR "
                               "con './configuraciones/vincular-whatsapp.sh' antes de enviar mensajes.",
                }

            # 2) Servicio activo → enviar el mensaje de prueba.
            r = await client.post(
                f"{WHATSAPP_URL}/send",
                json={"to": phone, "message": "Buscapega: mensaje de prueba de notificaciones ✓"},
            )
            if r.status_code == 200:
                return {"status": "ok", "message": f"Mensaje enviado a {phone}"}
            # Intentar extraer el detalle del cuerpo de la respuesta del servicio.
            detail = ""
            try:
                detail = r.json().get("error", "")
            except Exception:
                pass
            if r.status_code == 503:
                return {
                    "status": "error",
                    "message": "WhatsApp no está conectado. Vincula el dispositivo con './configuraciones/vincular-whatsapp.sh'"
                               + (f" (detalle: {detail})" if detail else "") + ".",
                }
            return {
                "status": "error",
                "message": f"WhatsApp respondió con error {r.status_code}"
                           + (f": {detail}" if detail else ""),
            }
    except Exception as e:
        return {"status": "error", "message": f"No se pudo conectar al servicio WhatsApp: {str(e)}"}


@router.post("/test-email")
async def test_email():
    """Valida el correo de postulaciones enviando un correo de prueba.

    Delega en el servicio scraper, que tiene configuradas las credenciales de
    envío (GMAIL_USER/GMAIL_APP_PASSWORD y el webhook de Google Apps Script).
    """
    settings = _read()
    email = settings.get("notification_email", "").strip()
    if not email:
        return {"status": "error", "message": "No hay correo de postulaciones configurado"}
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            r = await client.post(f"{SCRAPER_URL}/test-email", json={"to": email})
            if r.status_code == 200:
                return r.json()
            return {
                "status": "error",
                "message": f"El servicio de envío respondió con error {r.status_code}",
            }
    except Exception as e:
        return {"status": "error", "message": f"No se pudo conectar al servicio de envío: {str(e)}"}
