from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base
from app.routers import offers, companies, scraper, answers

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wunen API", version="0.1.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(offers.router)
app.include_router(companies.router)
app.include_router(scraper.router)
app.include_router(answers.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "backend"}
