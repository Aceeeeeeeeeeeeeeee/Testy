"""Usa Claude para redactar cartas de presentación y adaptar tu CV a una oferta."""
import anthropic

from .config import cargar_config, cargar_cv

MODELO = "claude-opus-5-5"
client = anthropic.Anthropic()  # lee ANTHROPIC_API_KEY del entorno

SISTEMA = """Eres un asesor de carrera experto en empleo remoto internacional. \
Ayudas a una persona concreta a postular a ofertas usando SOLO la información real de su CV: \
nunca inventes experiencia, títulos, empresas ni cifras. Si a la persona le falta algo que pide la \
oferta, no lo ocultes ni lo inventes; destaca lo transferible. \
Escribe en texto plano apto para WhatsApp (puedes usar *negrita* con asteriscos), sin Markdown con #."""

TAREAS = {
    "carta": """Redacta una carta de presentación para esta oferta.
- 180–250 palabras, tono profesional y cercano, nada genérico.
- Primer párrafo: por qué esta empresa/puesto concretamente.
- Conecta 2–3 logros reales del CV con requisitos clave de la oferta.
- Cierra con disponibilidad para una llamada y la firma indicada.""",
    "cv": """Dime cómo adaptar mi CV a esta oferta. Devuelve:
1. *Encaje*: puntuación del 1 al 10 y una frase de por qué.
2. *Resumen profesional* reescrito (3–4 líneas) orientado a esta oferta.
3. *Viñetas a destacar o reescribir*: 4–6 viñetas mejoradas usando solo hechos del CV.
4. *Palabras clave* de la oferta que conviene incluir (para filtros ATS).
5. *Huecos*: requisitos que no cubro y cómo abordarlos con honestidad.""",
}


def redactar(tipo: str, oferta) -> str:
    cfg = cargar_config().get("redaccion", {})
    idioma = cfg.get("idioma", "auto")
    instruccion_idioma = (
        "Escribe en el mismo idioma en que está redactada la oferta."
        if idioma == "auto" else f"Escribe en {idioma}."
    )
    prompt = f"""<mi_cv>
{cargar_cv()}
</mi_cv>

<oferta>
Puesto: {oferta['titulo']}
Empresa: {oferta['empresa']}
Ubicación: {oferta['ubicacion']}
Etiquetas: {oferta['etiquetas']}
Salario: {oferta['salario'] or 'no indicado'}
Enlace: {oferta['url']}

{oferta['descripcion']}
</oferta>

Firma a usar: {cfg.get('firma', '')}

{TAREAS[tipo]}
{instruccion_idioma}"""

    respuesta = client.beta.messages.create(
        model=MODELO,
        max_tokens=16000,
        system=SISTEMA,
        thinking={"type": "adaptive"},
        output_config={"effort": "medium"},
        messages=[{"role": "user", "content": prompt}],
        # Si el modelo rechazara la petición, la API la reintenta con otro modelo automáticamente.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if respuesta.stop_reason == "refusal":
        return "Claude no pudo generar este texto para esa oferta. Prueba con otra."
    texto = "".join(b.text for b in respuesta.content if b.type == "text").strip()
    if respuesta.stop_reason == "max_tokens":
        texto += "\n\n(El texto se cortó por longitud.)"
    return texto
