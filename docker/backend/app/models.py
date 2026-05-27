from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    portal = Column(String(100), nullable=False)
    title = Column(String(500))
    company = Column(String(500))
    url = Column(String(1000), unique=True, index=True)
    raw_description = Column(Text)
    summary = Column(Text)
    technologies = Column(Text)  # JSON array as string
    modality = Column(String(200))
    salary = Column(String(300))
    score = Column(Float)
    reason = Column(Text)
    status = Column(String(50), default="PENDIENTE", index=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BlockedCompany(Base):
    __tablename__ = "companies_blocked"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), unique=True, nullable=False)
    blocked_at = Column(DateTime, default=datetime.utcnow)


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False)          # ok | parcial | fallido
    requiere_humano = Column(Boolean, default=False)
    motivo = Column(Text)
    paso_alcanzado = Column(Text)
    url_continuar = Column(String(1000))
    cover_letter = Column(Text)
    applied_at = Column(DateTime, default=datetime.utcnow)


class ApplicationAnswer(Base):
    __tablename__ = "application_answers"

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(500), nullable=False)   # "Formación académica"
    keywords = Column(Text, nullable=False)             # JSON: ["formación", "estudios"]
    respuesta = Column(Text, nullable=False)
    portal = Column(String(100), nullable=True)         # None = todos los portales
    activo = Column(Boolean, default=True)
    creado_at = Column(DateTime, default=datetime.utcnow)
