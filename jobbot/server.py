"""Servidor web que recibe tus mensajes de WhatsApp (webhook de Twilio) y busca ofertas periódicamente."""
import logging
import threading
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, abort, request
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from . import bot, store, whatsapp, writer
from .config import cargar_config, env

log = logging.getLogger(__name__)
app = Flask(__name__)


def _responder(texto: str) -> str:
    r = MessagingResponse()
    r.message(texto)
    return str(r)


def _en_segundo_plano(funcion, *args) -> None:
    """Twilio espera respuesta en <15 s; lo lento (Claude, buscar) se hace aparte y se envía después."""
    def tarea():
        try:
            resultado = funcion(*args)
            whatsapp.enviar(resultado or "No hay ofertas nuevas por ahora. 🙂")
        except Exception as e:
            log.exception("Error en tarea")
            whatsapp.enviar(f"⚠️ Algo falló: {e}")
    threading.Thread(target=tarea, daemon=True).start()


def _verificar_twilio() -> None:
    url_publica = env("PUBLIC_URL", obligatorio=False)
    if not url_publica:
        return  # sin PUBLIC_URL no se puede verificar la firma (solo para pruebas locales)
    validador = RequestValidator(env("TWILIO_AUTH_TOKEN"))
    url = url_publica.rstrip("/") + request.path
    if not validador.validate(url, request.form, request.headers.get("X-Twilio-Signature", "")):
        abort(403)


@app.post("/whatsapp")
def entrante():
    _verificar_twilio()
    if request.form.get("From") != env("MI_WHATSAPP"):
        abort(403)  # solo tú puedes usar el bot

    orden, num = bot.interpretar(request.form.get("Body", ""))

    if orden in ("buscar", "busca"):
        _en_segundo_plano(bot.buscar)
        return _responder("🔎 Buscando ofertas… te aviso en un momento.")
    if orden in ("ofertas", "lista"):
        return _responder(bot.ultimas())
    if orden in ("ver", "carta", "cv"):
        if num is None:
            return _responder(f"Indica el número de la oferta, por ejemplo: *{orden} 12*")
        oferta = store.obtener(num)
        if not oferta:
            return _responder(f"No encuentro la oferta {num}. Escribe *ofertas* para ver los números.")
        if orden == "ver":
            return _responder(bot.detalle(num))
        _en_segundo_plano(writer.redactar, orden, oferta)
        que = "la carta" if orden == "carta" else "las mejoras de tu CV"
        return _responder(f"✍️ Preparando {que} para *{oferta['titulo']}*… (≈1 min)")
    return _responder(bot.AYUDA)


@app.get("/")
def salud():
    return "jobbot funcionando"


def busqueda_programada() -> None:
    try:
        mensaje = bot.buscar()
        if mensaje:
            whatsapp.enviar(mensaje)
    except Exception:
        log.exception("Falló la búsqueda programada")


def arrancar(puerto: int = 5000) -> None:
    horas = cargar_config().get("avisos", {}).get("cada_horas", 6)
    planificador = BackgroundScheduler()
    planificador.add_job(busqueda_programada, "interval", hours=horas, next_run_time=datetime.now())
    planificador.start()
    log.info("Búsqueda automática cada %s h. Escuchando en el puerto %d", horas, puerto)
    app.run(host="0.0.0.0", port=puerto)
