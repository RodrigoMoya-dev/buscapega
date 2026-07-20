import os
import httpx
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional

from scrapers.remotive import fetch_offers as fetch_remotive
from scrapers.remoteok import fetch_offers as fetch_remoteok
from scrapers.getonbrd import fetch_offers as fetch_getonbrd
from scrapers.findjobit import fetch_offers as fetch_findjobit
from applicator.registry import get_applicator
from applicator import findjobit as findjobit_applicator

app = FastAPI(title="Buscapega Scraper", version="0.2.0")

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
WHATSAPP_URL = os.getenv("WHATSAPP_URL", "http://whatsapp:3001")

# Score mínimo para auto-postular en FindJobIT (0–100)
FINDJOBIT_MIN_SCORE = int(os.getenv("FINDJOBIT_MIN_SCORE", "50"))


# ── Scraping ──────────────────────────────────────────────────────────────────

def _ingest_offers(offers: list):
    saved = skipped = 0
    with httpx.Client(timeout=60.0) as client:
        for offer in offers:
            # Filtrar campos privados (prefijo _) antes de enviar al backend
            clean = {k: v for k, v in offer.items() if not k.startswith("_")}
            try:
                r = client.post(f"{BACKEND_URL}/api/offers/ingest", json=clean)
                result = r.json()
                if result.get("status") == "saved":
                    saved += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"[Scraper] Error ingesting '{offer.get('title', '')}': {e}")
    print(f"[Scraper] Completado: {saved} guardadas, {skipped} ignoradas")


def run_all():
    offers = []
    offers.extend(fetch_remotive())
    offers.extend(fetch_remoteok())
    offers.extend(fetch_getonbrd())
    print(f"[Scraper] Total a ingestar: {len(offers)}")
    _ingest_offers(offers)


@app.post("/run")
def trigger_all(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_all)
    return {"status": "running", "message": "Scraping todos los portales en segundo plano"}


@app.post("/run/remotive")
def trigger_remotive(background_tasks: BackgroundTasks):
    background_tasks.add_task(_ingest_offers, fetch_remotive())
    return {"status": "running", "portal": "Remotive"}


@app.post("/run/remoteok")
def trigger_remoteok(background_tasks: BackgroundTasks):
    background_tasks.add_task(_ingest_offers, fetch_remoteok())
    return {"status": "running", "portal": "RemoteOK"}


@app.post("/run/getonbrd")
def trigger_getonbrd(background_tasks: BackgroundTasks):
    background_tasks.add_task(_ingest_offers, fetch_getonbrd())
    return {"status": "running", "portal": "GetOnBrd"}


# ── FindJobIT: scraping + auto-postulación automática ─────────────────────────

def _send_whatsapp(message: str):
    """Notifica por WhatsApp vía el servicio Baileys."""
    try:
        httpx.post(
            f"{WHATSAPP_URL}/send",
            json={"message": message},
            timeout=10.0
        )
    except Exception as e:
        print(f"[FindJobIT] No se pudo notificar WhatsApp: {e}")


def _update_offer_status(offer_id: int, status: str, application_data: dict = None):
    """Actualiza el estado de una oferta en el backend."""
    try:
        with httpx.Client(timeout=15.0) as client:
            client.patch(
                f"{BACKEND_URL}/api/offers/{offer_id}/set-status",
                json={"status": status}
            )
            if application_data:
                # Registrar en tabla de aplicaciones
                client.post(
                    f"{BACKEND_URL}/api/offers/{offer_id}/record-application",
                    json=application_data
                )
    except Exception as e:
        print(f"[FindJobIT] Error actualizando estado de oferta {offer_id}: {e}")


