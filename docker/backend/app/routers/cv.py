import json
import os
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from typing import Any

router = APIRouter(prefix="/api/cv", tags=["cv"])

BUSCAPEGA_DIR = os.getenv("BUSCAPEGA_DIR", "/buscapega")
DATA_DIR = os.path.join(BUSCAPEGA_DIR, "documentos")

CV_ES_PATH = os.path.join(DATA_DIR, "cv_data.json")
CV_EN_PATH = os.path.join(DATA_DIR, "cv_data_en.json")
PROFILE_PATH = os.path.join(DATA_DIR, "perfil_data.json")
PERFIL_MD_PATH = os.path.join(DATA_DIR, "perfil.md")
PERFIL_ROOT_PATH = os.path.join(BUSCAPEGA_DIR, "perfil.md")  # lo lee el evaluador

CV_ES_PDF_PATH = os.path.join(DATA_DIR, "cv_es.pdf")
CV_EN_PDF_PATH = os.path.join(DATA_DIR, "cv_en.pdf")

DEFAULT_CV = {
    "name": "",
    "title": "",
    "presentation": "",
    "contact": {"phone": "", "email": "", "linkedin": "", "github": ""},
    "professional_summary": "",
    "skills": [],
    "experience": [],
    "education": [],
    "languages": [],
}

DEFAULT_PROFILE = {
    "stack": [],
    "avoid_technologies": [],
    "work_modality": {"preference": "", "acceptable": "", "rejected": "", "timezone": "Chile (UTC-3 / UTC-4)"},
    "geo_availability": "",
    "salary": {"usd_min": 0, "usd_preferred": 0, "eur_min": 0, "eur_preferred": 0, "clp_min": 0, "clp_preferred": 0},
    "interested_types": "",
    "avoided_types": "",
    "sectors_preferred": "",
    "sectors_excluded": "",
    "languages": [],
    "contract_type": "",
    "min_project_duration": "",
    "selection_process": "",
    "communication_tools": "",
    "methodology": "",
}


