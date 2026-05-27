import json
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class OfferIngest(BaseModel):
    portal: str
    title: str
    company: str
    url: str
    description: str
    salary_raw: Optional[str] = None


class OfferResponse(BaseModel):
    id: int
    portal: str
    title: str
    company: str
    url: str
    summary: Optional[str] = None
    technologies: Optional[str] = None
    modality: Optional[str] = None
    salary: Optional[str] = None
    score: Optional[float] = None
    reason: Optional[str] = None
    status: str
    scraped_at: datetime

    class Config:
        from_attributes = True


class BlockCompanyRequest(BaseModel):
    name: str


class BlockedCompanyResponse(BaseModel):
    id: int
    name: str
    blocked_at: datetime

    class Config:
        from_attributes = True


class AnswerCreate(BaseModel):
    descripcion: str
    keywords: List[str]
    respuesta: str
    portal: Optional[str] = None


class AnswerUpdate(BaseModel):
    descripcion: Optional[str] = None
    keywords: Optional[List[str]] = None
    respuesta: Optional[str] = None
    portal: Optional[str] = None
    activo: Optional[bool] = None


class AnswerResponse(BaseModel):
    id: int
    descripcion: str
    keywords: List[str]
    respuesta: str
    portal: Optional[str] = None
    activo: bool
    creado_at: datetime

    @field_validator("keywords", mode="before")
    @classmethod
    def parse_keywords(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    class Config:
        from_attributes = True
