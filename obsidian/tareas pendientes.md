# Tareas Pendientes — Sesión 26/05/2026

## Plan de trabajo

### ✅ TAREA 1 — Configurar http://wunen.presto (nginx en Presto)
- [x] Agregar bloque en `/etc/nginx/conf.d/presto-proxy.conf`:
  - `wunen.presto` → puerto 3020 (frontend)
  - `api.wunen.presto` → puerto 8020 (backend API)
- [x] Recargar nginx → **FUNCIONANDO** ✅

---

### ✅ TAREA 2 — Baileys WhatsApp Service
- [x] Crear `docker/whatsapp/` con:
  - `package.json` — @whiskeysockets/baileys + express
  - `server.js` — HTTP API para enviar mensajes (port 3001)
  - `Dockerfile`
- [x] Agregar servicio `whatsapp` en `docker-compose.yml`
- [x] Build exitoso y contenedor `wunen_whatsapp` corriendo en presto (puerto 3002)

### ⚠️ ACCIÓN MANUAL REQUERIDA — Vincular WhatsApp
El servicio está corriendo pero necesita que vincules tu teléfono:

```bash
# Ver el código de pairing (en presto)
docker logs wunen_whatsapp --tail=20

# Código actual: ACN4-6SR7 (puede regenerarse si expira)
```

**Pasos:**
1. WhatsApp en tu teléfono → ⋮ (tres puntos) → Dispositivos vinculados
2. → Vincular un dispositivo
3. → "Vincular con número de teléfono" 
4. Ingresar el código de 8 dígitos que aparece en los logs

Tras vincular, el estado cambia a `connected` y persiste en el volumen `whatsapp_auth`.

---

### ✅ TAREA 3 — Portal FindJobIT: scraper + aplicador vía email
- [x] Crear `docker/scraper/scrapers/findjobit.py` (Playwright, country/chile)
- [x] Crear `docker/scraper/applicator/findjobit.py` (envío por Gmail SMTP)
- [x] Agregar ruta `POST /run/findjobit` en `scraper/main.py`
- [x] Agregar endpoint `PATCH /{id}/set-status` al backend
- [x] Agregar vars de entorno Gmail en `docker-compose.yml` y `.env.example`
- [x] Crear workflow n8n `TcDb0BaQJuuJRiKo` — cron horario → POST /run/findjobit → **ACTIVO** ✅
- [x] Documentar portal en `obsidian/tecnico/portales/findjobit.md`

### ⚠️ ACCIÓN MANUAL REQUERIDA — Configurar Gmail App Password
```bash
# En presto, editar el archivo .env:
nano ~/docker/wunen/.env
# Buscar GMAIL_APP_PASSWORD= y poner la contraseña de 16 caracteres
```

**Pasos para obtener la App Password:**
1. Ir a https://myaccount.google.com/security
2. Activar "Verificación en 2 pasos" (si no está activa)
3. Ir a https://myaccount.google.com/apppasswords
4. Crear → "Otro (nombre personalizado)" → "Wunen"
5. Copiar los 16 caracteres generados
6. En presto: `nano ~/docker/wunen/.env` → pegar en `GMAIL_APP_PASSWORD=`
7. Reiniciar: `cd ~/docker/wunen && docker compose restart scraper`

---

### ✅ TAREA 4 — Git: crear repo en Gitea y subir cambios
- [x] Crear repo `claude/wunen` en `http://gitea.presto/claude/wunen`
  *(La organización moya.dev no existe en Gitea — se usó el usuario claude)*
- [x] Init repo local y commit inicial en `main` (82 archivos)
- [x] Crear rama `feature_wunen_presto_whatsapp_findjobit_26052026`
- [x] Push a Gitea → http://gitea.presto/claude/wunen
- [x] Deploy en presto completado (rsync + docker compose restart)

---

## Estado final de servicios en Presto

| Servicio | Puerto | Estado |
|----------|--------|--------|
| Frontend (wunen.presto) | 3020 | ✅ UP |
| Backend (api.wunen.presto) | 8020 | ✅ UP |
| Scraper + FindJobIT | 8021 | ✅ UP |
| WhatsApp (Baileys) | 3002 | ⚠️ UP — falta vincular teléfono |
| PostgreSQL | 5433 | ✅ UP |
| n8n workflow FindJobIT | — | ✅ Activo (cada 1h) |

---

## Tareas originales

* ~~Lo primero es armar http://wunen.presto para poder utilizar la aplicación ahí.~~ ✅
* ~~Necesito que configures Baileys para el envío de mensajes de whatsapp desde la aplicación hacia un telefono personal.~~ ✅ (falta vincular el teléfono)
* ~~Necesito que me ayudes a automatizar el proceso de postulación a trabajos a través del portal findjobit.com.~~ ✅ (falta configurar Gmail App Password)
