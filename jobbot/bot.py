"""Lógica del bot: buscar ofertas, formatear avisos y responder a tus órdenes."""
import logging

from . import store
from .config import cargar_config
from .matcher import encaja
from .sources import descargar_todas

log = logging.getLogger(__name__)

AYUDA = """🤖 *Bot de empleo remoto*
• *buscar* — busca ofertas nuevas ahora
• *ofertas* — muestra las últimas ofertas guardadas
• *ver 12* — detalles de la oferta nº 12
• *carta 12* — carta de presentación para la oferta 12
• *cv 12* — cómo adaptar tu CV a la oferta 12
• *ayuda* — este mensaje"""


def linea(o) -> str:
    extra = f" · 💰 {o['salario']}" if o["salario"] else ""
    return f"*{o['num']}.* {o['titulo']} — {o['empresa']}\n🌍 {o['ubicacion'] or '?'}{extra}\n{o['url']}"


def buscar() -> str | None:
    """Descarga, filtra y guarda ofertas. Devuelve el mensaje a enviar o None si no hay nuevas."""
    cfg = cargar_config()
    primera_vez = not store.hay_ofertas()
    ofertas = [o for o in descargar_todas(cfg.get("fuentes", [])) if encaja(o, cfg.get("busqueda", {}))]
    nuevas = store.guardar_nuevas(ofertas)
    log.info("%d ofertas encajan, %d nuevas", len(ofertas), len(nuevas))
    if not nuevas:
        return None

    maximo = cfg.get("avisos", {}).get("max_por_aviso", 10)
    cabecera = f"🔎 *{len(nuevas)} ofertas {'encontradas' if primera_vez else 'nuevas'}*"
    cuerpo = "\n\n".join(linea(o) for o in nuevas[:maximo])
    pie = ""
    if len(nuevas) > maximo:
        pie = f"\n\n…y {len(nuevas) - maximo} más. Escribe *ofertas* para ver las últimas."
    return f"{cabecera}\n\n{cuerpo}{pie}\n\nResponde *carta N* o *cv N* para postular."


def detalle(num: int) -> str:
    o = store.obtener(num)
    if not o:
        return f"No encuentro la oferta {num}."
    desc = o["descripcion"][:1200] + ("…" if len(o["descripcion"]) > 1200 else "")
    return f"{linea(o)}\n🏷️ {o['etiquetas']}\n📡 {o['fuente']}\n\n{desc}"


def ultimas() -> str:
    filas = store.ultimas(10)
    if not filas:
        return "Aún no hay ofertas guardadas. Escribe *buscar*."
    return "📋 *Últimas ofertas*\n\n" + "\n\n".join(linea(o) for o in filas)


def interpretar(texto: str) -> tuple[str, int | None]:
    """Convierte 'Carta 12' en ('carta', 12)."""
    partes = texto.strip().lower().split()
    if not partes:
        return "ayuda", None
    orden = partes[0].lstrip("/")
    num = int(partes[1].lstrip("#")) if len(partes) > 1 and partes[1].lstrip("#").isdigit() else None
    return orden, num
