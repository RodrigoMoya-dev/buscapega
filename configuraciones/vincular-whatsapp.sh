#!/usr/bin/env bash
# Vincula el número de WhatsApp: muestra el QR o genera un código de vinculación.
# Uso: ./configuraciones/vincular-whatsapp.sh [host] [puerto] [telefono]
#   host      IP o hostname del servidor donde corre Buscapega (default: localhost)
#   puerto    Puerto del servicio WhatsApp (default: 3001)
#   telefono  (opcional) Número con código de país (solo dígitos, ej: 56962075019).
#             Si se indica, genera un CÓDIGO de vinculación en vez del QR —
#             útil si el QR falla con "No se pueden vincular dispositivos nuevos".

set -euo pipefail

HOST="${1:-localhost}"
PORT="${2:-3001}"
PHONE="${3:-}"
QR_URL="http://${HOST}:${PORT}/qr"
HEALTH_URL="http://${HOST}:${PORT}/health"
PAIR_URL="http://${HOST}:${PORT}/pair"

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

echo ""
echo -e "${BLUE}${BOLD}╔══════════════════════════════════════════╗${RESET}"
echo -e "${BLUE}${BOLD}║     Buscapega — Vincular WhatsApp            ║${RESET}"
echo -e "${BLUE}${BOLD}╚══════════════════════════════════════════╝${RESET}"
echo ""

# Verificar que el servicio esté corriendo
echo -e "${CYAN}▶${RESET} Verificando servicio WhatsApp en ${HOST}:${PORT}..."

STATUS=$(curl -sf --max-time 5 "$HEALTH_URL" 2>/dev/null | grep -o '"connection":"[^"]*"' | cut -d'"' -f4 || echo "unreachable")

if [[ "$STATUS" == "unreachable" ]]; then
  echo -e "${RED}✗${RESET} No se puede conectar al servicio WhatsApp en ${HOST}:${PORT}"
  echo ""
  echo -e "  Asegúrate de que el contenedor esté corriendo:"
  echo -e "  ${CYAN}cd ~/docker/buscapega && docker compose up -d whatsapp${RESET}"
  echo -e "  ${CYAN}docker compose logs -f whatsapp${RESET}"
  exit 1
fi

if [[ "$STATUS" == "connected" ]]; then
  echo -e "${GREEN}✓${RESET} WhatsApp ya está conectado. No necesitas escanear nada."
  exit 0
fi

echo -e "${YELLOW}!${RESET} Estado: ${STATUS}"
echo ""

# ── Alternativa: vinculación por código (sin QR) ──────────────────────────────
# Si se pasó un teléfono como 3er argumento, pide un código de vinculación.
if [[ -n "$PHONE" ]]; then
  CLEAN_PHONE="${PHONE//[^0-9]/}"
  echo -e "${CYAN}▶${RESET} Generando código de vinculación para ${CLEAN_PHONE}..."
  RESP=$(curl -sf --max-time 15 -X POST "$PAIR_URL" \
    -H "Content-Type: application/json" \
    -d "{\"phone\":\"${CLEAN_PHONE}\"}" 2>/dev/null || echo "")
  CODE=$(echo "$RESP" | grep -o '"code":"[^"]*"' | cut -d'"' -f4 || echo "")
  if [[ -n "$CODE" ]]; then
    echo ""
    echo -e "${GREEN}${BOLD}  Código de vinculación: ${CODE}${RESET}"
    echo ""
    echo -e "${BOLD}Pasos en el teléfono:${RESET}"
    echo -e "  1. Abre WhatsApp → ⋮ → ${BOLD}Dispositivos vinculados${RESET}"
    echo -e "  2. Toca ${BOLD}Vincular un dispositivo${RESET}"
    echo -e "  3. Toca ${BOLD}Vincular con número de teléfono${RESET} (abajo)"
    echo -e "  4. Ingresa el código mostrado arriba"
    echo ""
    echo -e "  Una vez vinculado, el estado cambiará a 'connected' automáticamente."
    echo ""
    exit 0
  else
    ERRMSG=$(echo "$RESP" | grep -o '"error":"[^"]*"' | cut -d'"' -f4 || echo "")
    echo -e "${RED}✗${RESET} No se pudo generar el código${ERRMSG:+: $ERRMSG}"
    echo -e "  Reintenta en unos segundos o usa el QR (abajo)."
    echo ""
  fi
fi

# Intentar mostrar el QR en el terminal si qrencode está disponible
if command -v qrencode &>/dev/null; then
  echo -e "${CYAN}▶${RESET} Obteniendo QR del servidor..."
  QR_DATA=$(curl -sf --max-time 10 "http://${HOST}:${PORT}/qr-data" 2>/dev/null || echo "")

  if [[ -n "$QR_DATA" && "$QR_DATA" != "null" ]]; then
    echo ""
    echo -e "${BOLD}Escanea este QR con WhatsApp:${RESET}"
    echo "$QR_DATA" | qrencode -t ANSIUTF8
    echo ""
  fi
fi

# Siempre mostrar la URL HTML como opción principal
echo -e "${BOLD}Opciones para escanear el QR:${RESET}"
echo ""
echo -e "  ${BOLD}1. Desde el navegador (recomendado):${RESET}"
echo -e "     ${CYAN}${QR_URL}${RESET}"
echo -e "     (La página se actualiza automáticamente cada 20 segundos)"
echo ""
echo -e "  ${BOLD}2. Desde los logs del contenedor:${RESET}"
if [[ "$HOST" == "localhost" || "$HOST" == "127.0.0.1" ]]; then
  echo -e "     ${CYAN}docker compose -f ~/docker/buscapega/docker-compose.yml logs -f whatsapp${RESET}"
else
  echo -e "     ${CYAN}ssh ${HOST} 'cd ~/docker/buscapega && docker compose logs -f whatsapp'${RESET}"
fi
echo ""
echo -e "  ${BOLD}3. ¿El QR falla? Vincula con un código (sin QR):${RESET}"
echo -e "     ${CYAN}./configuraciones/vincular-whatsapp.sh ${HOST} ${PORT} <tu_numero>${RESET}"
echo -e "     (ej: ./configuraciones/vincular-whatsapp.sh ${HOST} ${PORT} 56962075019)"
echo -e "     Útil si aparece \"No se pueden vincular dispositivos nuevos en este momento\"."
echo ""
echo -e "${BOLD}Pasos en el teléfono:${RESET}"
echo -e "  1. Abre WhatsApp"
echo -e "  2. Toca los tres puntos (⋮) → ${BOLD}Dispositivos vinculados${RESET}"
echo -e "  3. Toca ${BOLD}Vincular un dispositivo${RESET}"
echo -e "  4. Escanea el código QR mostrado en el navegador"
echo ""
echo -e "  Una vez vinculado, el estado cambiará a 'connected' automáticamente."
echo ""
