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
    # En Railway el CV va en la variable CV_TEXTO (no se sube a GitHub por privacidad).
    texto = os.getenv("CV_TEXTO", "").strip()
    if texto:
        return texto
    ruta = RAIZ / "cv.md"
    if not ruta.exists():
        raise FileNotFoundError(
            "No encuentro tu CV. Pégalo en la variable CV_TEXTO (Railway) o en el archivo cv.md."
        )
    return ruta.read_text(encoding="utf-8")


def env(nombre: str, obligatorio: bool = True) -> str:
    valor = os.getenv(nombre, "").strip()
    if obligatorio and not valor:
        raise RuntimeError(f"Falta la variable {nombre} (en .env o en las variables de Railway)")
    return valor


def url_publica() -> str:
    """URL pública del bot. En Railway se detecta sola a partir del dominio generado."""
    url = env("PUBLIC_URL", obligatorio=False)
    if not url and os.getenv("RAILWAY_PUBLIC_DOMAIN"):
        url = "https://" + os.environ["RAILWAY_PUBLIC_DOMAIN"]
    return url.rstrip("/")


# La base de datos va en el disco permanente (volume) si existe, para no repetir avisos al reiniciar.
CARPETA_DATOS = Path(os.getenv("DATA_DIR") or os.getenv("RAILWAY_VOLUME_MOUNT_PATH") or RAIZ)
RUTA_DB = CARPETA_DATOS / "ofertas.db"
