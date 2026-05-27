import os
import json
from typing import Optional
import anthropic


def _load_profile() -> str:
    try:
        with open("/wunen/perfil.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Candidato con 15+ años en PHP, WordPress, Laravel, VueJS, Docker. Salario mínimo: USD 9/h."


_profile_text = _load_profile()

_SYSTEM_PROMPT = f"""Eres un asistente experto en evaluación de ofertas de trabajo.

Analiza la oferta y responde ÚNICAMENTE con un JSON válido, sin texto adicional:

{{
  "resumen": "descripción breve del perfil buscado (2-3 oraciones)",
  "tecnologias": ["tech1", "tech2"],
  "modalidad": "remoto|híbrido|presencial|no especificado",
  "salario_estimado": "rango indicado o 'No indicado'",
  "score": <0-100>,
  "razon": "explicación del score en 1-2 oraciones"
}}

PERFIL DEL CANDIDATO:
{_profile_text}

Criterios de score:
- Stack tecnológico match (40%): PHP/WordPress/Laravel/VueJS avanzado, Python/Docker/Java intermedio
- Evitar: .Net, ASP, Angular
- Modalidad (25%): remoto o híbrido preferido, NO presencial
- Salario (25%): mínimo USD 9/h, EUR 9/h, o CLP 1.200.000/mes
- Otros factores (10%)

Score: 0-40=no encaja, 41-60=parcial, 61-80=buen encaje, 81-100=excelente"""

_client: Optional[anthropic.Anthropic] = None


def _get_client() -> Optional[anthropic.Anthropic]:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            _client = anthropic.Anthropic(api_key=api_key)
    return _client


def evaluate_offer(title: str, company: str, description: str, salary_raw: Optional[str] = None) -> dict:
    client = _get_client()
    if not client:
        return {
            "resumen": None,
            "tecnologias": None,
            "modalidad": None,
            "salario_estimado": salary_raw,
            "score": None,
            "razon": "Sin evaluación (configura ANTHROPIC_API_KEY)",
        }

    offer_text = f"Título: {title}\nEmpresa: {company}\n"
    if salary_raw:
        offer_text += f"Salario: {salary_raw}\n"
    offer_text += f"\n{description}"

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=[{"type": "text", "text": _SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": offer_text}],
        )
        return json.loads(response.content[0].text)
    except Exception as e:
        print(f"[Evaluator] Error Claude API: {e}. Usando evaluador local.")
        return _local_evaluate(title, description, salary_raw)


# --- Evaluador local (sin API) ---

_TECH_SCORES = {
    "php": 15, "wordpress": 15, "woocommerce": 12, "laravel": 12,
    "vuejs": 10, "vue": 10, "javascript": 8, "js": 5,
    "docker": 8, "python": 7, "odoo": 8, "java": 6, "spring": 5,
    "mysql": 5, "sql": 4, "linux": 4, "git": 3, "api": 3,
    "react": 4, "node": 4, "typescript": 4, "css": 2, "html": 2,
}
_AVOID = {"angular", ".net", "asp.net", "c#", "dotnet", "ruby", "rails", "ios", "swift", "kotlin"}
_REMOTE_WORDS = {"remote", "remoto", "teletrabajo", "anywhere", "worldwide", "distributed"}
_HYBRID_WORDS = {"hybrid", "híbrido", "flexible"}


def _local_evaluate(title: str, description: str, salary_raw: Optional[str]) -> dict:
    text = (title + " " + description).lower()
    words = set(text.replace(",", " ").replace("/", " ").split())

    # Tecnologías detectadas
    techs_found = [t for t in _TECH_SCORES if t in text]
    avoid_found = [t for t in _AVOID if t in text]

    # Score: tecnologías (40 pts max)
    tech_score = min(40, sum(_TECH_SCORES[t] for t in techs_found))
    if avoid_found:
        tech_score = max(0, tech_score - 20)

    # Modalidad (25 pts)
    if words & _REMOTE_WORDS:
        modality = "remoto"
        mod_score = 25
    elif words & _HYBRID_WORDS:
        modality = "híbrido"
        mod_score = 15
    else:
        modality = "no especificado"
        mod_score = 10

    # Salario (25 pts) — estimación básica
    sal_score = 12  # neutro si no hay info
    if salary_raw:
        sal_lower = salary_raw.lower()
        if any(x in sal_lower for x in ["$", "usd", "eur", "€"]):
            sal_score = 18

    score = int(tech_score + mod_score + sal_score + 5)  # +5 base

    # Resumen
    tech_display = [t.capitalize() for t in techs_found[:6]] or ["No especificadas"]
    avoid_msg = f" Requiere {', '.join(avoid_found)} que prefiero evitar." if avoid_found else ""
    resumen = (
        f"Oferta de {title} en {modality}. "
        f"Tecnologías detectadas: {', '.join(tech_display)}.{avoid_msg} "
        f"[Evaluación local — sin API Claude]"
    )

    razon = f"Stack {'compatible' if tech_score >= 20 else 'poco compatible'} con el perfil"
    if avoid_found:
        razon += f"; incluye {', '.join(avoid_found)} (a evitar)"
    razon += f"; modalidad {modality}"

    return {
        "resumen": resumen,
        "tecnologias": [t.capitalize() for t in techs_found[:8]],
        "modalidad": modality,
        "salario_estimado": salary_raw or "No indicado",
        "score": min(score, 95),
        "razon": razon,
    }
