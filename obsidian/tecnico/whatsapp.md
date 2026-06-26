# Servicio WhatsApp — whatsapp-web.js

**Tecnología:** [whatsapp-web.js](https://wwebjs.dev/) (^1.26.0, sobre Chromium/Puppeteer)
**Directorio:** `docker/whatsapp/`
**Puerto:** 3001
**Contenedor:** `wunen_whatsapp`

> **Corrección 24/06/2026:** este servicio **no usa Baileys** (el doc anterior `whatsapp-baileys.md`
> estaba desactualizado). Usa `whatsapp-web.js`. Se renombró el archivo a `whatsapp.md`.
>
> **Actualización 26/06/2026:** además del QR, ahora soporta vinculación por **código de pairing**
> (`requestPairingCode`) vía `POST /pair`, alternativa cuando el QR falla con "No se pueden vincular
> dispositivos nuevos en este momento".

---

## ¿Qué es?

Servicio HTTP liviano que mantiene una conexión permanente con WhatsApp Web (protocolo de WhatsApp
Web, no la API oficial de Business). Expone endpoints REST para enviar mensajes desde otros servicios
de Wunen.

**Uso actual:** Notificaciones automáticas de postulaciones (auto-apply) vía webhook n8n → WhatsApp.

---

## Endpoints

### `GET /health`
Verifica el estado de la conexión.

```json
{ "status": "ok", "connection": "connected", "reconnect_attempts": 0, "service": "whatsapp" }
```

- `status`: `ok` solo cuando está conectado; `unavailable` en cualquier otro caso.
- El backend (`/api/settings/test-whatsapp`) consulta primero este endpoint antes de enviar, para dar
  un mensaje claro si el dispositivo no está vinculado (ver `obsidian/web/configuracion.md`).

### `GET /qr`
Devuelve una página HTML con el **código QR** actual (autorefresca). Se usa desde
`./vincular-whatsapp.sh`. Si ya está conectado, muestra un aviso en vez del QR.

### `POST /pair`
Alternativa al QR: genera un **código de vinculación** de 8 caracteres (`requestPairingCode`).

**Body:** `{ "phone": "56912345678" }` (número con código de país, solo dígitos).
**Éxito:** `{ "ok": true, "code": "ABCD-1234", "phone": "56912345678" }`.
**Ya conectado:** **409**. **Cliente no listo:** **503**. **Falta phone:** **400**.

En el teléfono: WhatsApp → ⋮ → Dispositivos vinculados → Vincular un dispositivo → **Vincular con
número de teléfono** → ingresar el código. Útil si el QR falla con "No se pueden vincular
dispositivos nuevos en este momento".

### `POST /send`
Envía un mensaje de texto.

**Body:** `{ "message": "Texto", "to": "56912345678" }` (`to` opcional → usa `DEFAULT_PHONE`).
**Éxito:** `{ "ok": true, "to": "56912345678" }`.
**No conectado:** responde **503** con `{ "ok": false, "error": "WhatsApp no está conectado", "status": <estado> }`.

### `POST /send-bulk`
Envía múltiples mensajes (pausa entre cada uno). Body: arreglo de `{ message, to? }`.

---

## Vincular número (QR o código)

```bash
# Desde la raíz del proyecto (curl al servicio)
./vincular-whatsapp.sh [host] [port]              # QR
./vincular-whatsapp.sh [host] [port] <telefono>   # código de vinculación (sin QR)
```

O manualmente:
1. `docker compose logs -f whatsapp` y escanear el QR del terminal, **o** abrir `http://<host>:3001/qr`.
2. En el teléfono: WhatsApp → ⋮ → **Dispositivos vinculados** → Vincular un dispositivo → escanear.
3. Alternativa sin QR: `curl -X POST http://<host>:3001/pair -H 'Content-Type: application/json' -d '{"phone":"56912345678"}'` y usar "Vincular con número de teléfono".

El estado de autenticación se guarda en `AUTH_DIR` (`/app/auth`, volumen Docker) y persiste entre
reinicios.

---

## Reconexión

El cliente reconecta automáticamente; `reconnect_attempts` en `/health` refleja los intentos. Si la
sesión queda inválida (cierre manual desde el teléfono), borrar el volumen de auth y reescanear el QR.

---

## Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `PORT` | `3001` | Puerto HTTP del servicio |
| `AUTH_DIR` | `/app/auth` | Carpeta de estado de autenticación (volumen) |
| `DEFAULT_PHONE` | `56912345678` | Número destino por defecto (sin +) |
| `CHROME_PATH` | `/usr/bin/chromium` | Ejecutable de Chromium para Puppeteer |

---

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `docker/whatsapp/server.js` | Servidor HTTP + cliente whatsapp-web.js |
| `docker/whatsapp/package.json` | Dependencias Node.js (whatsapp-web.js, qrcode) |
| `docker/whatsapp/Dockerfile` | Imagen Docker (incluye Chromium) |

---

## Integración desde Python (scraper/backend)

```python
import httpx

def send_whatsapp(message: str):
    httpx.post("http://whatsapp:3001/send", json={"message": message}, timeout=10.0)
```

---

## Notas

- Protocolo de WhatsApp Web, **no** la API oficial de WhatsApp Business.
- Un número solo puede estar en un dispositivo web a la vez.
- Servicio para uso **personal**, no para envío masivo.
