"""Uso:
    python -m jobbot servir          # arranca el bot de WhatsApp (+ búsqueda automática)
    python -m jobbot buscar          # busca una vez y muestra el resultado en la terminal
    python -m jobbot buscar --enviar # busca una vez y lo manda por WhatsApp (útil con cron)
    python -m jobbot carta 12        # carta para la oferta 12 en la terminal
    python -m jobbot cv 12           # sugerencias de CV para la oferta 12
"""
import argparse
import logging
import os

from . import bot, store


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    p = argparse.ArgumentParser(prog="jobbot", description="Bot de búsqueda de empleo remoto")
    sub = p.add_subparsers(dest="orden", required=True)
    s = sub.add_parser("servir")
    s.add_argument("--puerto", type=int, default=int(os.getenv("PORT", 5000)))
    b = sub.add_parser("buscar")
    b.add_argument("--enviar", action="store_true", help="enviar el resultado por WhatsApp")
    for nombre in ("carta", "cv", "ver"):
        sub.add_parser(nombre).add_argument("num", type=int)
    args = p.parse_args()

    if args.orden == "servir":
        from .server import arrancar
        arrancar(args.puerto)
    elif args.orden == "buscar":
        mensaje = bot.buscar() or "No hay ofertas nuevas."
        if args.enviar:
            from .whatsapp import enviar
            enviar(mensaje)
        print(mensaje)
    elif args.orden == "ver":
        print(bot.detalle(args.num))
    else:
        oferta = store.obtener(args.num)
        if not oferta:
            raise SystemExit(f"No existe la oferta {args.num}. Ejecuta primero: python -m jobbot buscar")
        from .writer import redactar
        print(redactar(args.orden, oferta))


if __name__ == "__main__":
    main()
