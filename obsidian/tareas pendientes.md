# Tareas Pendientes — Sesión 26/05/2026

## Estado final ✅ COMPLETADO

### ✅ TAREA 1 — Configurar http://wunen.presto (nginx en Presto)
- [x] `wunen.presto` → puerto 3020 (frontend)
- [x] `api.wunen.presto` → puerto 8020 (backend API)
- [x] Nginx recargado → **FUNCIONANDO** ✅

---

### ✅ TAREA 2 — WhatsApp Service (whatsapp-web.js)
- [x] Migrado de Baileys a `whatsapp-web.js` (compatible con WA Business)
- [x] `docker/whatsapp/server.js` con `LocalAuth` + Puppeteer Chromium
- [x] Contenedor `wunen_whatsapp` corriendo en presto (puerto 3002)
- [x] QR generado por consola → teléfono vinculado ✅
- [x] Estado: **CONECTADO** ✅

---

### ✅ TAREA 3 — Portal FindJobIT: scraper + notificación WhatsApp
- [x] `docker/scraper/scrapers/findjobit.py` (Playwright, country/chile, h4 titles, dedup)
- [x] `docker/scraper/applicator/findjobit.py` (Gmail SMTP + WhatsApp notify)
- [x] Ruta `POST /run/findjobit` en `scraper/main.py`
- [x] Gmail App Password configurado en `.env`
- [x] Workflow n8n `TcDb0BaQJuuJRiKo` — cron horario → **ACTIVO** ✅
- [x] Prueba exitosa: 10 ofertas únicas extraídas con títulos correctos
- [x] Notificaciones WhatsApp enviadas para score ≥ 50:
  - "Dev Assistant" (score 51) → 👀 alerta enviada ✅
  - "Fullstack Java React Sr" (score 60) → 👀 alerta enviada ✅
- [x] Documentado en `obsidian/tecnico/portales/findjobit.md`

**Nota:** FindJobIT no expone emails sin login → apply se hace manualmente desde la UI.  
El flujo para offers con score ≥ 50 es: WhatsApp alert → revisar en wunen.presto → postular manualmente.

---

### ✅ TAREA 4 — Git: Gitea + deploy Presto
- [x] Repo `claude/wunen` en `http://gitea.presto/claude/wunen`
- [x] Rama `feature_wunen_presto_whatsapp_findjobit_26052026`
- [x] Deploy en presto completado ✅

---

## Estado final de servicios en Presto

| Servicio | Puerto | Estado |
|----------|--------|--------|
| Frontend (wunen.presto) | 3020 | ✅ UP |
| Backend (api.wunen.presto) | 8020 | ✅ UP |
| Scraper + FindJobIT | 8021 | ✅ UP |
| WhatsApp (whatsapp-web.js) | 3002 | ✅ CONECTADO |
| PostgreSQL | 5433 | ✅ UP |
| n8n workflow FindJobIT | — | ✅ Activo (cada 1h) |

---

## Tareas originales completadas

* ~~Lo primero es armar http://wunen.presto para poder utilizar la aplicación ahí.~~ ✅
* ~~Necesito que configures Baileys para el envío de mensajes de whatsapp desde la aplicación hacia un telefono personal.~~ ✅ (whatsapp-web.js, conectado)
* ~~Necesito que me ayudes a automatizar el proceso de postulación a trabajos a través del portal findjobit.com.~~ ✅ (scraper + n8n + WhatsApp alerts)
* ~~Configura la aplicación para el envío por gmail. La key de gmail para la app Wunen es : crcv hcvc iajm cvkw~~ ✅
* ~~No entra el código de whatsapp. ¿Puedes generar el código QR via consola?~~ ✅
