from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Offer, Application

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
def get_stats(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    sent_this_week = db.query(func.count(Offer.id)).filter(
        Offer.status.in_(["ENVIADA", "POSTULADA"]),
        Offer.updated_at >= week_start,
    ).scalar() or 0

    total_sent = db.query(func.count(Offer.id)).filter(
        Offer.status.in_(["ENVIADA", "POSTULADA"])
    ).scalar() or 0

    total_pending = db.query(func.count(Offer.id)).filter(
        Offer.status == "PENDIENTE"
    ).scalar() or 0

    total_discarded = db.query(func.count(Offer.id)).filter(
        Offer.status == "DESCARTADA"
    ).scalar() or 0

    portal_rows = (
        db.query(Offer.portal, func.count(Offer.id).label("count"))
        .filter(Offer.status.in_(["ENVIADA", "POSTULADA"]))
        .group_by(Offer.portal)
        .all()
    )
    by_portal = [{"portal": r.portal, "count": r.count} for r in portal_rows]

    return {
        "sent_this_week": sent_this_week,
        "total_sent": total_sent,
        "total_pending": total_pending,
        "total_discarded": total_discarded,
        "by_portal": by_portal,
    }
