import httpx
import html
import re
from typing import List, Dict

SEARCH_TAGS = {"php", "laravel", "wordpress", "backend", "python", "vue", "vuejs", "javascript", "woocommerce"}

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Wunen/1.0; personal-job-search)"}


def _clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:3000]


def fetch_offers() -> List[Dict]:
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get("https://remoteok.com/api", headers=_HEADERS)
            resp.raise_for_status()
            jobs = resp.json()
    except Exception as e:
        print(f"[RemoteOK] Error: {e}")
        return []

    # Skip first element (legal notice)
    if jobs and isinstance(jobs[0], dict) and "legal" in jobs[0]:
        jobs = jobs[1:]

    offers = []
    for job in jobs:
        if not isinstance(job, dict):
            continue
        tags = {t.lower() for t in job.get("tags", [])}
        if not tags.intersection(SEARCH_TAGS):
            continue

        salary_raw = None
        if job.get("salary_min") and job.get("salary_max"):
            salary_raw = f"${job['salary_min']:,}–${job['salary_max']:,} USD/año"

        job_id = job.get("id", "")
        url = job.get("url") or f"https://remoteok.com/remote-jobs/{job_id}"

        offers.append({
            "portal": "RemoteOK",
            "title": job.get("position", ""),
            "company": job.get("company", ""),
            "url": url,
            "description": _clean_html(job.get("description", "")),
            "salary_raw": salary_raw,
        })

    print(f"[RemoteOK] {len(offers)} ofertas relevantes")
    return offers
