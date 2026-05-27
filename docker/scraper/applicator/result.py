from dataclasses import dataclass, field
from typing import Literal


@dataclass
class ApplyResult:
    status: Literal["ok", "parcial", "fallido"]
    requiere_humano: bool
    motivo: str
    paso_alcanzado: str
    url_continuar: str
    cover_letter: str = ""

    def to_dict(self, offer: dict) -> dict:
        return {
            "status": self.status,
            "requiere_humano": self.requiere_humano,
            "motivo": self.motivo,
            "paso_alcanzado": self.paso_alcanzado,
            "url_continuar": self.url_continuar,
            "empresa": offer.get("company", ""),
            "portal": offer.get("portal", ""),
            "titulo": offer.get("title", ""),
            "score": offer.get("score"),
        }


def session_expired(url: str) -> ApplyResult:
    return ApplyResult(
        status="fallido",
        requiere_humano=True,
        motivo="Sesión expirada. Ejecuta 'python setup_session.py <portal>' en tu Mac para renovarla.",
        paso_alcanzado="Carga de sesión",
        url_continuar=url,
    )


def captcha_detectado(url: str, paso: str) -> ApplyResult:
    return ApplyResult(
        status="parcial",
        requiere_humano=True,
        motivo="CAPTCHA detectado. El formulario fue rellenado pero el envío requiere verificación manual.",
        paso_alcanzado=paso,
        url_continuar=url,
    )


def sin_sesion(portal: str, url: str) -> ApplyResult:
    return ApplyResult(
        status="fallido",
        requiere_humano=True,
        motivo=f"No hay sesión guardada para {portal}. Ejecuta 'python setup_session.py {portal.lower()}' en tu Mac.",
        paso_alcanzado="Inicio",
        url_continuar=url,
    )
