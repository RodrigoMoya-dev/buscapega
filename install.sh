#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Wunen — Instalador
# Sistema personal de automatización de búsqueda de empleo
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

BLUE='\033[0;34m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'
BOLD='\033[1m'

print_header() {
  echo ""
  echo -e "${BLUE}${BOLD}╔══════════════════════════════════════════╗${RESET}"
  echo -e "${BLUE}${BOLD}║           Wunen — Instalador             ║${RESET}"
  echo -e "${BLUE}${BOLD}║  Automatización de búsqueda de empleo    ║${RESET}"
  echo -e "${BLUE}${BOLD}╚══════════════════════════════════════════╝${RESET}"
  echo ""
}

log()    { echo -e "${CYAN}▶${RESET} $1"; }
ok()     { echo -e "${GREEN}✓${RESET} $1"; }
warn()   { echo -e "${YELLOW}!${RESET} $1"; }
error()  { echo -e "${RED}✗${RESET} $1"; exit 1; }
ask()    { echo -e "${BOLD}$1${RESET}"; }

# ─────────────────────────────────────────────────────────────────────────────
# Detectar directorio del script
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$SCRIPT_DIR/docker"

print_header

# ─────────────────────────────────────────────────────────────────────────────
# 1. Verificar prerrequisitos
# ─────────────────────────────────────────────────────────────────────────────
log "Verificando prerrequisitos..."

if ! command -v docker &> /dev/null; then
  error "Docker no está instalado. Instálalo desde https://docs.docker.com/get-docker/"
fi

if ! docker compose version &> /dev/null 2>&1; then
  if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose no está disponible. Actualiza Docker Desktop o instala docker-compose."
  fi
fi

ok "Docker disponible: $(docker --version)"

# ─────────────────────────────────────────────────────────────────────────────
# 2. Configuración interactiva
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}Configuración inicial${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo "Necesitamos algunos datos para configurar el sistema."
echo "Presiona Enter para usar el valor por defecto (entre corchetes)."
echo ""

# Anthropic API Key
ask "→ Anthropic API Key (obtenla en console.anthropic.com):"
read -r -p "  sk-ant-... > " ANTHROPIC_API_KEY
if [[ -z "$ANTHROPIC_API_KEY" ]]; then
  warn "No ingresaste API key. La evaluación de ofertas usará el modo sin IA (scoring básico)."
fi
echo ""

# WhatsApp
ask "→ Número de teléfono para notificaciones WhatsApp (sin el +, ej: 56912345678):"
read -r -p "  [56912345678] > " WHATSAPP_PHONE
WHATSAPP_PHONE="${WHATSAPP_PHONE:-56912345678}"
echo ""

# Gmail
ask "→ Correo Gmail para postulaciones (se usará para enviar aplicaciones via email):"
read -r -p "  correo@gmail.com > " GMAIL_USER
echo ""

GMAIL_APP_PASSWORD=""
if [[ -n "$GMAIL_USER" ]]; then
  ask "→ Contraseña de aplicación Gmail (16 caracteres, sin espacios):"
  echo -e "  ${CYAN}Cómo obtenerla: https://myaccount.google.com/apppasswords${RESET}"
  read -r -p "  > " GMAIL_APP_PASSWORD
  echo ""
fi

# Puerto frontend
ask "→ Puerto para la interfaz web:"
read -r -p "  [3000] > " FRONTEND_PORT
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

# Puerto backend
ask "→ Puerto para el API backend:"
read -r -p "  [8000] > " BACKEND_PORT
BACKEND_PORT="${BACKEND_PORT:-8000}"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 3. Generar contraseña PostgreSQL
# ─────────────────────────────────────────────────────────────────────────────
POSTGRES_PASSWORD=$(LC_ALL=C tr -dc 'A-Za-z0-9_' < /dev/urandom | head -c 24 || true)
if [[ -z "$POSTGRES_PASSWORD" ]]; then
  POSTGRES_PASSWORD="wunen_$(date +%s)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 4. Crear archivo .env
# ─────────────────────────────────────────────────────────────────────────────
ENV_FILE="$DOCKER_DIR/.env"

if [[ -f "$ENV_FILE" ]]; then
  warn "Ya existe un archivo .env. Se creará una copia de respaldo como .env.bak"
  cp "$ENV_FILE" "$ENV_FILE.bak"
fi

log "Generando archivo de configuración..."

cat > "$ENV_FILE" << EOF
# Generado por install.sh — $(date)

# PostgreSQL
POSTGRES_DB=wunen
POSTGRES_USER=wunen
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# Anthropic / Claude API
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}

# Frontend (URL del backend vista desde el navegador)
NEXT_PUBLIC_API_URL=http://localhost:${BACKEND_PORT}

