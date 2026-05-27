# Tareas Pendientes - Sesión 26/05/2026

## Plan de trabajo

### ✅ TAREA 1 — Configurar http://wunen.presto (nginx en Presto)
- [x] Agregar bloque en `/etc/nginx/conf.d/presto-proxy.conf`:
  - `wunen.presto` → puerto 3020 (frontend)
  - `api.wunen.presto` → puerto 8020 (backend API)
- [x] Recargar nginx

---

### 🔲 TAREA 2 — Baileys WhatsApp Service
- [x] Crear `docker/whatsapp/` con:
  - `package.json` — @whiskeysockets/baileys + express
  - `server.js` — HTTP API para enviar mensajes
  - `Dockerfile`
- [x] Agregar servicio `whatsapp` en `docker-compose.yml`
- [ ] **Pairing manual requerido**: al levantar el servicio por primera vez,
  leer los logs del contenedor `wunen_whatsapp` — mostrará un código de 8 dígitos.
  Abrir WhatsApp → Dispositivos vinculados → Vincular → Ingresar código.
  ```bash
  cd ~/docker/wunen && docker compose logs -f whatsapp
  ```
  El estado de autenticación se persiste en el volumen `whatsapp_auth`.

---

### 🔲 TAREA 3 — Portal FindJobIT: scraper + aplicador vía email
- [x] Crear `docker/scraper/scrapers/findjobit.py` (Playwright, country/chile, solo remoto)
- [x] Crear `docker/scraper/applicator/findjobit.py` (envío por Gmail SMTP)
- [x] Registrar en `applicator/registry.py`
- [x] Agregar ruta `POST /run/findjobit` en `scraper/main.py`
- [x] Agregar vars de entorno Gmail en `docker-compose.yml` y `.env.example`
- [x] Crear workflow n8n: cron horario → POST /run/findjobit (en presto)
- [x] Documentar portal en `obsidian/tecnico/portales/findjobit.md`

#### Paso a paso para conectar Gmail con la aplicación
1. Ir a https://myaccount.google.com/security
2. Activar "Verificación en 2 pasos" si no está activa
3. Ir a https://myaccount.google.com/apppasswords
4. Crear una contraseña de aplicación: seleccionar "Otro (nombre personalizado)" → escribir "Wunen"
5. Copiar la contraseña de 16 caracteres generada (formato: xxxx xxxx xxxx xxxx)
6. En `~/docker/wunen/.env` (en presto), agregar:
   ```env
   GMAIL_USER=correo@ejemplo.com
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```
7. Reiniciar el scraper: `cd ~/docker/wunen && docker compose restart scraper`

---

### 🔲 TAREA 4 — Git: crear repo en Gitea y subir cambios
- [x] Crear repo `moya.dev/wunen` en Gitea (http://gitea.presto)
- [x] Init repo local y hacer push a Gitea
- [x] Crear rama `feature_wunen_presto_whatsapp_findjobit_26052026`
- [x] Commits por tarea con descripción de cambios
- [ ] Deploy en presto (git pull + docker compose up --build)

---

## Tareas originales

* ~~Lo primero es armar http://wunen.presto para poder utilizar la aplicación ahí.~~
* Necesito que configures Baileys para el envío de mensajes de whatsapp desde la aplicación hacia un telefono personal. El numero de envío y el de recepción son el +56912345678.  
* Necesito que me ayudes a automatizar, usando esta plataforma, el proceso de postulación a trabajos a través del portal findjobit.com.