def run_findjobit():
    """
    Pipeline completo de FindJobIT:
    1. Scraping de ofertas remotas en Chile
    2. Ingestión y evaluación con Claude
    3. Auto-postulación vía email si el score es suficiente
    4. Notificación por WhatsApp
    """
    print("[FindJobIT] Iniciando pipeline completo...")

    # 1. Scraping
    try:
        offers = fetch_findjobit()
    except Exception as e:
        print(f"[FindJobIT] Error en scraping: {e}")
        _send_whatsapp(f"❌ *FindJobIT* — Error durante el scraping: {str(e)[:200]}")
        return

    if not offers:
        print("[FindJobIT] No se encontraron ofertas")
        _send_whatsapp("ℹ️ *FindJobIT* — No hay ofertas nuevas disponibles por ahora.")
        return

    print(f"[FindJobIT] {len(offers)} ofertas a procesar")
    applied = 0
    skipped = 0
    failed = 0
    new_count = 0  # ofertas realmente nuevas (no duplicadas en BD)

    with httpx.Client(timeout=60.0) as client:
        for offer in offers:
            title = offer.get("title", "Sin título")
            company = offer.get("company", "")
            url = offer.get("url", "")

            # Extraer metadata privada antes de enviar al backend
            apply_email = offer.get("_apply_email")
            apply_subject = offer.get("_apply_subject")
            form_accessible = offer.get("_form_accessible", False)

            # 2. Ingestar al backend (evalúa con Claude, deduplica por URL)
            clean_offer = {k: v for k, v in offer.items() if not k.startswith("_")}
            try:
                r = client.post(f"{BACKEND_URL}/api/offers/ingest", json=clean_offer)
                result = r.json()
            except Exception as e:
                print(f"[FindJobIT] Error ingesting '{title}': {e}")
                failed += 1
                continue

            if result.get("status") == "skipped":
                reason = result.get("reason", "duplicate")
                print(f"[FindJobIT] Omitida ({reason}): {title}")
                skipped += 1
                continue

            new_count += 1
            offer_id = result.get("id")
            score = result.get("score") or 0

            print(f"[FindJobIT] Oferta guardada (id={offer_id}, score={score}): {title}")

            # 3. Verificar score mínimo
            if score < FINDJOBIT_MIN_SCORE:
                print(f"[FindJobIT] Score {score} < {FINDJOBIT_MIN_SCORE}, no se postula")
                skipped += 1
                continue

            # 4. Auto-postular: email directo O formulario Playwright (si hay sesión)
            if not apply_email and not form_accessible:
                # Sin email ni sesión → alerta para revisión manual
                print(f"[FindJobIT] Sin email ni sesión activa para '{title}', revisión manual")
                _send_whatsapp(
                    f"👀 *FindJobIT — Oferta interesante (score {score:.0f})*\n"
                    f"*Cargo:* {title}\n"
                    f"*Empresa:* {company}\n"
                    f"⚠️ Sin email directo. Activar sesión: `setup_session.py findjobit`\n"
                    f"*Link:* {url}"
                )
                skipped += 1
                continue

            # Llamar al aplicador — él decide la estrategia (email vs formulario)
            apply_mode = "email" if apply_email else "formulario Playwright"
            print(f"[FindJobIT] Aplicando a '{title}' ({company}) vía {apply_mode}")
            apply_result = findjobit_applicator.apply(offer)

            # 5. Actualizar estado en backend
            status_map = {"ok": "POSTULADA", "parcial": "PARCIAL", "fallido": "FALLIDA"}
            new_status = status_map.get(apply_result.status, "FALLIDA")
            _update_offer_status(offer_id, new_status)

            if apply_result.status == "ok":
                applied += 1
            else:
                failed += 1

    print(f"[FindJobIT] Pipeline finalizado: {new_count} nuevas, {applied} postuladas, {skipped} omitidas, {failed} fallidas")
    if new_count == 0:
        _send_whatsapp("ℹ️ *FindJobIT* — No hay ofertas nuevas disponibles por ahora.")
    elif applied > 0 or failed > 0:
        print(f"[FindJobIT] Resumen: {applied} enviadas, {failed} fallidas")


@app.post("/run/findjobit")
def trigger_findjobit(background_tasks: BackgroundTasks):
    """Disparar el pipeline completo de FindJobIT (scraping + auto-postulación)."""
    background_tasks.add_task(run_findjobit)
    return {
        "status": "running",
        "message": "Pipeline FindJobIT iniciado en segundo plano",
        "portal": "FindJobIT",
    }


