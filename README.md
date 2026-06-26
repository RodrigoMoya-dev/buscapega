# Wunen

Sistema personal de automatización de búsqueda de empleo. Scraping de ofertas, evaluación con IA, interfaz de revisión y postulación automática en múltiples portales.

---

## Instalación

```bash
git clone http://gitea.presto/moya.dev/wunen.git
cd wunen
bash install.sh
```

El instalador:
1. Verifica Docker y dependencias
2. Solicita API Key de Anthropic, teléfono WhatsApp y correo Gmail
3. Genera `docker/.env` y `documentos/settings.json`
4. Construye y levanta todos los servicios Docker
5. (Opcional) Configura sesiones de portales para auto-postulación

Una vez terminado, abre **http://localhost:3000** en tu navegador.

---

## Vincular WhatsApp

El servicio WhatsApp usa un código QR para vincular tu número. Hay tres formas de obtenerlo:

### Opción 1 — Script (recomendado)

```bash
# Si Wunen corre en local
bash vincular-whatsapp.sh

# Si Wunen corre en un servidor remoto (ej: presto)
bash vincular-whatsapp.sh presto 3001
```

El script muestra la URL del QR y los pasos a seguir.

### Opción 2 — Navegador

Abre en el navegador la URL del servicio WhatsApp:

```
http://localhost:3001/qr       (si corre en local)
http://presto.local:3001/qr    (si corre en el servidor Presto)
```

La página muestra el QR y se actualiza automáticamente cada 20 segundos.

### Opción 3 — Logs del contenedor

```bash
cd ~/docker/wunen
docker compose logs -f whatsapp
```

Busca el bloque con el QR ASCII en los logs.

### Pasos en el teléfono

1. Abre WhatsApp
2. Toca ⋮ (tres puntos) → **Dispositivos vinculados**
3. Toca **Vincular un dispositivo**
4. Escanea el código QR

> El QR expira en ~20 segundos. Si expira, se genera uno nuevo automáticamente.

### Revincular si se desconecta

Si el número se desvincula (se ve `logged_out` en el estado):

```bash
cd ~/docker/wunen
docker volume rm wunen_whatsapp_auth
docker compose up -d whatsapp
# Espera ~30 segundos y repite el proceso de vinculación
bash ~/wunen/vincular-whatsapp.sh presto 3001
```

---

## Comandos útiles

```bash
# Ver logs
cd ~/docker/wunen && docker compose logs -f backend
cd ~/docker/wunen && docker compose logs -f whatsapp

# Reiniciar un servicio
cd ~/docker/wunen && docker compose restart backend

# Detener todo
cd ~/docker/wunen && docker compose down

# Configurar sesiones de portales
./setup-sessions.sh --lista
```

---

## Estructura

| Servicio | Puerto | Descripción |
|---------|--------|-------------|
| Frontend | 3000 | Interfaz web (Next.js) |
| Backend | 8000 | API principal (FastAPI) |
| Scraper | 8001 | Scrapers + aplicadores (Playwright) |
| WhatsApp | 3001 | Notificaciones WhatsApp |
| PostgreSQL | 5432 | Base de datos |

Ver `CLAUDE.md` para documentación técnica completa.
