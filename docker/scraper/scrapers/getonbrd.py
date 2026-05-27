import re
import httpx
from typing import List, Dict

SEARCH_TAGS = {"php", "laravel", "wordpress", "backend", "python", "vue", "vuejs", "woocommerce", "odoo", "javascript"}
CATEGORIES = ["programming", "devops-sysadmin", "data-science"]
BASE_URL = "https://www.getonbrd.com/api/v0"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Wunen/1.0; personal-job-search)",
    "Accept": "application/json",
}


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:3000]


def _build_salary(attrs: dict) -> str | None:
    min_s = attrs.get("min_salary")
    max_s = attrs.get("max_salary")
    if min_s and max_s:
        return f"${min_s:,}–${max_s:,} USD/mes"
    if min_s:
        return f"desde ${min_s:,} USD/mes"
    return None


def fetch_offers() -> List[Dict]:
    offers = []
    seen_urls: set = set()

    with httpx.Client(timeout=30.0, headers=_HEADERS) as client:
        for category in CATEGORIES:
            page = 0
            while True:
                try:
                    resp = client.get(
                        f"{BASE_URL}/categories/{category}/jobs",
                        params={"per_page": 100, "page": page},
                    )
                    resp.raise_for_status()
                    payload = resp.json()
                except Exception as e:
                    print(f"[GetOnBrd] Error en categoría '{category}' página {page}: {e}")
                    break

                jobs = payload.get("data", [])
                if not jobs:
                    break

                # Sideloaded related resources (JSON:API includes)
                included = {}
                for item in payload.get("included", []):
                    key = (item.get("type"), item.get("id"))
                    included[key] = item

                for job in jobs:
                    attrs = job.get("attributes", {})
                    links = job.get("links", {})
                    rels = job.get("relationships", {})

                    # Tags from included resources
                    tag_refs = rels.get("tags", {}).get("data", [])
                    tags = set()
                    for ref in tag_refs:
                        inc = included.get((ref.get("type"), ref.get("id")), {})
                        tag_name = inc.get("attributes", {}).get("name", "")
                        if tag_name:
                            tags.add(tag_name.lower())
                    # Fallback: tags can also appear inline as attribute
                    for t in attrs.get("tag_list", []):
                        tags.add(t.lower())

                    if not tags.intersection(SEARCH_TAGS):
                        continue

                    url = links.get("public_url", "")
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)

                    # Company from included resources
                    company_ref = rels.get("company", {}).get("data", {})
                    company_inc = included.get((company_ref.get("type"), company_ref.get("id")), {})
                    company_name = company_inc.get("attributes", {}).get("name", "")

                    description = _clean_text(
                        (attrs.get("description") or "") + " " +
                        (attrs.get("functions") or "") + " " +
                        (attrs.get("projects") or "")
                    )

                    modality = "Remoto" if attrs.get("remote") else None

                    offers.append({
                        "portal": "GetOnBrd",
                        "title": attrs.get("title", ""),
                        "company": company_name,
                        "url": url,
                        "description": description,
                        "salary_raw": _build_salary(attrs),
                    })

                # GetOnBrd paginates — stop if we got fewer than per_page
                if len(jobs) < 100:
                    break
                page += 1

    print(f"[GetOnBrd] {len(offers)} ofertas relevantes")
    return offers
