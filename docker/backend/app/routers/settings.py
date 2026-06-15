import json
import os
import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/api/settings", tags=["settings"])

WUNEN_DIR = os.getenv("WUNEN_DIR", "/wunen")
SETTINGS_PATH = os.path.join(WUNEN_DIR, "documentos", "settings.json")
WHATSAPP_URL = os.getenv("WHATSAPP_URL", "http://whatsapp:3001")

DEFAULT_SETTINGS = {
    "user_name": "",
    "whatsapp_phone": "",
    "notification_email": "",
    "reply_email": "",
}


def _read() -> dict:
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()


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
            r = await client.post(
                f"{WHATSAPP_URL}/send",
                json={"phone": phone, "message": "Wunen: mensaje de prueba de notificaciones ✓"},
            )
            if r.status_code == 200:
                return {"status": "ok", "message": f"Mensaje enviado a {phone}"}
            return {"status": "error", "message": f"WhatsApp respondió con error {r.status_code}"}
    except Exception as e:
        return {"status": "error", "message": f"No se pudo conectar al servicio WhatsApp: {str(e)}"}
