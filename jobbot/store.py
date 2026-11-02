"""Guarda las ofertas en SQLite para no avisarte dos veces de la misma."""
import sqlite3
from contextlib import contextmanager

from .config import RUTA_DB
from .sources import Oferta

ESQUEMA = """
CREATE TABLE IF NOT EXISTS ofertas (
    num         INTEGER PRIMARY KEY AUTOINCREMENT,
    id          TEXT UNIQUE NOT NULL,
    fuente      TEXT, titulo TEXT, empresa TEXT, url TEXT,
    ubicacion   TEXT, etiquetas TEXT, descripcion TEXT,
    publicada   TEXT, salario TEXT,
    encontrada  TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


@contextmanager
def conexion():
    con = sqlite3.connect(RUTA_DB)
    con.row_factory = sqlite3.Row
    con.execute(ESQUEMA)
    try:
        yield con
        con.commit()
    finally:
        con.close()


def guardar_nuevas(ofertas: list[Oferta]) -> list[sqlite3.Row]:
    """Inserta las ofertas que no se habían visto y devuelve solo esas (con su número)."""
    nuevas = []
    with conexion() as con:
        for o in ofertas:
            cur = con.execute(
                "INSERT OR IGNORE INTO ofertas (id, fuente, titulo, empresa, url, ubicacion,"
                " etiquetas, descripcion, publicada, salario) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (o.id, o.fuente, o.titulo, o.empresa, o.url, o.ubicacion,
                 ", ".join(e for e in o.etiquetas if e), o.descripcion, o.publicada, o.salario),
            )
            if cur.rowcount:
                nuevas.append(con.execute("SELECT * FROM ofertas WHERE num = ?", (cur.lastrowid,)).fetchone())
    return nuevas


def obtener(num: int) -> sqlite3.Row | None:
    with conexion() as con:
        return con.execute("SELECT * FROM ofertas WHERE num = ?", (num,)).fetchone()


def ultimas(n: int = 10) -> list[sqlite3.Row]:
    with conexion() as con:
        return con.execute("SELECT * FROM ofertas ORDER BY num DESC LIMIT ?", (n,)).fetchall()


def hay_ofertas() -> bool:
    with conexion() as con:
        return con.execute("SELECT 1 FROM ofertas LIMIT 1").fetchone() is not None
