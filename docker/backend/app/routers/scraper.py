import os
import httpx
from fastapi import APIRouter, BackgroundTasks

router = APIRouter(prefix="/api/scraper", tags=["scraper"])

SCRAPER_URL = os.getenv("SCRAPER_URL", "http://scraper:8001")


@router.post("/trigger")
async def trigger_scraping(background_tasks: BackgroundTasks):
    background_tasks.add_task(_call_scraper)
    return {"status": "triggered", "message": "Scraping iniciado en segundo plano"}


async def _call_scraper():
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            await client.post(f"{SCRAPER_URL}/run")
        except Exception as e:
            print(f"[Backend] Error al llamar scraper: {e}")