# ── Applicator ────────────────────────────────────────────────────────────────

class ApplyRequest(BaseModel):
    offer_id: int
    portal: str
    title: str
    company: str
    url: str
    description: Optional[str] = ""
    technologies: Optional[str] = ""
    score: Optional[float] = None


@app.post("/apply")
def apply_to_offer(req: ApplyRequest):
    applicator = get_applicator(req.portal)
    if not applicator:
        raise HTTPException(
            status_code=400,
            detail=f"Portal '{req.portal}' no soporta auto-postulación o no está configurado."
        )

    offer = req.model_dump()
    result = applicator.apply(offer)
    return result.to_dict(offer)


# ── Prueba de correo ──────────────────────────────────────────────────────────

class TestEmailRequest(BaseModel):
    to: str


@app.post("/test-email")
def test_email(req: TestEmailRequest):
    """Envía un correo de prueba para validar que el correo de postulaciones funciona.

    Reutiliza el mismo mecanismo de envío de las postulaciones (webhook de Google
    Apps Script con respaldo de Gmail SMTP).
    """
    to = (req.to or "").strip()
    if not to:
        return {"status": "error", "message": "No hay correo configurado"}

    tiene_gas = bool(findjobit_applicator.GAS_WEBHOOK_URL)
    tiene_smtp = bool(findjobit_applicator.GMAIL_USER and findjobit_applicator.GMAIL_APP_PASSWORD)
    if not tiene_gas and not tiene_smtp:
        return {
            "status": "error",
            "message": "No hay método de envío configurado. Define GMAIL_USER y "
                       "GMAIL_APP_PASSWORD en docker/.env (o ejecuta ./configuraciones/setup-gmail.sh).",
        }

    try:
        ok = findjobit_applicator._send_email(
            to_email=to,
            subject="Buscapega — correo de prueba ✓",
            body_text="Este es un correo de prueba de Buscapega. Si lo recibiste, el correo "
                      "de postulaciones está funcionando correctamente.",
            body_html="<p>Este es un <strong>correo de prueba</strong> de Buscapega. Si lo "
                      "recibiste, el correo de postulaciones está funcionando correctamente. ✓</p>",
            cv_url=None,
        )
    except Exception as e:
        return {"status": "error", "message": f"Error al enviar el correo: {e}"}

    if ok:
        return {"status": "ok", "message": f"Correo de prueba enviado a {to}"}
    return {
        "status": "error",
        "message": "No se pudo enviar el correo. Revisa GMAIL_USER/GMAIL_APP_PASSWORD "
                   "(o el webhook de Google Apps Script) en docker/.env.",
    }


@app.get("/email-status")
def email_status():
    """Informa si el envío de correos está configurado, sin exponer credenciales.

    Lo consume la web (vía el backend) para avisar cuando falta la contraseña de
    aplicación de Gmail: en el instalador es opcional, así que se puede terminar la
    instalación sin ella y sin enterarse de que las postulaciones por correo no salen.
    """
    tiene_gas = bool(findjobit_applicator.GAS_WEBHOOK_URL)
    tiene_usuario = bool(findjobit_applicator.GMAIL_USER)
    tiene_password = bool(findjobit_applicator.GMAIL_APP_PASSWORD)

    if tiene_gas or (tiene_usuario and tiene_password):
        return {"configurado": True, "motivo": None, "mensaje": None}

    if tiene_usuario and not tiene_password:
        motivo = "falta_password"
        mensaje = (
            "Falta la contraseña de aplicación de Gmail. Las postulaciones por correo "
            "no se enviarán. Agrégala con ./configuraciones/setup-gmail.sh o en "
            "docker/.env (GMAIL_APP_PASSWORD)."
        )
    elif not tiene_usuario:
        motivo = "falta_usuario"
        mensaje = (
            "No hay correo de postulaciones configurado. Configúralo con "
            "./configuraciones/setup-gmail.sh."
        )
    else:
        motivo = "sin_metodo"
        mensaje = "No hay ningún método de envío de correo configurado."

    return {"configurado": False, "motivo": motivo, "mensaje": mensaje}


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "scraper"}
