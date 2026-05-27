import os
from pathlib import Path
from typing import Optional
import anthropic

_client: Optional[anthropic.Anthropic] = None

_PROFILE_PATHS = [
    Path("/wunen/perfil.md"),
    Path("/app/perfil.md"),
]

_FALLBACK_PROFILE = """
Desarrollador web con 10+ años de experiencia en PHP, WordPress/WooCommerce, Laravel y VueJS.
Experiencia en Docker, Python básico, Java/Spring Boot e integración con Odoo.
Trabajo remoto o híbrido. Zona horaria Chile (UTC-3/UTC-4). Inglés B2.
"""


def _load_profile() -> str:
    for path in _PROFILE_PATHS:
        if path.exists():
            return path.read_text(encoding="utf-8")
    return _FALLBACK_PROFILE


def _get_client() -> Optional[anthropic.Anthropic]:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            _client = anthropic.Anthropic(api_key=api_key)
    return _client


_SYSTEM_PROMPT = """Eres un experto en redacción de cartas de presentación para ofertas de trabajo tech.
Redacta cartas concisas (200-300 palabras), en primera persona, sin frases genéricas.
Menciona tecnologías específicas del candidato que encajan con la oferta.
Tono profesional pero cercano. Si el portal es de España, usa vocabulario español (peninsular).
Si es LATAM, usa vocabulario latinoamericano.
Responde SOLO con el texto de la carta, sin asunto ni firma."""


def generate(offer: dict) -> str:
    client = _get_client()
    if not client:
        return _fallback_letter(offer)

    profile = _load_profile()
    prompt = f"""Redacta una carta de presentación para esta oferta:

Empresa: {offer.get('company', '')}
Cargo: {offer.get('title', '')}
Portal: {offer.get('portal', '')}
Tecnologías requeridas: {offer.get('technologies', '')}
Descripción: {offer.get('description', '')[:1500]}

Perfil del candidato:
{profile[:2000]}"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            system=[{"type": "text", "text": _SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"[CoverLetter] Error Claude API: {e}")
        return _fallback_letter(offer)


_ANSWER_SYSTEM = """Eres un asistente que completa formularios de postulación a empleo.
Responde la pregunta del formulario de forma concisa (máximo 200 caracteres), en primera persona, tono profesional.
Responde SOLO con el texto de la respuesta, sin explicaciones ni saludos."""


def generate_answer(question: str, offer: dict) -> str:
    """Genera una respuesta a una pregunta personalizada de un formulario."""
    client = _get_client()
    if not client:
        return ""

    profile = _load_profile()
    prompt = (
        f"Pregunta del formulario: {question}\n\n"
        f"Perfil del candidato:\n{profile[:1000]}\n\n"
        f"Cargo: {offer.get('title', '')}\nEmpresa: {offer.get('company', '')}"
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=120,
            system=[{"type": "text", "text": _ANSWER_SYSTEM, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()[:255]
    except Exception as e:
        print(f"[Answer] Error Claude API: {e}")
        return ""


def _fallback_letter(offer: dict) -> str:
    return (
        f"Estimado equipo de {offer.get('company', 'la empresa')},\n\n"
        f"Me dirijo a ustedes para postular al cargo de {offer.get('title', '')}. "
        f"Cuento con más de 10 años de experiencia en desarrollo web, "
        f"con dominio avanzado de PHP, WordPress/WooCommerce y Laravel, "
        f"y experiencia intermedia en Docker, VueJS y Java/Spring Boot.\n\n"
        f"Trabajo en modalidad remota desde Chile (UTC-3) y tengo nivel de inglés B2. "
        f"Quedo a disposición para una conversación.\n\n"
        f"Saludos cordiales,\nRodrigo Moya"
    )
