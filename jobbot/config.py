import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")


def cargar_config() -> dict:
    ruta = RAIZ / "config.yaml"
    if not ruta.exists():
        ruta = RAIZ / "config.example.yaml"
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f)


def cargar_cv() -> str:
    ruta = RAIZ / "cv.md"
    if not ruta.exists():
        raise FileNotFoundError("No encuentro cv.md. Copia cv.example.md como cv.md y pega tu CV.")
    return ruta.read_text(encoding="utf-8")


def env(nombre: str, obligatorio: bool = True) -> str:
    valor = os.getenv(nombre, "").strip()
    if obligatorio and not valor:
        raise RuntimeError(f"Falta la variable {nombre} en el archivo .env")
    return valor


RUTA_DB = RAIZ / "ofertas.db"
