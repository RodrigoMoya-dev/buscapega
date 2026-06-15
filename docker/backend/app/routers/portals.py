import json
import os
import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Offer

router = APIRouter(prefix="/api/portals", tags=["portals"])

COOKIES_DIR = os.getenv("COOKIES_DIR", "/app/cookies")
WUNEN_DIR = os.getenv("WUNEN_DIR", "/wunen")
PORTALES_PATH = os.path.join(WUNEN_DIR, "documentos", "portales.json")

DEFAULT_PORTAL_LIST = [
    {"name": "Tecnoempleo",   "url": "https://www.tecnoempleo.com",   "auto_apply": True,  "market": "España",        "session_key": "tecnoempleo"},
    {"name": "ChileTrabajos", "url": "https://www.chiletrabajos.cl",  "auto_apply": True,  "market": "Chile",         "session_key": "chiletrabajos"},
    {"name": "Chumi-IT",      "url": "https://chumi-it.com",          "auto_apply": True,  "market": "LATAM/España",  "session_key": "chumiit"},
    {"name": "RemoteLatinos", "url": "https://www.remotelatinos.com", "auto_apply": True,  "market": "LATAM/EEUU",    "session_key": "remotelatinos"},
    {"name": "GetOnBrd",      "url": "https://www.getonbrd.com",      "auto_apply": True,  "market": "LATAM/Chile",   "session_key": "getonbrd"},
    {"name": "FindJobIT",     "url": "https://findjobit.com",         "auto_apply": True,  "market": "Internacional", "session_key": "findjobit"},
    {"name": "Torre.ai",      "url": "https://torre.ai",              "auto_apply": False, "market": "LATAM/EEUU",    "session_key": None},
    {"name": "InfoJobs",      "url": "https://www.infojobs.net",      "auto_apply": False, "market": "España",        "session_key": None},
    {"name": "LaraJobs",      "url": "https://larajobs.com",          "auto_apply": False, "market": "Internacional", "session_key": None},
    {"name": "FlexJobs",      "url": "https://www.flexjobs.com",      "auto_apply": False, "market": "Internacional", "session_key": None},
    {"name": "Remotive",      "url": "https://remotive.com",          "auto_apply": False, "market": "Internacional", "session_key": None},
    {"name": "RemoteOK",      "url": "https://remoteok.com",          "auto_apply": False, "market": "Internacional", "session_key": None},
]


def _load_portal_list() -> list:
    if os.path.exists(PORTALES_PATH):
        try:
            with open(PORTALES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_PORTAL_LIST


def _cookie_active(session_key: str | None) -> bool:
    if not session_key:
        return False
    path = os.path.join(COOKIES_DIR, f"{session_key}_session.json")
    return os.path.exists(path)


@router.get("")
def list_portals(db: Session = Depends(get_db)):
    portal_list = _load_portal_list()

    sent_statuses = ["ENVIADA", "POSTULADA"]
    counts_rows = (
        db.query(Offer.portal, func.count(Offer.id).label("count"))
        .filter(Offer.status.in_(sent_statuses))
        .group_by(Offer.portal)
        .all()
    )
    counts_map: dict[str, int] = {}
    for r in counts_rows:
        key = r.portal.lower().replace(" ", "").replace("-", "").replace(".", "")
        counts_map[key] = r.count

    result = []
    for p in portal_list:
        key = p["name"].lower().replace(" ", "").replace("-", "").replace(".", "")
        cookie_active = _cookie_active(p.get("session_key"))
        portal_data = {k: v for k, v in p.items() if k != "session_key"}
        result.append({
            **portal_data,
            "session_active": cookie_active,
            "applications_count": counts_map.get(key, 0),
        })
    return result


KNOWN_PORTALS_SCRAPING = {
    "findjobit.com": {"allows_scraping": True, "has_google_auth": True},
    "getonbrd.com": {"allows_scraping": True, "has_google_auth": True},
    "tecnoempleo.com": {"allows_scraping": True, "has_google_auth": False},
    "chiletrabajos.cl": {"allows_scraping": True, "has_google_auth": False},
    "chumi-it.com": {"allows_scraping": True, "has_google_auth": False},
    "remotelatinos.com": {"allows_scraping": True, "has_google_auth": True},
}


def _normalize_url(url: str) -> str:
    url = url.strip()
    if url and not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url


def _match_known_portal(url: str) -> dict | None:
    url_lower = url.lower()
    for domain, props in KNOWN_PORTALS_SCRAPING.items():
        if domain in url_lower:
            return props
    return None


@router.post("/validate")
async def validate_portal(body: dict):
    raw_url: str = body.get("url", "")
    if not raw_url:
        return {"error": "url requerida"}

    url = _normalize_url(raw_url)

    result = {
        "url": url,
        "allows_scraping": False,
        "has_google_auth": False,
        "notes": [],
        "already_configured": False,
    }

    if url != raw_url.strip():
        result["notes"].append("URL normalizada: se agregó https:// automáticamente")

    portal_list = _load_portal_list()
    for p in portal_list:
        p_domain = p["url"].lower().replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
        q_domain = url.lower().replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
        if p_domain and (q_domain.startswith(p_domain) or p_domain.startswith(q_domain.split("/")[0])):
            result["already_configured"] = True
            result["notes"].append(f"Este sitio ya está registrado en Wunen como '{p['name']}'")
            break

    known = _match_known_portal(url)
    if known:
        result["allows_scraping"] = known["allows_scraping"]
        result["has_google_auth"] = known["has_google_auth"]
        result["notes"].append("Portal conocido — datos obtenidos del registro interno de Wunen")
        result["automatable"] = result["allows_scraping"]
        return result

    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            robots_url = url.rstrip("/") + "/robots.txt"
            try:
                r = await client.get(robots_url)
                robots_text = r.text.lower() if r.status_code == 200 else ""
                if "disallow: /" in robots_text and "user-agent: *" in robots_text:
                    result["allows_scraping"] = False
                    result["notes"].append("robots.txt bloquea scraping general")
                else:
                    result["allows_scraping"] = True
                    result["notes"].append("robots.txt no bloquea scraping general")
            except Exception:
                result["allows_scraping"] = True
                result["notes"].append("No se encontró robots.txt — se asume permisivo")

            try:
                r = await client.get(url)
                page = r.text.lower()
                google_indicators = [
                    "accounts.google.com",
                    "google-signin",
                    "g_id_signin",
                    "gsi/client",
                    "oauth2/auth",
                    "login with google",
                    "sign in with google",
                    "iniciar sesión con google",
                    "continuar con google",
                ]
                for ind in google_indicators:
                    if ind in page:
                        result["has_google_auth"] = True
                        result["notes"].append(f"Google Auth detectado: '{ind}'")
                        break
                if not result["has_google_auth"]:
                    result["notes"].append("No se detectó autenticación Google en la página principal (puede requerir JS para renderizarla)")
            except Exception as e:
                result["notes"].append(f"Error al acceder a la URL: {str(e)}")
    except Exception as e:
        result["notes"].append(f"Error general: {str(e)}")

    result["automatable"] = result["allows_scraping"]
    return result
