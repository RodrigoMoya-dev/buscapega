# Vista: Configuración

**Ruta web:** `/settings`
**Archivo:** `docker/frontend/app/settings/page.tsx`
**API:** `GET/POST /api/settings`, `POST /api/settings/test-whatsapp`, `POST /api/settings/test-email` (`docker/backend/app/routers/settings.py`)

---

## ¿Qué es?

Ajustes generales: nombre del usuario (saludo del menú), número de WhatsApp para notificaciones,
y correos de postulación. Persisten en `documentos/settings.json`.

## Origen de los datos

`settings.json` lo **crea el instalador** (`install.sh`) con el nombre, teléfono y correo
ingresados. La vista de Configuración lee y escribe ese mismo archivo, por lo que el teléfono y
correo de postulaciones provienen del instalador y pueden editarse luego aquí o directamente en
`documentos/settings.json`.

Campos: `user_name`, `whatsapp_phone`, `notification_email`, `reply_email`.

## Saludo "Hola, {nombre}"

El componente `components/NavGreeting.tsx` lee `settings.user_name` y muestra "Hola, Rodrigo"
en el menú superior. Si no aparece, es porque `settings.json` no tiene `user_name` o se está
sirviendo un build viejo.

## WhatsApp (whatsapp-web.js) y Gmail

- **WhatsApp:** no se configura en el instalador (requiere escanear un QR). Usar
  `./vincular-whatsapp.sh` (o `./vincular-whatsapp.sh <host> <port> <telefono>` para vincular por
  código sin QR).
- **Gmail:** el correo y la contraseña de aplicación se piden en el instalador y se guardan en
  `docker/.env`. Para cambiarlos luego: `./setup-gmail.sh`.
- La API key de Anthropic **es opcional**: la web no la pide. La evaluación funciona con scoring
  por keywords o con Claude Code.

## Mejoras 24/06/2026

### Saludo se refresca al guardar el nombre (T9)
Antes había que recargar la página para que el saludo "Hola, {nombre}" del menú se actualizara.
Ahora, al guardar, la vista dispara el evento `window` `wunen:settings-updated` con el nuevo
`user_name`; `components/NavGreeting.tsx` lo escucha y refresca el saludo **sin recargar**.

### Mensaje claro cuando WhatsApp no está vinculado (T10)
`POST /api/settings/test-whatsapp` ahora consulta primero `GET {whatsapp}/health`:
- Si el servicio no responde → "El servicio de WhatsApp no responde…".
- Si `status != ok` (no vinculado) → "WhatsApp no está vinculado (estado: …). Escanea el QR con
  './whatsapp-qr.sh'…".
- Solo si está activo envía el mensaje. Un 503 al enviar también devuelve un mensaje de vinculación
  con el detalle del servicio (antes solo decía "WhatsApp respondió con error 503").

  También se corrigió el cuerpo enviado a `/send`: usa `to` (el servicio ignoraba `phone`).

### Checkbox reply-to (T11)
El campo "Correo de respuesta (reply-to)" tiene un checkbox **"Usar el mismo correo de envío"**.
Al activarlo, el reply-to replica `notification_email` (campo deshabilitado) y se persiste así al
guardar. Se inicia marcado si el reply-to está vacío o coincide con el correo de envío.

## Mejoras 26/06/2026 — validar correo de postulaciones (T6)

La sección "Correo de postulaciones" tiene un botón **"Enviar correo de prueba"** que valida que el
correo funcione. Flujo:
- La vista guarda primero el correo del formulario y llama `POST /api/settings/test-email`.
- El backend lee `notification_email` de `settings.json` y delega en el scraper
  (`POST {scraper}/test-email`), que tiene las credenciales de envío.
- El scraper reutiliza el mecanismo real de envío (`findjobit._send_email`: webhook de Google Apps
  Script con respaldo de Gmail SMTP) y manda un correo de prueba al "Correo de envío".
- El resultado (✓ enviado / mensaje de error) se muestra junto al botón.

## Cambios sesión 17/06/2026

- Documentado que teléfono/correo provienen del instalador (settings.json) y editables aquí.
- Scripts de configuración en la raíz: `vincular-whatsapp.sh` (WhatsApp, antes `whatsapp-qr.sh`) y
  `setup-gmail.sh` (Gmail).
