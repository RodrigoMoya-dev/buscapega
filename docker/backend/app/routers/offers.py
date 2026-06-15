import json
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import case
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import httpx

from app.database import get_db
from app.models import Offer, BlockedCompany, Application
from app.schemas import OfferIngest, OfferResponse
from app.evaluator import evaluate_offer

SCRAPER_URL = os.getenv("SCRAPER_URL", "http://scraper:8001")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/wunen-apply-result")

AUTO_APPLY_PORTALS = [
    "FindJobIT", "findjobit",
    "Tecnoempleo", "tecnoempleo",
    "Chumi-IT", "chumiit",
    "ChileTrabajos", "chiletrabajos",
    "RemoteLatinos", "remotelatinos",
    "GetOnBrd", "getonbrd",
    "Torre.ai", "InfoJobs",
]

router = APIRouter(prefix="/api/offers", tags=["offers"])


@router.post("/ingest", status_code=201)
def ingest_offer(data: OfferIngest, db: Session = Depends(get_db)):
    blocked = db.query(BlockedCompany).filter(
        BlockedCompany.name.ilike(data.company)
    ).first()
    if blocked:
        return {"status": "skipped", "reason": "company_blocked"}

    existing = db.query(Offer).filter(Offer.url == data.url).first()
    if existing:
        return {"status": "skipped", "reason": "duplicate"}

    ev = evaluate_offer(data.title, data.company, data.description, data.salary_raw)

    offer = Offer(
        portal=data.portal,
        title=data.title,
        company=data.company,
        url=data.url,
        raw_description=data.description[:5000],
        summary=ev.get("resumen"),
        technologies=json.dumps(ev.get("tecnologias") or [], ensure_ascii=False),
        modality=ev.get("modalidad"),
        salary=ev.get("salario_estimado") or data.salary_raw,
        score=ev.get("score"),
        reason=ev.get("razon"),
        status="PENDIENTE",
    )
    db.add(offer)
    try:
        db.commit()
        db.refresh(offer)
    except IntegrityError:
        db.rollback()
        return {"status": "skipped", "reason": "duplicate"}

    return {"status": "saved", "id": offer.id, "score": offer.score}


@router.get("", response_model=List[OfferResponse])
def list_offers(status: Optional[str] = "PENDIENTE", db: Session = Depends(get_db)):
    q = db.query(Offer)
    if status:
        q = q.filter(Offer.status == status)
    auto_apply_first = case(
        (Offer.portal.in_(AUTO_APPLY_PORTALS), 0),
        else_=1,
    )
    return q.order_by(auto_apply_first, Offer.score.desc().nullslast(), Offer.scraped_at.desc()).all()


@router.patch("/{offer_id}/save")
def save_offer(offer_id: int, db: Session = Depends(get_db)):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    offer.status = "GUARDADA"
    db.commit()
    return {"status": "ok"}


@router.patch("/{offer_id}/discard")
def discard_offer(offer_id: int, db: Session = Depends(get_db)):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    offer.status = "DESCARTADA"
    db.commit()
    return {"status": "ok"}


@router.post("/reevaluate")
def reevaluate_pending(db: Session = Depends(get_db)):
    offers = db.query(Offer).filter(Offer.score == None, Offer.status == "PENDIENTE").all()
    updated = 0
    for offer in offers:
        ev = evaluate_offer(offer.title, offer.company, offer.raw_description or "", None)
        offer.summary = ev.get("resumen")
        offer.technologies = json.dumps(ev.get("tecnologias") or [], ensure_ascii=False)
        offer.modality = ev.get("modalidad")
        if not offer.salary:
            offer.salary = ev.get("salario_estimado")
        offer.score = ev.get("score")
        offer.reason = ev.get("razon")
        updated += 1
    db.commit()
    return {"status": "ok", "reevaluated": updated}


@router.patch("/{offer_id}/set-status")
def set_offer_status(offer_id: int, payload: dict, db: Session = Depends(get_db)):
    """Actualiza el estado de una oferta. Usado por el scraper tras auto-postular."""
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    new_status = payload.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Falta el campo 'status'")
    offer.status = new_status
    db.commit()
    return {"status": "ok", "new_status": new_status}


