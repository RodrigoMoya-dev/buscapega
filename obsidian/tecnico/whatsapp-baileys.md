# Servicio WhatsApp — Baileys

**Tecnología:** [Baileys](https://github.com/whiskeysockets/baileys) (librería WhatsApp Web para Node.js)  
**Directorio:** `docker/whatsapp/`  
**Puerto:** 3001  
**Contenedor:** `wunen_whatsapp`

---

## ¿Qué es?

Servicio HTTP liviano que mantiene una conexión permanente con WhatsApp Web mediante el protocolo oficial de WhatsApp Web (no una API oficial). Expone endpoints REST para enviar mensajes desde otros servicios de Wunen.

**Uso actual:** Notificaciones automáticas de postulaciones en FindJobIT.

---

## Endpoints

### `GET /health`
Verifica el estado de la conexión.

```json
{ "status": "ok", "connection": "connected", "service": "whatsapp" }
```

Estados posibles de `connection`: `connected`, `connecting`, `disconnected`, `waiting_pairing`, `logged_out`

---

### `POST /send`
Envía un mensaje de texto.

**Body:**
```json
{
  "message": "Texto del mensaje",
  "to": "56912345678"    // opcional — usa DEFAULT_PHONE si se omite
}
```

**Respuesta exitosa:**
```json
{ "ok": true, "to": "56912345678" }
```

---

### `POST /send-bulk`
Envía múltiples mensajes (con pausa de 500ms entre cada uno).

**Body:**
```json
[
  { "message": "Mensaje 1" },
  { "message": "Mensaje 2", "to": "56912345678" }
]
```

---

## Primer arranque — Vincular número

Al levantar el servicio por primera vez, Baileys solicitará un **código de pairing** (no QR):

```bash
# Ver el código en los logs
cd ~/docker/wunen && docker compose logs -f whatsapp
```

Buscar la salida:
```
╔════════════════════════════════════════╗
║   CÓDIGO DE VINCULACIÓN WHATSAPP       ║
║   Código: XXXX-XXXX                    ║
╠════════════════════════════════════════╣
║  1. Abre WhatsApp en tu teléfono       ║
║  2. Dispositivos vinculados             ║
║  3. Vincular un dispositivo             ║
║  4. Ingresa el código de 8 dígitos     ║
╚════════════════════════════════════════╝
```

Pasos en el teléfono:
1. WhatsApp → ⋮ → Dispositivos vinculados
2. Vincular un dispositivo
3. Toca "Vincular con número de teléfono"
4. Ingresar el código de 8 dígitos mostrado en los logs

El estado de autenticación se guarda en el volumen Docker `whatsapp_auth` y persiste entre reinicios.

---

## Reconexión automática

Si la conexión se corta (pérdida de red, reinicio del servidor), Baileys reconecta automáticamente en 5 segundos.

Si la sesión queda inválida (cierre manual desde el teléfono), el servicio mostrará `"logged_out"` y habrá que repetir el proceso de pairing:

```bash
# Borrar el estado de auth y reiniciar
docker volume rm wunen_whatsapp_auth
cd ~/docker/wunen && docker compose up -d whatsapp
```

---

## Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `WHATSAPP_DEFAULT_PHONE` | `56912345678` | Número destino por defecto (sin +) |
| `WHATSAPP_PAIRING_PHONE` | `56912345678` | Número a vincular (sin +) |

En `~/docker/wunen/.env`:
```env
WHATSAPP_DEFAULT_PHONE=56912345678
WHATSAPP_PAIRING_PHONE=56912345678
```

---

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `docker/whatsapp/server.js` | Servidor HTTP + lógica Baileys |
| `docker/whatsapp/package.json` | Dependencias Node.js |
| `docker/whatsapp/Dockerfile` | Imagen Docker |

---

## Comandos útiles

```bash
# Levantar sólo el servicio WhatsApp
cd ~/docker/wunen && docker compose up -d whatsapp

# Ver logs en tiempo real (para ver el código de pairing)
docker compose logs -f whatsapp

# Probar envío de mensaje
curl -X POST http://localhost:3001/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola desde Wunen! 🤖"}'

# Ver estado de conexión
curl http://localhost:3001/health
```

---

## Integración desde Python (scraper)

```python
import httpx

def send_whatsapp(message: str):
    httpx.post(
        "http://whatsapp:3001/send",
        json={"message": message},
        timeout=10.0
    )
```

---

## Notas importantes

- Baileys usa el protocolo de WhatsApp Web, **no la API oficial de WhatsApp Business**
- Un número sólo puede estar conectado en un dispositivo web a la vez
- Si el teléfono no tiene internet, los mensajes se pueden perder
- El servicio es para uso **personal** — no para envío masivo
