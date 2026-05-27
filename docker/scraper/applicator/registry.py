from .getonbrd import GetOnBrdApplicator
from .tecnoempleo import TecnoempleoApplicator
from .remotelatinos import RemoteLatinosaApplicator
from .chiletrabajos import ChileTrabajosApplicator
from .chumiit import ChumiITApplicator

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
}


def get_applicator(portal: str):
    """Devuelve una instancia del applicator para el portal dado, o None si no está soportado."""
    cls = REGISTRY.get(portal)
    return cls() if cls else None
