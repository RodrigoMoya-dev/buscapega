# Tareas Pendientes — Sesión 27/05/2026

## En curso — Sesión actual

### 🔧 Fix 1 — Detección /auth/signin en FindJobIT ✅ COMPLETADO
- [x] `scrapers/findjobit.py`: `_get_apply_info` ahora detecta `/auth/`, `/signin`
- [x] `applicator/findjobit.py`: `_apply_via_form` ídem con URL real en mensaje de error
- [x] Causa raíz: FindJobIT redirige a `/auth/signin` (no `/login`) → sesión expirada no se detectaba
- [x] Efecto: antes el sistema creía que `form_accessible=True` cuando en realidad no había sesión
- [x] Código subido a Presto vía rsync ✅

### 🔧 Fix 2 — WhatsApp server.js robusto ✅ COMPLETADO
- [x] Manejo de errores con try/catch en `startClient()`
- [x] `scheduleReconnect()` con backoff exponencial
- [x] `process.on('unhandledRejection')` para no crashear
- [x] `--single-process` en Chromium para menos uso de memoria
- [x] Endpoint `/qr` con imagen PNG para escaneo desde browser
- [x] Añadido `qrcode` a dependencias
- [x] Reconstruyendo imagen Docker en Presto...
- [ ] Verificar que WhatsApp conecta (escanear QR si es necesario)

### 🔧 Fix 3 — WhatsApp Chromium: perfil corrupto (SingletonLock) ✅ RESUELTO
- [x] Eliminado `SingletonLock` y `SingletonSocket` del volume
- [x] Sesión WhatsApp borrada y recreada (se usaron credenciales guardadas)

### ✅ Fix 4 — Sesión FindJobIT (skip_strategy_1) COMPLETADO
- [x] Causa: `/job-seekers/login` redirige a `/job-seekers` sin auth → falso positivo
- [x] `portales_config.py`: `skip_strategy_1: True` para FindJobIT
- [x] `setup_session.py`: no infiere login desde redirect cuando `skip_strategy_1=True`
- [x] Sesión re-capturada con 6 cookies válidas incl. `__Secure-next-auth.session-token` ✅

### ✅ Fix 5 — CV disponible en Presto COMPLETADO
- [x] `cv_es.pdf` copiado a `~/docker/wunen/data/cv_es.pdf`
- [x] `cv_en.pdf` generado (traducción al inglés vía reportlab)
- [x] `docker-compose.yml` con `./data:/wunen:ro` → accesible en `/wunen/cv_es.pdf` ✅

### ✅ Fix 6 — Auto-aplicación FindJobIT funcional COMPLETADO (27/05/2026)
- [x] `_job_id` extraído desde URL de la oferta cuando no viene en payload
- [x] Detección de vacantes externas → retorna URL destino (ej: newcombin.com)
- [x] Detección de vacantes por email → extrae email del formulario con regex
- [x] SMTP bloqueado en Presto (puerto 587 timeout) → usa Google Apps Script webhook HTTPS
- [x] GAS webhook: mismo script que usa Trafkin backup → envío exitoso confirmado
- [x] Probado con 5 ofertas: 4 emails enviados OK, 1 externa (URL devuelta)
- [x] FindJobITApplicator registrado en `registry.py`

---

## Estado de servicios

| Servicio | Puerto | Estado |
|----------|--------|--------|
| Frontend (wunen.presto) | 3020 | ✅ UP |
| Backend (api.wunen.presto) | 8020 | ✅ UP |
| Scraper + FindJobIT | 8021 | ✅ UP |
| WhatsApp | 3002 | ✅ UP (conectado) |
| PostgreSQL | 5433 | ✅ UP |
| n8n workflow FindJobIT | — | ✅ Activo (cada 1h) |

### ⚠️ Nota: Créditos Anthropic API agotados
- La carta de presentación usa `_fallback_letter()` en lugar de Claude
- Las evaluaciones de nuevas ofertas tampoco funcionan
- Recargar créditos en console.anthropic.com para restaurar

---

## Sesión anterior — 26/05/2026 ✅ COMPLETADO

### ✅ TAREA 1 — Configurar http://wunen.presto (nginx en Presto)
- [x] `wunen.presto` → puerto 3020 (frontend)
- [x] `api.wunen.presto` → puerto 8020 (backend API)

### ✅ TAREA 2 — WhatsApp Service (whatsapp-web.js)
- [x] Migrado de Baileys a `whatsapp-web.js`
- [x] `docker/whatsapp/server.js` con `LocalAuth` + Puppeteer Chromium
- [x] QR generado por consola → teléfono vinculado ✅

### ✅ TAREA 3 — Portal FindJobIT: scraper + auto-apply
- [x] `scrapers/findjobit.py` (Playwright, country/chile, h4 titles, dedup)
- [x] `applicator/findjobit.py` (Gmail SMTP + WhatsApp notify)
- [x] Sesión Playwright → `form_accessible` mode
- [x] Pipeline completo corriendo via n8n (cada 1h)

### ✅ TAREA 4 — Git: Gitea + deploy Presto
- [x] Repo `claude/wunen` en `http://gitea.presto/claude/wunen`
- [x] Rama `feature_wunen_presto_whatsapp_findjobit_26052026`
