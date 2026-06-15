from .getonbrd import GetOnBrdApplicator
from .tecnoempleo import TecnoempleoApplicator
from .remotelatinos import RemoteLatinosaApplicator
from .chiletrabajos import ChileTrabajosApplicator
from .chumiit import ChumiITApplicator
from . import findjobit as _findjobit_module


class FindJobITApplicator:
    """Wrapper de clase para el applicator funcional de FindJobIT."""
    def apply(self, offer: dict):
        # Indicar que la sesión existe para que intente el formulario
        offer.setdefault("_form_accessible", True)
        return _findjobit_module.apply(offer)


# Mapea el campo `portal` de la BD al applicator correspondiente
REGISTRY: dict = {
    "getonbrd":      GetOnBrdApplicator,
    "GetOnBrd":      GetOnBrdApplicator,
    "tecnoempleo":   TecnoempleoApplicator,
    "Tecnoempleo":   TecnoempleoApplicator,
    "remotelatinos": RemoteLatinosaApplicator,
    "RemoteLatinos": RemoteLatinosaApplicator,
    "chiletrabajos": ChileTrabajosApplicator,
    "ChileTrabajos": ChileTrabajosApplicator,
    "chumiit":       ChumiITApplicator,
    "Chumi-IT":      ChumiITApplicator,
    "findjobit":     FindJobITApplicator,
    "FindJobIT":     FindJobITApplicator,
}


def get_applicator(portal: str):
    """Devuelve una instancia del applicator para el portal dado, o None si no está soportado."""
    cls = REGISTRY.get(portal)
    return cls() if cls else None
