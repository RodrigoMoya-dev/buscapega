from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BlockedCompany
from app.schemas import BlockCompanyRequest, BlockedCompanyResponse

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.post("/block", status_code=201)
def block_company(data: BlockCompanyRequest, db: Session = Depends(get_db)):
    existing = db.query(BlockedCompany).filter(BlockedCompany.name == data.name).first()
    if existing:
        return {"status": "already_blocked"}
    blocked = BlockedCompany(name=data.name)
    db.add(blocked)
    db.commit()
    return {"status": "blocked", "name": data.name}


@router.get("/blocked", response_model=List[BlockedCompanyResponse])
def list_blocked(db: Session = Depends(get_db)):
    return db.query(BlockedCompany).order_by(BlockedCompany.blocked_at.desc()).all()
