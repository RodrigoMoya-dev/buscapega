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

PORTAL_LIST = [
    {"name": "Tecnoempleo", "url": "https://www.tecnoempleo.com", "auto_apply": True, "market": "España", "session_key": "tecnoempleo"},
    {"name": "ChileTrabajos", "url": "https://www.chiletrabajos.cl", "auto_apply": True, "market": "Chile", "session_key": "chiletrabajos"},
    {"name": "Chumi-IT", "url": "https://chumi-it.com", "auto_apply": True, "market": "LATAM/España", "session_key": "chumiit"},
    {"name": "RemoteLatinos", "url": "https://www.remotelatinos.com", "auto_apply": True, "market": "LATAM/EEUU", "session_key": "remotelatinos"},
    {"name": "GetOnBrd", "url": "https://www.getonbrd.com", "auto_apply": True, "market": "LATAM/Chile", "session_key": "getonbrd"},
    {"name": "Torre.ai", "url": "https://torre.ai", "auto_apply": False, "market": "LATAM/EEUU", "session_key": None},
    {"name": "InfoJobs", "url": "https://www.infojobs.net", "auto_apply": False, "market": "España", "session_key": None},
    {"name": "FindJobIT", "url": "https://findjobit.com", "auto_apply": True, "market": "Internacional", "session_key": "findjobit"},
    {"name": "LaraJobs", "url": "https://larajobs.com", "auto_apply": False, "market": "Internacional", "session_key": None},
    {"name": "FlexJobs", "url": "https://www.flexjobs.com", "auto_apply": False, "market": "Internacional", "session_key": None},
    {"name": "Remotive", "url": "https://remotive.com", "auto_apply": False, "market": "Internacional", "session_key": None},
    {"name": "RemoteOK", "url": "https://remoteok.com", "auto_apply": False, "market": "Internacional", "session_key": None},
]


def _cookie_active(session_key: str | None) -> bool:
    if not session_key:
        return False
    path = os.path.join(COOKIES_DIR, f"{session_key}_session.json")
    return os.path.exists(path)


@router.get("")
def list_portals(db: Session = Depends(get_db)):
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
    for p in PORTAL_LIST:
        key = p["name"].lower().replace(" ", "").replace("-", "").replace(".", "")
        cookie_active = _cookie_active(p.get("session_key"))
        portal_data = {k: v for k, v in p.items() if k != "session_key"}
        result.append({
            **portal_data,
            "session_active": cookie_active,
            "applications_count": counts_map.get(key, 0),
        })
    return result


@router.post("/validate")
async def validate_portal(body: dict):
    url: str = body.get("url", "")
    if not url:
        return {"error": "url requerida"}

    result = {
        "url": url,
        "allows_scraping": False,
        "has_google_auth": False,
        "notes": [],
    }

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
                    result["notes"].append("No se detectó autenticación Google en la página principal")
            except Exception as e:
                result["notes"].append(f"Error al acceder a la URL: {str(e)}")
    except Exception as e:
        result["notes"].append(f"Error general: {str(e)}")

    result["automatable"] = result["allows_scraping"] and result["has_google_auth"]
    return result
