#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Wunen — Configurar / reconfigurar el correo Gmail de postulaciones
#
# Gmail se pide durante install.sh, pero puedes configurarlo o cambiarlo en
# cualquier momento con este script. Actualiza docker/.env y reinicia el scraper.
#
# Uso: ./setup-gmail.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'
BOLD='\033[1m'; RESET='\033[0m'

log()   { echo -e "${CYAN}▶${RESET} $1"; }
ok()    { echo -e "${GREEN}✓${RESET} $1"; }
warn()  { echo -e "${YELLOW}!${RESET} $1"; }
error() { echo -e "${RED}✗ ERROR:${RESET} $1"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/docker/.env"

echo ""
echo -e "${BOLD}Wunen — Configurar correo Gmail de postulaciones${RESET}"
echo ""

[[ -f "$ENV_FILE" ]] || error "No se encontró $ENV_FILE. Ejecuta primero ./install.sh"

echo "Necesitas una contraseña de aplicación de Gmail (NO tu contraseña normal)."
echo -e "Genérala en: ${CYAN}https://myaccount.google.com/apppasswords${RESET}"
echo ""

while true; do
  echo -e "${BOLD}→ Correo Gmail (correo@gmail.com):${RESET}"
  read -r -p "  > " GMAIL_USER
  if [[ "$GMAIL_USER" =~ ^[^@]+@[^@]+\.[^@]+$ ]]; then
    break
  else
    warn "Correo inválido. Usa el formato correo@dominio.com"
  fi
done
echo ""

echo -e "${BOLD}→ Contraseña de aplicación (16 caracteres, con o sin espacios):${RESET}"
read -r -p "  > " GMAIL_APP_PASSWORD
GMAIL_APP_PASSWORD=$(echo "$GMAIL_APP_PASSWORD" | tr -d ' ')
echo ""

# Actualizar (o agregar) las variables en docker/.env
update_env() {
  local key="$1" val="$2"
  if grep -q "^${key}=" "$ENV_FILE"; then
    # Usar | como separador para no chocar con caracteres del valor
    sed -i.bak "s|^${key}=.*|${key}=${val}|" "$ENV_FILE" && rm -f "$ENV_FILE.bak"
  else
    echo "${key}=${val}" >> "$ENV_FILE"
  fi
}

log "Actualizando docker/.env..."
update_env "GMAIL_USER" "$GMAIL_USER"
update_env "GMAIL_APP_PASSWORD" "$GMAIL_APP_PASSWORD"
ok "Credenciales guardadas en docker/.env"

log "Reiniciando el servicio scraper para aplicar los cambios..."
if docker compose version &>/dev/null 2>&1; then
  ( cd "$SCRIPT_DIR/docker" && docker compose up -d scraper )
  ok "Scraper reiniciado"
else
  warn "No se detectó docker compose. Reinicia manualmente: cd docker && docker compose up -d scraper"
fi

echo ""
ok "Gmail configurado. El correo de postulaciones es: ${GMAIL_USER}"
echo ""
