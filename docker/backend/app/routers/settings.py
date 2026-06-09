import json
import os
from fastapi import APIRouter

router = APIRouter(prefix="/api/settings", tags=["settings"])

DATA_DIR = os.getenv("DATA_DIR", "/wunen")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")

DEFAULT_SETTINGS = {
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
