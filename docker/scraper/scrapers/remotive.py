import httpx
import html
import re
from typing import List, Dict

SEARCH_TAGS = {"php", "laravel", "wordpress", "backend", "python", "vue", "vuejs", "woocommerce", "odoo"}


def _clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:3000]


def fetch_offers() -> List[Dict]:
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(
                "https://remotive.com/api/remote-jobs",
                params={"category": "software-dev", "limit": 100},
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        print(f"[Remotive] Error: {e}")
        return []

    offers = []
    for job in data.get("jobs", []):
        tags = {t.lower() for t in job.get("tags", [])}
        if not tags.intersection(SEARCH_TAGS):
            continue
        offers.append({
            "portal": "Remotive",
            "title": job.get("title", ""),
            "company": job.get("company_name", ""),
            "url": job.get("url", ""),
            "description": _clean_html(job.get("description", "")),
            "salary_raw": job.get("salary") or None,
        })

    print(f"[Remotive] {len(offers)} ofertas relevantes")
    return offers
