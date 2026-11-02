"""Descarga ofertas remotas de APIs públicas y las normaliza a un mismo formato."""
import html
import logging
import re
from dataclasses import dataclass, field

import requests

log = logging.getLogger(__name__)
HEADERS = {"User-Agent": "jobbot/1.0 (busqueda personal de empleo)"}
TIMEOUT = 30


@dataclass
class Oferta:
    id: str            # único: "fuente:id"
    fuente: str
    titulo: str
    empresa: str
    url: str
    ubicacion: str = ""
    etiquetas: list[str] = field(default_factory=list)
    descripcion: str = ""
    publicada: str = ""
    salario: str = ""


def limpiar_html(texto: str) -> str:
    texto = re.sub(r"<(br|/p|/li|/h\d)[^>]*>", "\n", texto or "", flags=re.I)
    texto = re.sub(r"<[^>]+>", "", texto)
    texto = html.unescape(texto)
    return re.sub(r"\n\s*\n+", "\n\n", texto).strip()


def remotive() -> list[Oferta]:
    r = requests.get("https://remotive.com/api/remote-jobs", headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return [
        Oferta(
            id=f"remotive:{j['id']}",
            fuente="Remotive",
            titulo=j.get("title", ""),
            empresa=j.get("company_name", ""),
            url=j.get("url", ""),
            ubicacion=j.get("candidate_required_location", ""),
            etiquetas=list(j.get("tags") or []) + [j.get("category", "")],
            descripcion=limpiar_html(j.get("description", "")),
            publicada=j.get("publication_date", ""),
            salario=j.get("salary", "") or "",
        )
        for j in r.json().get("jobs", [])
    ]


def remoteok() -> list[Oferta]:
    r = requests.get("https://remoteok.com/api", headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    ofertas = []
    for j in r.json():
        if "id" not in j or "position" not in j:  # el primer elemento es un aviso legal
            continue
        salario = ""
        if j.get("salary_min"):
            salario = f"{j['salary_min']}–{j.get('salary_max', '')} USD"
        ofertas.append(Oferta(
            id=f"remoteok:{j['id']}",
            fuente="RemoteOK",
            titulo=j.get("position", ""),
            empresa=j.get("company", ""),
            url=j.get("url", ""),
            ubicacion=j.get("location", "") or "Worldwide",
            etiquetas=list(j.get("tags") or []),
            descripcion=limpiar_html(j.get("description", "")),
            publicada=j.get("date", ""),
            salario=salario,
        ))
    return ofertas


def arbeitnow() -> list[Oferta]:
    r = requests.get("https://www.arbeitnow.com/api/job-board-api", headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return [
        Oferta(
            id=f"arbeitnow:{j['slug']}",
            fuente="Arbeitnow",
            titulo=j.get("title", ""),
            empresa=j.get("company_name", ""),
            url=j.get("url", ""),
            ubicacion=j.get("location", ""),
            etiquetas=list(j.get("tags") or []) + list(j.get("job_types") or []),
            descripcion=limpiar_html(j.get("description", "")),
            publicada=str(j.get("created_at", "")),
        )
        for j in r.json().get("data", [])
        if j.get("remote")  # solo remotas
    ]


FUENTES = {"remotive": remotive, "remoteok": remoteok, "arbeitnow": arbeitnow}


def descargar_todas(nombres: list[str]) -> list[Oferta]:
    resultado = []
    for nombre in nombres:
        funcion = FUENTES.get(nombre.lower())
        if not funcion:
            log.warning("Fuente desconocida: %s", nombre)
            continue
        try:
            ofertas = funcion()
            log.info("%s: %d ofertas", nombre, len(ofertas))
            resultado.extend(ofertas)
        except Exception as e:  # una fuente caída no debe tumbar las demás
            log.warning("No se pudo leer %s: %s", nombre, e)
    return resultado
