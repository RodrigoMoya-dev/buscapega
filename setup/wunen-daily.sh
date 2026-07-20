#!/bin/bash
# =============================================================================
# wunen-daily.sh — Búsqueda y auto-postulación diaria de ofertas laborales
#
# Flujo:
#   1. Esperar que el backend de Buscapega esté listo
#   2. Disparar pipeline completo FindJobIT (scraping + auto-postulación)
#   3. Disparar scraping de otros portales (Remotive, RemoteOK, GetOnBrd, etc.)
#   4. Esperar a que los scrapers terminen
#   5. Auto-postular a todas las ofertas PENDIENTE elegibles
#   6. Notificar por Telegram con resumen
#
# Crontab sugerido (9:30am, Domingo-Viernes):
#   30 9 * * 0-5 /home/rodrigo/scripts/cron_wrapper.sh "Buscapega Daily" "/home/rodrigo/scripts/wunen-daily.sh"
# =============================================================================

BACKEND="http://localhost:8020"
SCRAPER="http://localhost:8021"
NOTIFY="/home/rodrigo/scripts/notify_telegram.sh"
LOG_DIR="/var/log/wunen"
LOG_FILE="$LOG_DIR/daily-$(date '+%Y%m%d_%H%M%S').log"
MIN_SCORE=40          # score mínimo para auto-postular (0-100)
MAX_WAIT_SECS=300     # esperar hasta 5 min a que el backend inicie
SCRAPING_WAIT=600     # esperar 10 min a que los scrapers terminen

mkdir -p "$LOG_DIR"

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg" | tee -a "$LOG_FILE"
}

# ── 1. Esperar backend ────────────────────────────────────────────────────────
log "=== Buscapega Daily Run ==="
log "Esperando que el backend esté disponible (max ${MAX_WAIT_SECS}s)..."

waited=0
until curl -sf "$BACKEND/health" > /dev/null 2>&1; do
    if [ $waited -ge $MAX_WAIT_SECS ]; then
        log "ERROR: Backend no respondió en ${MAX_WAIT_SECS}s. Abortando."
        $NOTIFY "❌ <b>Buscapega Daily — ABORTADO</b>
⚠️ Backend no disponible después de ${MAX_WAIT_SECS}s
📅 $(date '+%d/%m/%Y %H:%M')"
        exit 1
    fi
    sleep 15
    waited=$((waited + 15))
done
log "Backend listo (esperé ${waited}s)."

# ── 2. Pipeline FindJobIT (scraping + auto-postulación en un solo paso) ───────
log "Disparando pipeline FindJobIT (scraping + postulación)..."
FJIT_RESP=$(curl -sf -X POST "$SCRAPER/run/findjobit" 2>&1 || echo '{"error":"sin respuesta"}')
log "FindJobIT: $FJIT_RESP"

# ── 3. Scraping otros portales ────────────────────────────────────────────────
log "Disparando scraping otros portales (Remotive, RemoteOK, GetOnBrd)..."
OTHER_RESP=$(curl -sf -X POST "$BACKEND/api/scraper/trigger" 2>&1 || echo '{"error":"sin respuesta"}')
log "Otros portales: $OTHER_RESP"

# ── 4. Esperar a que los scrapers terminen ────────────────────────────────────
log "Esperando ${SCRAPING_WAIT}s para que los scrapers completen..."
sleep $SCRAPING_WAIT

# ── 5. Auto-postular a ofertas pendientes ────────────────────────────────────
log "Iniciando auto-postulaciones (score >= $MIN_SCORE)..."
BATCH_RESP=$(curl -sf -X POST \
    "$BACKEND/api/offers/autoapply-batch?min_score=$MIN_SCORE" \
    2>&1 || echo '{"error":"sin respuesta","started":0}')
log "Batch result: $BATCH_RESP"

STARTED=$(echo "$BATCH_RESP" | python3 -c \
    "import json,sys; d=json.load(sys.stdin); print(d.get('started',0))" 2>/dev/null || echo "?")

# ── 6. Contar ofertas nuevas en la BD ─────────────────────────────────────────
PENDIENTES=$(curl -sf "$BACKEND/api/offers?status=PENDIENTE" 2>/dev/null | \
    python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?")

# ── 7. Notificación Telegram ──────────────────────────────────────────────────
log "Auto-postulaciones iniciadas: $STARTED. Pendientes en bandeja: $PENDIENTES"

$NOTIFY "🤖 <b>Buscapega — Búsqueda diaria completada</b>

✉️ Postulaciones automáticas: <b>${STARTED}</b>
📋 Ofertas pendientes en bandeja: <b>${PENDIENTES}</b>
📅 $(date '+%d/%m/%Y %H:%M')

Revisa las postulaciones en: http://wunen.presto"

log "=== Buscapega Daily Run completado ==="
