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

app = FastAPI(title="Wunen Scraper", version="0.2.0")

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
        return

    print(f"[FindJobIT] {len(offers)} ofertas a procesar")
    applied = 0
    skipped = 0
    failed = 0

    with httpx.Client(timeout=60.0) as client:
        for offer in offers:
            title = offer.get("title", "Sin título")
            company = offer.get("company", "")
            url = offer.get("url", "")

            # Extraer metadata privada antes de enviar al backend
            apply_email = offer.get("_apply_email")
            apply_subject = offer.get("_apply_subject")

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

            offer_id = result.get("id")
            score = result.get("score") or 0

            print(f"[FindJobIT] Oferta guardada (id={offer_id}, score={score}): {title}")

            # 3. Verificar score mínimo
            if score < FINDJOBIT_MIN_SCORE:
                print(f"[FindJobIT] Score {score} < {FINDJOBIT_MIN_SCORE}, no se postula")
                skipped += 1
                continue

            # 4. Auto-postular vía email
            if not apply_email:
                print(f"[FindJobIT] Sin email de contacto para '{title}', se requiere revisión manual")
                # Notificar que requiere revisión
                _send_whatsapp(
                    f"👀 *FindJobIT — Oferta interesante (score {score:.0f})*\n"
                    f"*Cargo:* {title}\n"
                    f"*Empresa:* {company}\n"
                    f"⚠️ No tiene email de postulación directo. Revisar manualmente.\n"
                    f"*Link:* {url}"
                )
                skipped += 1
                continue

            # Agregar metadata de aplicación al offer para el aplicador
            offer["_apply_email"] = apply_email
            offer["_apply_subject"] = apply_subject

            print(f"[FindJobIT] Aplicando a '{title}' ({company}) → {apply_email}")
            apply_result = findjobit_applicator.apply(offer)

            # 5. Actualizar estado en backend
            status_map = {"ok": "POSTULADA", "parcial": "PARCIAL", "fallido": "FALLIDA"}
            new_status = status_map.get(apply_result.status, "FALLIDA")
            _update_offer_status(offer_id, new_status)

            if apply_result.status == "ok":
                applied += 1
            else:
                failed += 1

    print(f"[FindJobIT] Pipeline finalizado: {applied} postuladas, {skipped} omitidas, {failed} fallidas")
    if applied > 0 or failed > 0:
        # Resumen general (las notificaciones individuales ya las envió el aplicador)
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


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "scraper"}
