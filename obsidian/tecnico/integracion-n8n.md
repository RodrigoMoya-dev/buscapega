# Integración n8n — Wunen

## Qué se hizo

Se instaló y configuró n8n en el servidor **Presto** como orquestador del sistema Wunen. n8n actúa como el cerebro de la automatización: programa cuándo se buscan ofertas, recibe los resultados de postulación y envía notificaciones por Telegram al usuario.

---

## Servicios en Presto

| Servicio | Puerto | Descripción |
|---|---|---|
| **n8n** | `presto:5678` | Orquestador de flujos (ya estaba instalado) |
| **Backend (FastAPI)** | `presto:8020` | API principal de Wunen |
| **Scraper (Playwright)** | `presto:8021` | Scraping + auto-postulación |
| **Frontend (Next.js)** | `presto:3020` | Bandeja de revisión de ofertas |
| **PostgreSQL** | `presto:5433` | Base de datos |

Todos los servicios de Wunen se gestionan desde:
```
~/docker/wunen/docker-compose.yml
```

---

## Dónde revisar los flujos de n8n

Acceder a la interfaz web de n8n:

```
http://presto:5678
Usuario: rodrigo
Contraseña: moya2024n8n
```

En el menú lateral izquierdo, bajo **Workflows**, aparecen los 3 flujos de Wunen. Haciendo click en cada uno se abre el editor visual donde se pueden ver los nodos, sus conexiones, y el historial de ejecuciones.

---

## Los 3 workflows y cómo están armados

### Workflow 1 — Scraping periódico
**ID:** `5owx5DLVVAnCvvO0` | **Estado:** activo

Corre automáticamente cada 6 horas y busca nuevas ofertas de trabajo.

```
[Cron cada 6h]
    │
    ▼
[HTTP POST → presto:8021/run]         ← dispara todos los scrapers
    │
    ▼
[HTTP GET → presto:8020/offers?status=pendiente]   ← cuenta ofertas nuevas
    │
    ▼
[IF: ¿total > 0?]
    │
    ├─ SÍ → [Telegram: "📋 X ofertas nuevas en bandeja → http://presto:3020"]
    │
    └─ NO → (no hace nada)
```

**Qué ocurre en cada nodo:**
- **Cron**: disparo automático cada 6 horas
- **Disparar scraper**: llama al servicio scraper que ejecuta Playwright y APIs (Remotive, RemoteOK, GetOnBrd, etc.)
- **Obtener pendientes**: consulta cuántas ofertas nuevas quedaron en estado PENDIENTE
- **IF**: solo notifica si hay al menos una oferta nueva (evita spam)
- **Telegram**: envía mensaje con el total y el link a la bandeja

---

### Workflow 2 — Notificación post-postulación
**ID:** `RpAlL4F6pHtFwlpm` | **Estado:** activo

Se activa mediante un **webhook** que llama el backend automáticamente al terminar cada auto-postulación.

```
[Webhook: POST /webhook/wunen-apply-result]
    │
    ▼
[IF: ¿status == "ok"?]
    │
    ├─ SÍ → [Telegram: "✅ Postulación enviada"]
    │          Empresa, portal, cargo, score
    │
    └─ NO → [Telegram: "⚠️ Requiere intervención"]
               Empresa, portal, cargo
               Motivo exacto del fallo
               Hasta qué paso llegó
               Link directo para continuar manualmente
```

**El mensaje de intervención incluye:**
- Motivo preciso (ej: "CAPTCHA detectado en el paso de envío", "Sesión expirada")
- Paso alcanzado (ej: "Carta rellenada, faltó el envío final")
- Link directo a la oferta para completarla manualmente

**URL del webhook** (usada internamente por el backend):
```
http://localhost:5678/webhook/wunen-apply-result
```

---

### Workflow 3 — Resumen diario 9am
**ID:** `PNY4XTPH75oHOR07` | **Estado:** activo

Envía un resumen cada mañana a las 9:00 (hora Santiago, UTC-3).

```
[Cron: 0 9 * * *]
    │
    ▼
[HTTP GET → presto:8020/offers?status=pendiente]
    │
    ▼
[IF: ¿hay pendientes?]
    │
    ├─ SÍ → [Telegram: "🌅 X oferta(s) esperando revisión → link bandeja"]
    │
    └─ NO → [Telegram: "🌅 Bandeja vacía, scraper correrá pronto"]
```

