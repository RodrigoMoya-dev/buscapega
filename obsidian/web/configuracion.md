# Vista: Configuración

**Ruta web:** `/settings`
**Archivo:** `docker/frontend/app/settings/page.tsx`
**API:** `GET/POST /api/settings`, `POST /api/settings/test-whatsapp` (`docker/backend/app/routers/settings.py`)

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

## WhatsApp (Baileys) y Gmail

- **WhatsApp:** no se configura en el instalador (requiere escanear un QR). Usar `./whatsapp-qr.sh`.
- **Gmail:** el correo y la contraseña de aplicación se piden en el instalador y se guardan en
  `docker/.env`. Para cambiarlos luego: `./setup-gmail.sh`.
- La API key de Anthropic **es opcional**: la web no la pide. La evaluación funciona con scoring
  por keywords o con Claude Code.

## Cambios sesión 17/06/2026

- Documentado que teléfono/correo provienen del instalador (settings.json) y editables aquí.
- Scripts de configuración en la raíz: `whatsapp-qr.sh` (WhatsApp) y `setup-gmail.sh` (Gmail).
