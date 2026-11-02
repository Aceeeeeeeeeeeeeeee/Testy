"""Decide qué ofertas encajan con tus filtros de config.yaml."""
import re

from .sources import Oferta


def _contiene(texto: str, palabra: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(palabra.lower()) + r"(?!\w)", texto.lower()) is not None


def encaja(oferta: Oferta, filtros: dict) -> bool:
    claves = filtros.get("palabras_clave") or []
    excluir = filtros.get("excluir") or []
    ubicaciones = filtros.get("ubicaciones") or []

    if any(_contiene(oferta.titulo, p) for p in excluir):
        return False

    donde = " ".join([oferta.titulo, *oferta.etiquetas])
    if filtros.get("buscar_en_descripcion"):
        donde += " " + oferta.descripcion
    if claves and not any(_contiene(donde, p) for p in claves):
        return False

    if ubicaciones and oferta.ubicacion:
        if not any(u.lower() in oferta.ubicacion.lower() for u in ubicaciones):
            return False
    return True