---

## Flujo completo del sistema

```
                    ┌─────────────────────────────────────────────────┐
                    │              PRESTO (servidor)                  │
                    │                                                  │
  [n8n Cron 6h] ───┤──► Scraper ──► evalúa con Claude ──► PostgreSQL │
                    │                                                  │
  [n8n Cron 9am] ──┤──► consulta BD ──► Telegram resumen diario      │
                    │                                                  │
  [Tu Mac]          │                                                  │
    │               │                                                  │
    ├─ setup_session.py ──► cookies ──► rsync ──► /cookies/           │
    │               │                                                  │
    └─ Abre Frontend (presto:3020)                                     │
         │                                                             │
         ├─ [Revisar ofertas PENDIENTES]                               │
         ├─ [Guardar / Descartar]                                      │
         └─ [Auto-postular] ──► Backend ──► Scraper (Playwright)      │
                                    │                                  │
                                    └──► n8n webhook ──► Telegram     │
                                              │                        │
                                    ✅ "Postulación enviada"           │
                                    ⚠️  "Requiere intervención         │
                                         Motivo: CAPTCHA detectado    │
                                         Link: [URL directa]"         │
                    └─────────────────────────────────────────────────┘
```

---

## Bot de Telegram

| Dato | Valor |
|---|---|
| Nombre del bot | @Wunen_bot |
| Chat ID del usuario | `8301524530` |
| Token | guardado en `~/docker/wunen/.env` |

---

## API Key de n8n

La API key generada para automatización está guardada en la base de datos SQLite de n8n. Si se necesita hacer llamadas a la API de n8n desde scripts externos:

```
X-N8N-API-KEY: n8n_api_407ff1bfdb4df4d649f2e05581039805ac1dcd053d06c9f3
```

Ejemplo para listar workflows:
```bash
curl http://presto:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: n8n_api_407ff1bfdb4df4d649f2e05581039805ac1dcd053d06c9f3"
```

---

## Variables de entorno relevantes

En `~/docker/wunen/.env`:

```env
ANTHROPIC_API_KEY=...          # Claude API para evaluación y cartas
TELEGRAM_BOT_TOKEN=...         # Token del bot @Wunen_bot
TELEGRAM_CHAT_ID=8301524530    # Tu chat ID personal
NEXT_PUBLIC_API_URL=http://presto:8020
```

En el scraper (docker-compose.yml):
```env
N8N_WEBHOOK_URL=http://localhost:5678/webhook/wunen-apply-result
```

---

## Gestión de sesiones de portales

Las sesiones de Google OAuth para los portales se guardan en:
- **Local (Mac):** `wunen/setup/cookies/<portal>_session.json`
- **Presto:** `~/docker/wunen/cookies/<portal>_session.json`

Para renovar o crear una sesión:
```bash
cd "/Users/rodrigo/Proyectos/Moya.dev/Proyectos internos/wunen/setup"
python setup_session.py getonbrd       # GetOnBrd
python setup_session.py tecnoempleo    # Tecnoempleo
python setup_session.py remotelatinos  # RemoteLatinos
python setup_session.py chiletrabajos  # ChileTrabajos
python setup_session.py chumiit        # Chumi-IT

python setup_session.py --lista        # Ver estado de todas las sesiones
```

El script abre Chromium en tu pantalla, completas el login con Google manualmente, y las cookies se sincronizan automáticamente a Presto.

---

## Comandos útiles en Presto

```bash
# Ver estado de los contenedores
cd ~/docker/wunen && docker compose ps

# Ver logs en tiempo real
docker logs wunen_backend -f
docker logs wunen_scraper -f

# Reiniciar un servicio
docker compose restart backend
docker compose restart scraper

# Disparar scraping manualmente
curl -X POST http://localhost:8021/run

# Ver ofertas pendientes
curl http://localhost:8020/api/offers?status=pendiente | python3 -m json.tool

# Probar webhook de postulación
curl -X POST http://localhost:5678/webhook/wunen-apply-result \
  -H "Content-Type: application/json" \
  -d '{"body": {"status":"parcial","empresa":"Test","portal":"GetOnBrd",
       "titulo":"Dev PHP","motivo":"CAPTCHA detectado","paso_alcanzado":"Formulario rellenado",
       "url_continuar":"https://getonbrd.com/test","score":85}}'
```