@router.patch("/{offer_id}/apply")
def apply_offer(offer_id: int, db: Session = Depends(get_db)):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    offer.status = "ENVIADA"
    db.commit()
    return {"status": "ok", "url": offer.url}


@router.post("/autoapply-batch")
def autoapply_batch(
    background_tasks: BackgroundTasks,
    min_score: int = 40,
    portal: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Auto-postula en background todas las ofertas PENDIENTE con score >= min_score.
    Solo portales que tienen applicator registrado (AUTO_APPLY_PORTALS).
    Opcionalmente filtra por portal (parcial, case-insensitive).
    """
    q = db.query(Offer).filter(
        Offer.status == "PENDIENTE",
        Offer.score >= min_score,
        Offer.portal.in_(AUTO_APPLY_PORTALS),
    )
    if portal:
        q = q.filter(Offer.portal.ilike(f"%{portal}%"))

    offers = q.order_by(Offer.score.desc()).all()

    started = []
    for offer in offers:
        offer.status = "POSTULANDO"
        background_tasks.add_task(
            _run_autoapply,
            offer.id, offer.portal, offer.title, offer.company,
            offer.url, offer.raw_description or "", offer.technologies or "", offer.score,
        )
        started.append({
            "id": offer.id,
            "title": offer.title,
            "portal": offer.portal,
            "score": float(offer.score or 0),
        })

    db.commit()
    print(f"[AutoApply-Batch] Iniciadas {len(started)} postulaciones (min_score={min_score})")
    return {"status": "ok", "started": len(started), "offers": started}


@router.post("/{offer_id}/autoapply")
def autoapply_offer(offer_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    if offer.status not in ("PENDIENTE", "GUARDADA"):
        raise HTTPException(status_code=400, detail=f"Estado actual '{offer.status}' no permite auto-postulación")

    offer.status = "POSTULANDO"
    db.commit()

    background_tasks.add_task(_run_autoapply, offer_id, offer.portal, offer.title,
                               offer.company, offer.url, offer.raw_description or "",
                               offer.technologies or "", offer.score)
    return {"status": "iniciado", "offer_id": offer_id}


def _run_autoapply(offer_id: int, portal: str, title: str, company: str,
                   url: str, description: str, technologies: str, score):
    payload = {
        "offer_id": offer_id,
        "portal": portal,
        "title": title,
        "company": company,
        "url": url,
        "description": description,
        "technologies": technologies,
        "score": score,
    }

    try:
        with httpx.Client(timeout=180.0) as client:
            r = client.post(f"{SCRAPER_URL}/apply", json=payload)
            r.raise_for_status()
            result = r.json()
    except Exception as e:
        result = {
            "status": "fallido",
            "requiere_humano": True,
            "motivo": f"Error al contactar el scraper: {str(e)[:200]}",
            "paso_alcanzado": "Llamada al scraper",
            "url_continuar": url,
            "empresa": company,
            "portal": portal,
            "titulo": title,
            "score": score,
        }

    # Actualizar BD
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        offer = db.query(Offer).filter(Offer.id == offer_id).first()
        if offer:
            status_map = {"ok": "POSTULADA", "parcial": "PARCIAL", "fallido": "FALLIDA"}
            offer.status = status_map.get(result.get("status", "fallido"), "FALLIDA")

        application = Application(
            offer_id=offer_id,
            status=result.get("status", "fallido"),
            requiere_humano=result.get("requiere_humano", True),
            motivo=result.get("motivo", ""),
            paso_alcanzado=result.get("paso_alcanzado", ""),
            url_continuar=result.get("url_continuar", url),
            cover_letter=result.get("cover_letter", ""),
        )
        db.add(application)
        db.commit()
    finally:
        db.close()

    # Notificar a n8n → Telegram
    try:
        with httpx.Client(timeout=10.0) as client:
            client.post(N8N_WEBHOOK_URL, json={"body": result})
    except Exception as e:
        print(f"[AutoApply] Error notificando n8n: {e}")
