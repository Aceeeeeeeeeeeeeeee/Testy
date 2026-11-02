"""Envío de mensajes de WhatsApp a través de Twilio."""
from twilio.rest import Client

from .config import env

LIMITE = 1500  # WhatsApp/Twilio admite 1600 caracteres por mensaje


def _trocear(texto: str) -> list[str]:
    trozos, actual = [], ""
    for parrafo in texto.split("\n"):
        while len(parrafo) > LIMITE:  # párrafo gigante: cortar a lo bruto
            if actual:
                trozos.append(actual)
                actual = ""
            trozos.append(parrafo[:LIMITE])
            parrafo = parrafo[LIMITE:]
        if len(actual) + len(parrafo) + 1 > LIMITE:
            trozos.append(actual)
            actual = parrafo
        else:
            actual = f"{actual}\n{parrafo}" if actual else parrafo
    if actual:
        trozos.append(actual)
    return trozos


def enviar(texto: str, para: str | None = None) -> None:
    cliente = Client(env("TWILIO_ACCOUNT_SID"), env("TWILIO_AUTH_TOKEN"))
    for trozo in _trocear(texto):
        cliente.messages.create(
            from_=env("TWILIO_WHATSAPP_FROM"),
            to=para or env("MI_WHATSAPP"),
            body=trozo,
        )
