# 📱 Poner el bot en marcha desde el iPad (Railway)

Todo se hace desde **Safari en el iPad** y **WhatsApp en tu móvil**. No necesitas ordenador.
Tiempo: unos 30 minutos. Ve marcando cada paso ✅.

Al final tendrás el bot funcionando las 24 horas: buscará ofertas cada 6 horas y podrás
escribirle por WhatsApp.

> 💡 **Consejo:** abre una nota en el iPad para ir pegando las claves que vayas copiando.
> Son secretas: no las compartas con nadie ni las publiques en GitHub.

---

## Paso 1 · Clave de Claude (para las cartas) — 5 min

1. Entra en **https://platform.claude.com** y crea una cuenta.
2. En **Billing**, añade una tarjeta y un saldo pequeño (5 USD dan para muchísimas cartas).
3. Ve a **API Keys → Create Key**, ponle de nombre `jobbot` y **copia la clave**
   (empieza por `sk-ant-`). Solo se muestra una vez → pégala en tu nota.

## Paso 2 · WhatsApp con Twilio — 10 min

1. Entra en **https://www.twilio.com/try-twilio** y crea una cuenta gratuita
   (te pedirá verificar tu número de móvil).
2. En la página principal de la consola, en **Account Info**, copia en tu nota:
   - **Account SID** (empieza por `AC`)
   - **Auth Token** (pulsa *Show* para verlo)
3. Ve a **Messaging → Try it out → Send a WhatsApp message**.
4. Verás un código del tipo `join palabra-palabra`. **Desde tu móvil**, envía ese mensaje
   exacto por WhatsApp al número **+1 415 523 8886**. Te responderá confirmando la conexión.
5. Deja esta pestaña abierta: volverás en el paso 6.

## Paso 3 · Crear el bot en Railway — 5 min

1. Entra en **https://railway.com** y pulsa **Login → GitHub** (usa tu cuenta de GitHub).
2. Pulsa **New Project → Deploy from GitHub repo**.
3. Si no aparece tu repositorio, pulsa **Configure GitHub App** y dale acceso a **Testy**.
4. Elige **Testy**. Railway empezará a instalarlo solo (tarda 1–2 minutos).
   *Es normal que al principio aparezcan errores de "faltan variables": los arreglamos ahora.*

## Paso 4 · Dirección pública y disco permanente — 3 min

Toca la caja del servicio (**Testy**) para abrir su panel.

**Dirección pública:**
1. Ve a **Settings → Networking → Generate Domain**.
2. Si te pregunta el puerto, escribe **8080**.
3. Aparecerá una dirección como `testy-production-xxxx.up.railway.app` → cópiala en tu nota.

**Disco permanente** (para que no te repita ofertas cuando el bot se reinicie):
1. Vuelve al lienzo del proyecto y pulsa **+ Create** (o **Create**) → **Volume**.
2. Conéctalo al servicio **Testy** y como *Mount path* escribe **`/data`**.

## Paso 5 · Tus claves y tu CV — 5 min

En el panel del servicio, ve a la pestaña **Variables**.

1. Pulsa **Raw Editor** y pega esto, **cambiando los valores por los tuyos**:

   ```
   ANTHROPIC_API_KEY=sk-ant-...
   TWILIO_ACCOUNT_SID=AC...
   TWILIO_AUTH_TOKEN=...
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   MI_WHATSAPP=whatsapp:+1XXXXXXXXXX
   PORT=8080
   ```

   - En `MI_WHATSAPP` va **tu** número con `+1` y sin espacios ni guiones,
     por ejemplo `whatsapp:+13055550100`. Debe ser el mismo móvil del paso 2.
   - Pulsa **Update Variables**.

2. Ahora pulsa **+ New Variable**:
   - Nombre: **`CV_TEXTO`**
   - Valor: **pega tu CV completo en texto** (mejor en inglés, con tus idiomas y logros con números:
     CSAT, tickets al día, tamaño del equipo, puntuaciones de calidad…).
   - Guarda.

3. Railway te pedirá **Deploy** para aplicar los cambios → pulsa **Deploy**.

## Paso 6 · Conectar Twilio con el bot — 2 min

1. Vuelve a Twilio → **Messaging → Try it out → Send a WhatsApp message**
   → pestaña **Sandbox settings**.
2. En **When a message comes in** pega tu dirección de Railway **añadiendo `/whatsapp`** al final:

   ```
   https://testy-production-xxxx.up.railway.app/whatsapp
   ```

3. Método: **POST**. Pulsa **Save**.

## Paso 7 · ¡Probar! 🎉

Desde tu móvil, escríbele por WhatsApp al +1 415 523 8886:

- `ayuda` → te muestra las órdenes.
- `buscar` → en un minuto te llegan las ofertas.
- `carta 3` → te escribe una carta para la oferta 3.
- `cv 3` → te dice cuánto encajas y cómo adaptar tu CV.

Además, el bot buscará solo cada 6 horas y te avisará de las ofertas nuevas.

---

## Si algo no funciona

Abre el servicio en Railway → **Deployments → View Logs**. Al arrancar, el bot escribe:

- `⚠️ Faltan variables: ...` → revisa el paso 5 (nombre exacto de cada variable).
- `⚠️ No encuentro tu CV` → falta la variable `CV_TEXTO`.
- `URL para Twilio: https://.../whatsapp` → esa es exactamente la dirección del paso 6.

| Problema | Solución |
|---|---|
| El bot no contesta | Revisa la dirección del paso 6 (debe acabar en `/whatsapp`, método POST). |
| Twilio dice que no estás conectado | El sandbox caduca a los 3 días sin mensajes: vuelve a enviar `join palabra-palabra`. |
| Contesta a otros pero no a ti | `MI_WHATSAPP` debe coincidir exactamente con tu número (con `+1`). |
| Te llegan ofertas repetidas tras reiniciar | Falta el disco permanente (paso 4) con *Mount path* `/data`. |

## Cambiar lo que busca

Los filtros están en el archivo **`config.example.yaml`** de tu repositorio de GitHub.
Puedes editarlo desde el iPad: abre el archivo en github.com, pulsa el lápiz ✏️, cámbialo y
pulsa **Commit changes**. Railway actualizará el bot solo en un par de minutos.
(O pídeselo a Claude Code: "añade la palabra clave X".)

## Costes aproximados

- **Railway:** plan Hobby, unos 5 USD al mes (hay periodo de prueba). Este bot gasta muy poco.
- **Twilio:** el sandbox es gratis para probar; cada mensaje cuesta céntimos de su saldo de prueba.
- **Claude:** pagas por uso; cada carta o revisión de CV cuesta unos pocos céntimos.

Consulta los precios actuales en la web de cada servicio.

## Para uso permanente (opcional, más adelante)

El sandbox de Twilio está pensado para pruebas. Si el bot te resulta útil a largo plazo,
en Twilio puedes registrar un número propio de **WhatsApp Business** (requiere aprobación de
Meta); luego solo cambias `TWILIO_WHATSAPP_FROM` en Railway.
