import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ApplicationAnswer
from app.schemas import AnswerCreate, AnswerUpdate, AnswerResponse

router = APIRouter(prefix="/api/answers", tags=["answers"])


@router.get("", response_model=List[AnswerResponse])
def list_answers(portal: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(ApplicationAnswer).filter(ApplicationAnswer.activo == True)
    if portal:
        q = q.filter(
            (ApplicationAnswer.portal == portal) | (ApplicationAnswer.portal == None)
        )
    return q.order_by(ApplicationAnswer.id).all()


@router.post("", response_model=AnswerResponse, status_code=201)
def create_answer(data: AnswerCreate, db: Session = Depends(get_db)):
    answer = ApplicationAnswer(
        descripcion=data.descripcion,
        keywords=json.dumps(data.keywords, ensure_ascii=False),
        respuesta=data.respuesta,
        portal=data.portal,
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


@router.put("/{answer_id}", response_model=AnswerResponse)
def update_answer(answer_id: int, data: AnswerUpdate, db: Session = Depends(get_db)):
    answer = db.query(ApplicationAnswer).filter(ApplicationAnswer.id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    if data.descripcion is not None:
        answer.descripcion = data.descripcion
    if data.keywords is not None:
        answer.keywords = json.dumps(data.keywords, ensure_ascii=False)
    if data.respuesta is not None:
        answer.respuesta = data.respuesta
    if data.portal is not None:
        answer.portal = data.portal
    if data.activo is not None:
        answer.activo = data.activo
    db.commit()
    db.refresh(answer)
    return answer


@router.delete("/{answer_id}", status_code=204)
def delete_answer(answer_id: int, db: Session = Depends(get_db)):
    answer = db.query(ApplicationAnswer).filter(ApplicationAnswer.id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    db.delete(answer)
    db.commit()
