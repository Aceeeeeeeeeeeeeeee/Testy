# 🤖 jobbot — tu asistente de búsqueda de empleo remoto por WhatsApp

> 📱 **¿Usas iPad?** Ve directamente a la [guía de Railway](GUIA_RAILWAY.md). Lo de abajo es para instalarlo en un ordenador.

Este bot:

1. **Busca ofertas remotas** cada pocas horas en Remotive, RemoteOK y Arbeitnow, con tus palabras clave.
2. **Te avisa por WhatsApp** solo de las ofertas **nuevas** y las numera.
3. Le respondes por WhatsApp y **Claude redacta una carta de presentación** o te dice **cómo adaptar tu CV** a esa oferta, usando solo datos reales de tu CV.

```
Bot:  🔎 3 ofertas nuevas
      *14.* Customer Support Team Lead — Acme 🌍 Worldwide  https://...
Tú:   carta 14
Bot:  ✍️ Preparando la carta…
Bot:  Estimado equipo de Acme: ...
```

| Mensaje       | Qué hace                                          |
|---------------|---------------------------------------------------|
| `buscar`      | Busca ofertas nuevas ahora                        |
| `ofertas`     | Muestra las últimas 10 ofertas guardadas          |
| `ver 14`      | Muestra la descripción de la oferta 14            |
| `carta 14`    | Escribe una carta de presentación para la 14      |
| `cv 14`       | Dice cuánto encajas y cómo adaptar tu CV a la 14  |
| `ayuda`       | Muestra la lista de órdenes                       |

---

## Puesta en marcha (≈20 minutos)

### 1. Instalar
Necesitas Python 3.10 o superior.
```bash
python -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Tus datos
```bash
cp config.example.yaml config.yaml   # palabras clave, exclusiones, ubicaciones…
cp cv.example.md cv.md               # pega aquí tu CV en texto
cp .env.example .env                 # claves (paso 3 y 4)
```
Edita `config.yaml` con **los puestos que buscas** (ya viene preparado para atención al cliente, analista de calidad y team leader).

### 3. Clave de Claude
Crea una API key en <https://platform.claude.com> y ponla en `.env` como `ANTHROPIC_API_KEY`.
Cada carta cuesta unos céntimos.

### 4. WhatsApp con Twilio (gratis para probar)
1. Crea una cuenta en <https://www.twilio.com>.
2. Ve a **Messaging → Try it out → Send a WhatsApp message** (el *Sandbox*).
3. Desde tu móvil manda a **+1 415 523 8886** el mensaje `join <tu-código>` que te indica la página.
4. Copia en `.env`: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` y tu número en `MI_WHATSAPP`
   (formato `whatsapp:+34600111222`, con código de país).

### 5. Probar en la terminal (sin WhatsApp)
```bash
python -m jobbot buscar       # lista las ofertas que encajan
python -m jobbot carta 1      # carta para la oferta 1
python -m jobbot cv 1         # sugerencias de CV para la oferta 1
```

### 6. Activar el bot de WhatsApp
```bash
python -m jobbot servir
```
Para que Twilio pueda llegar a tu ordenador, expónlo a internet, por ejemplo con
[ngrok](https://ngrok.com): `ngrok http 5000`. Copia la URL `https://….ngrok-free.app`:

- en `.env` como `PUBLIC_URL` (sirve para verificar que los mensajes vienen de Twilio), y
- en Twilio, en el Sandbox → **When a message comes in**: `https://….ngrok-free.app/whatsapp` (método POST).

Escribe `ayuda` al bot por WhatsApp. ¡Listo! Buscará solo cada `cada_horas` horas.

---

## Tenerlo encendido 24/7 (sin ordenador)
📱 **Sigue la [guía para Railway desde el iPad](GUIA_RAILWAY.md).** El bot queda funcionando
en la nube, con tu CV en la variable `CV_TEXTO` y las ofertas guardadas en un disco permanente.

Alternativa sin servidor: solo avisos (sin responder) con cron:
```
0 */6 * * *  cd /ruta/jobbot && .venv/bin/python -m jobbot buscar --enviar
```

## Notas
- **Privacidad:** el bot solo obedece al número de `MI_WHATSAPP`. Tu CV se envía a la API de Claude solo cuando pides una carta o un CV.
- **Honestidad:** las instrucciones prohíben a Claude inventar experiencia; revisa siempre el texto antes de enviarlo.
- El Sandbox de Twilio caduca a las 72 h sin mensajes: vuelve a mandar `join <código>`. Para uso permanente hay que registrar un número de WhatsApp Business en Twilio.
- ¿Más bolsas de empleo? Añade una función en `jobbot/sources.py` y regístrala en `FUENTES`.