# Entorno
ENVIRONMENT=production

# ── WhatsApp (Baileys) ───────────────────────────────────────────────────────
WHATSAPP_DEFAULT_PHONE=${WHATSAPP_PHONE}
WHATSAPP_PAIRING_PHONE=${WHATSAPP_PHONE}

# ── Gmail ────────────────────────────────────────────────────────────────────
GMAIL_USER=${GMAIL_USER:-}
GMAIL_APP_PASSWORD=${GMAIL_APP_PASSWORD:-}
GMAIL_FROM_NAME=Wunen

# Score mínimo para auto-postular en FindJobIT
FINDJOBIT_MIN_SCORE=50
EOF

ok ".env generado en $ENV_FILE"

# ─────────────────────────────────────────────────────────────────────────────
# 5. Ajustar puertos en docker-compose si son distintos al default
# ─────────────────────────────────────────────────────────────────────────────
COMPOSE_FILE="$DOCKER_DIR/docker-compose.yml"

if [[ "$FRONTEND_PORT" != "3000" ]] || [[ "$BACKEND_PORT" != "8000" ]]; then
  warn "Puertos personalizados detectados. Actualiza manualmente los ports en $COMPOSE_FILE si es necesario."
fi

# ─────────────────────────────────────────────────────────────────────────────
# 6. Construir e iniciar servicios
# ─────────────────────────────────────────────────────────────────────────────
echo ""
log "Construyendo e iniciando servicios Docker..."
echo -e "${YELLOW}Esto puede tardar varios minutos la primera vez.${RESET}"
echo ""

cd "$DOCKER_DIR"

if docker compose version &> /dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
else
  COMPOSE_CMD="docker-compose"
fi

$COMPOSE_CMD pull db --quiet || true
$COMPOSE_CMD build --quiet
$COMPOSE_CMD up -d

echo ""
ok "Servicios iniciados"

# ─────────────────────────────────────────────────────────────────────────────
# 7. Esperar a que los servicios estén listos
# ─────────────────────────────────────────────────────────────────────────────
log "Esperando a que el backend esté listo..."
MAX_WAIT=60
WAITED=0
until curl -sf "http://localhost:${BACKEND_PORT}/health" > /dev/null 2>&1; do
  if [[ $WAITED -ge $MAX_WAIT ]]; then
    warn "El backend tardó más de lo esperado. Verifica con: cd docker && docker compose logs backend"
    break
  fi
  sleep 2
  WAITED=$((WAITED + 2))
done

if curl -sf "http://localhost:${BACKEND_PORT}/health" > /dev/null 2>&1; then
  ok "Backend disponible en http://localhost:${BACKEND_PORT}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 8. Resumen final
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}${BOLD}║         Instalación completada           ║${RESET}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  ${BOLD}Interfaz web:${RESET}     http://localhost:${FRONTEND_PORT}"
echo -e "  ${BOLD}API / Backend:${RESET}    http://localhost:${BACKEND_PORT}"
echo -e "  ${BOLD}API Docs:${RESET}         http://localhost:${BACKEND_PORT}/docs"
echo ""
echo -e "  ${BOLD}Comandos útiles:${RESET}"
echo -e "    cd docker && docker compose logs -f     ${CYAN}# Ver logs en tiempo real${RESET}"
echo -e "    cd docker && docker compose down        ${CYAN}# Detener todos los servicios${RESET}"
echo -e "    cd docker && docker compose restart     ${CYAN}# Reiniciar servicios${RESET}"
echo ""

if [[ -z "$ANTHROPIC_API_KEY" ]]; then
  echo -e "  ${YELLOW}⚠  Sin API key de Anthropic: las ofertas se evaluarán con scoring básico.${RESET}"
  echo -e "     Agrega ANTHROPIC_API_KEY en $ENV_FILE y reinicia con 'docker compose restart backend'."
  echo ""
fi

echo -e "  ${BOLD}Próximos pasos:${RESET}"
echo -e "    1. Abre http://localhost:${FRONTEND_PORT} en tu navegador"
echo -e "    2. Ve a 'Acerca de mí' y completa tu CV y perfil"
echo -e "    3. Ve a 'Portales' y activa la autenticación de los portales"
echo -e "       → Ejecuta: cd setup && python3 setup_session.py --lista"
echo -e "    4. Presiona 'Buscar ofertas' para traer las primeras propuestas"
echo ""

if command -v claude &> /dev/null; then
  echo -e "  ${BOLD}Claude Code detectado — comandos disponibles:${RESET}"
  echo -e "    claude /valida <url>     ${CYAN}# Verifica si un portal es automatizable${RESET}"
  echo -e "    claude /autentica        ${CYAN}# Configura sesiones de todos los portales${RESET}"
  echo ""
fi