def _read_json(path: str, default: Any) -> Any:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def _write_json(path: str, data: Any):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _cv_to_markdown(cv: dict, lang: str = "es") -> str:
    lines = []
    name = cv.get("name", "")
    title = cv.get("title", "")
    lines.append(f"# {name}")
    if title:
        lines.append(f"**{title}**")
    lines.append("")
    lines.append("---")
    lines.append("")

    contact = cv.get("contact", {})
    if any(contact.values()):
        lines.append("## Contacto" if lang == "es" else "## Contact")
        lines.append("")
        lines.append("| | |")
        lines.append("|---|---|")
        if contact.get("phone"):
            lines.append(f"| Teléfono | {contact['phone']} |" if lang == "es" else f"| Phone | {contact['phone']} |")
        if contact.get("email"):
            lines.append(f"| Email | {contact['email']} |")
        if contact.get("linkedin"):
            lines.append(f"| LinkedIn | {contact['linkedin']} |")
        if contact.get("github"):
            lines.append(f"| GitHub | {contact['github']} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    summary = cv.get("professional_summary", "")
    if summary:
        lines.append("## Resumen Profesional" if lang == "es" else "## Professional Summary")
        lines.append("")
        lines.append(summary)
        lines.append("")
        lines.append("---")
        lines.append("")

    skills = cv.get("skills", [])
    if skills:
        lines.append("## Habilidades Técnicas" if lang == "es" else "## Technical Skills")
        lines.append("")
        by_level: dict = {}
        for s in skills:
            lvl = s.get("level", "Básico")
            by_level.setdefault(lvl, []).append(s.get("name", ""))
        for lvl, names in by_level.items():
            lines.append(f"### {lvl}")
            lines.append(" ".join(f"`{n}`" for n in names))
            lines.append("")
        lines.append("---")
        lines.append("")

    experience = cv.get("experience", [])
    if experience:
        lines.append("## Experiencia Profesional" if lang == "es" else "## Professional Experience")
        lines.append("")
        for exp in experience:
            role = exp.get("role", "")
            company = exp.get("company", "")
            start = exp.get("start", "")
            end = exp.get("end", "A la fecha" if lang == "es" else "Present") if exp.get("current") else exp.get("end", "")
            lines.append(f"### {role}")
            lines.append(f"**{company}** — *{start} – {end}*")
            lines.append("")
            for bullet in exp.get("bullets", []):
                lines.append(f"- {bullet}")
            lines.append("")
            lines.append("---")
            lines.append("")

    education = cv.get("education", [])
    if education:
        lines.append("## Formación Académica" if lang == "es" else "## Education")
        lines.append("")
        lines.append("| Título | Institución | Año |" if lang == "es" else "| Degree | Institution | Year |")
        lines.append("|---|---|---|")
        for e in education:
            lines.append(f"| {e.get('degree','')} | {e.get('institution','')} | {e.get('year','')} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    languages = cv.get("languages", [])
    if languages:
        lines.append("## Idiomas" if lang == "es" else "## Languages")
        lines.append("")
        lines.append("| Idioma | Nivel |" if lang == "es" else "| Language | Level |")
        lines.append("|---|---|")
        for l in languages:
            lines.append(f"| {l.get('language','')} | {l.get('level','')} |")
        lines.append("")

    return "\n".join(lines)


def _profile_to_markdown(profile: dict) -> str:
    lines = ["# Perfil del Candidato", "", "---", ""]

    stack = profile.get("stack", [])
    if stack:
        lines.append("## Stack Tecnológico")
        lines.append("")
        lines.append("| Tecnología | Nivel | Años de experiencia | ¿Dispuesto a trabajar con ella? |")
        lines.append("| --- | --- | --- | --- |")
        for s in stack:
            lines.append(f"| {s.get('tech','')} | {s.get('level','')} | {s.get('years','')} | {s.get('willing','Sí')} |")
        lines.append("")

        avoid = profile.get("avoid_technologies", [])
        if avoid:
            lines.append("**Tecnologías que prefiero evitar:**")
            for t in avoid:
                lines.append(f"- {t}")
        lines.append("")
        lines.append("---")
        lines.append("")

    modality = profile.get("work_modality", {})
    lines.append("## Modalidad de Trabajo")
    lines.append("")
    if modality.get("preference"):
        lines.append(f"- **Preferencia:** {modality['preference']}")
    if modality.get("acceptable"):
        lines.append(f"- **Aceptable:** {modality['acceptable']}")
    if modality.get("rejected"):
        lines.append(f"- **No acepto:** {modality['rejected']}")
    if modality.get("timezone"):
        lines.append(f"- **Zona horaria:** {modality['timezone']}")
    lines.append("")
    lines.append("---")
    lines.append("")

    salary = profile.get("salary", {})
    lines.append("## Expectativa Salarial")
    lines.append("")
    lines.append("| Moneda | Mínimo aceptable | Rango preferido |")
    lines.append("|---|---|---|")
    lines.append(f"| USD (freelance/hora) | {salary.get('usd_min','')} | {salary.get('usd_preferred','')} |")
    lines.append(f"| EUR (freelance/hora) | {salary.get('eur_min','')} | {salary.get('eur_preferred','')} |")
    lines.append(f"| CLP (dependencia mensual) | {salary.get('clp_min','')} | {salary.get('clp_preferred','')} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lang_list = profile.get("languages", [])
    if lang_list:
        lines.append("## Idiomas para el Trabajo")
        lines.append("")
        lines.append("| Idioma | Nivel | Contextos donde lo uso |")
        lines.append("|---|---|---|")
        for l in lang_list:
            lines.append(f"| {l.get('language','')} | {l.get('level','')} | {l.get('contexts','')} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Otros Criterios")
    lines.append("")
    if profile.get("contract_type"):
        lines.append(f"- **Tipo de contrato:** {profile['contract_type']}")
    if profile.get("min_project_duration"):
        lines.append(f"- **Duración mínima de proyecto:** {profile['min_project_duration']}")
    if profile.get("selection_process"):
        lines.append(f"- **Proceso de selección:** {profile['selection_process']}")
    if profile.get("communication_tools"):
        lines.append(f"- **Herramientas de comunicación:** {profile['communication_tools']}")
    if profile.get("methodology"):
        lines.append(f"- **Metodología:** {profile['methodology']}")

    return "\n".join(lines)


@router.get("/es")
def get_cv_es():
    return _read_json(CV_ES_PATH, DEFAULT_CV)


@router.post("/es")
def save_cv_es(data: dict):
    _write_json(CV_ES_PATH, data)
    md = _cv_to_markdown(data, lang="es")
    cv_md_path = os.path.join(DATA_DIR, "cv.md")
    with open(cv_md_path, "w", encoding="utf-8") as f:
        f.write(md)
    return {"status": "ok"}


@router.get("/en")
def get_cv_en():
    return _read_json(CV_EN_PATH, DEFAULT_CV)


@router.post("/en")
def save_cv_en(data: dict):
    _write_json(CV_EN_PATH, data)
    md = _cv_to_markdown(data, lang="en")
    cv_en_md_path = os.path.join(DATA_DIR, "cv_en.md")
    with open(cv_en_md_path, "w", encoding="utf-8") as f:
        f.write(md)
    return {"status": "ok"}


@router.post("/es/upload")
async def upload_cv_es(file: UploadFile = File(...)):
    if file.content_type not in ("application/pdf", "application/octet-stream") and not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")
    os.makedirs(DATA_DIR, exist_ok=True)
    content = await file.read()
    with open(CV_ES_PDF_PATH, "wb") as f:
        f.write(content)
    return {"status": "ok", "filename": "cv_es.pdf"}


@router.get("/es/pdf")
def get_cv_es_pdf():
    if not os.path.exists(CV_ES_PDF_PATH):
        raise HTTPException(status_code=404, detail="CV en español no encontrado")
    return FileResponse(CV_ES_PDF_PATH, media_type="application/pdf", filename="cv_es.pdf")


@router.get("/es/pdf/exists")
def cv_es_pdf_exists():
    return {"exists": os.path.exists(CV_ES_PDF_PATH)}


@router.post("/en/upload")
async def upload_cv_en(file: UploadFile = File(...)):
    if file.content_type not in ("application/pdf", "application/octet-stream") and not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")
    os.makedirs(DATA_DIR, exist_ok=True)
    content = await file.read()
    with open(CV_EN_PDF_PATH, "wb") as f:
        f.write(content)
    return {"status": "ok", "filename": "cv_en.pdf"}


@router.get("/en/pdf")
def get_cv_en_pdf():
    if not os.path.exists(CV_EN_PDF_PATH):
        raise HTTPException(status_code=404, detail="CV in English not found")
    return FileResponse(CV_EN_PDF_PATH, media_type="application/pdf", filename="cv_en.pdf")


@router.get("/en/pdf/exists")
def cv_en_pdf_exists():
    return {"exists": os.path.exists(CV_EN_PDF_PATH)}


@router.get("/profile")
def get_profile():
    return _read_json(PROFILE_PATH, DEFAULT_PROFILE)


@router.post("/profile")
def save_profile(data: dict):
    _write_json(PROFILE_PATH, data)
    md = _profile_to_markdown(data)
    for path in (PERFIL_MD_PATH, PERFIL_ROOT_PATH):
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
    return {"status": "ok"}
