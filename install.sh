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

log()   { echo -e "${CYAN}▶${RESET} $1"; }
ok()    { echo -e "${GREEN}✓${RESET} $1"; }
warn()  { echo -e "${YELLOW}!${RESET} $1"; }
error() { echo -e "${RED}✗ ERROR:${RESET} $1"; exit 1; }
ask()   { echo -e "${BOLD}$1${RESET}"; }
sep()   { echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$SCRIPT_DIR/docker"
DOCS_DIR="$SCRIPT_DIR/documentos"
SETUP_DIR="$SCRIPT_DIR/setup"

print_header

# ─────────────────────────────────────────────────────────────────────────────
# 1. Validar estructura de carpetas obligatorias
# ─────────────────────────────────────────────────────────────────────────────
log "Validando estructura del proyecto..."

MISSING_DIRS=()

for required in \
  "$DOCKER_DIR" \
  "$DOCKER_DIR/backend" \
  "$DOCKER_DIR/scraper" \
  "$DOCKER_DIR/frontend" \
  "$DOCKER_DIR/whatsapp"
do
  if [[ ! -d "$required" ]]; then
    MISSING_DIRS+=("$required")
  fi
done

if [[ ${#MISSING_DIRS[@]} -gt 0 ]]; then
  echo ""
  error "Faltan carpetas obligatorias del proyecto:
$(for d in "${MISSING_DIRS[@]}"; do echo "  ✗ $d"; done)

  Asegúrate de estar ejecutando install.sh desde la raíz del proyecto Wunen."
fi

ok "Estructura de carpetas del proyecto correcta"

# Crear carpeta documentos si no existe
if [[ ! -d "$DOCS_DIR" ]]; then
  log "Creando carpeta documentos/..."
  mkdir -p "$DOCS_DIR"
  ok "Carpeta documentos/ creada"
else
  ok "Carpeta documentos/ existe"
fi

# Crear portales.json por defecto si no existe
if [[ ! -f "$DOCS_DIR/portales.json" ]]; then
  log "Creando portales.json con lista por defecto..."
  cat > "$DOCS_DIR/portales.json" << 'PORTALES_EOF'
[
  {"name": "Tecnoempleo",    "url": "https://www.tecnoempleo.com",    "auto_apply": true,  "market": "España",        "session_key": "tecnoempleo"},
  {"name": "ChileTrabajos",  "url": "https://www.chiletrabajos.cl",   "auto_apply": true,  "market": "Chile",         "session_key": "chiletrabajos"},
  {"name": "Chumi-IT",       "url": "https://chumi-it.com",           "auto_apply": true,  "market": "LATAM/España",  "session_key": "chumiit"},
  {"name": "RemoteLatinos",  "url": "https://www.remotelatinos.com",  "auto_apply": true,  "market": "LATAM/EEUU",    "session_key": "remotelatinos"},
  {"name": "GetOnBrd",       "url": "https://www.getonbrd.com",       "auto_apply": true,  "market": "LATAM/Chile",   "session_key": "getonbrd"},
  {"name": "FindJobIT",      "url": "https://findjobit.com",          "auto_apply": true,  "market": "Internacional", "session_key": "findjobit"},
  {"name": "Torre.ai",       "url": "https://torre.ai",               "auto_apply": false, "market": "LATAM/EEUU",    "session_key": null},
  {"name": "InfoJobs",       "url": "https://www.infojobs.net",       "auto_apply": false, "market": "España",        "session_key": null},
  {"name": "LaraJobs",       "url": "https://larajobs.com",           "auto_apply": false, "market": "Internacional", "session_key": null},
  {"name": "FlexJobs",       "url": "https://www.flexjobs.com",       "auto_apply": false, "market": "Internacional", "session_key": null},
  {"name": "Remotive",       "url": "https://remotive.com",           "auto_apply": false, "market": "Internacional", "session_key": null},
  {"name": "RemoteOK",       "url": "https://remoteok.com",           "auto_apply": false, "market": "Internacional", "session_key": null}
]
PORTALES_EOF
  ok "portales.json creado"
fi

# Crear perfil.md por defecto si no existe
if [[ ! -f "$SCRIPT_DIR/perfil.md" ]]; then
  log "Creando perfil.md base..."
  cat > "$SCRIPT_DIR/perfil.md" << 'PERFIL_EOF'
# Perfil del Candidato

> Completa este archivo desde la interfaz web en la sección "Acerca de mí > Perfil",
> o edítalo directamente. El evaluador de ofertas lo usa para puntuar cada vacante.

## Stack Tecnológico

| Tecnología | Nivel | Años de experiencia | ¿Dispuesto a trabajar con ella? |
|---|---|---|---|
| (completar) | Intermedio | - | Sí |

## Modalidad de Trabajo

- **Preferencia:** Remoto
- **Zona horaria:** UTC-3 / UTC-4

## Expectativa Salarial

| Moneda | Mínimo aceptable | Rango preferido |
|---|---|---|
| USD (freelance/hora) | - | - |
| CLP (dependencia mensual) | - | - |

## Idiomas para el Trabajo

| Idioma | Nivel | Contextos donde lo uso |
|---|---|---|
| Español | Nativo | Todo |
PERFIL_EOF
  ok "perfil.md base creado (complétalo desde la interfaz web)"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 2. Verificar prerrequisitos del sistema
# ─────────────────────────────────────────────────────────────────────────────
log "Verificando prerrequisitos del sistema..."

if ! command -v docker &> /dev/null; then
  error "Docker no está instalado. Instálalo desde https://docs.docker.com/get-docker/"
fi

if docker compose version &> /dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
  COMPOSE_CMD="docker-compose"
else
  error "Docker Compose no está disponible. Actualiza Docker Desktop o instala docker-compose."
fi

ok "Docker disponible: $(docker --version | head -1)"

# ─────────────────────────────────────────────────────────────────────────────
# 3. Configuración interactiva
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}Configuración inicial${RESET}"
sep
echo ""
echo "Necesitamos algunos datos para configurar el sistema."
echo "Presiona Enter para usar el valor por defecto (entre corchetes)."
echo ""

ask "→ Anthropic API Key (console.anthropic.com — necesaria para evaluación IA de ofertas):"
read -r -p "  sk-ant-... > " ANTHROPIC_API_KEY
[[ -z "$ANTHROPIC_API_KEY" ]] && warn "Sin API key — la evaluación usará scoring básico por keywords."
echo ""

ask "→ Número de teléfono para notificaciones WhatsApp (sin el +, ej: 56912345678):"
read -r -p "  [56912345678] > " WHATSAPP_PHONE
WHATSAPP_PHONE="${WHATSAPP_PHONE:-56912345678}"
echo ""

ask "→ Correo Gmail para postulaciones automáticas (para portales que usan email):"
read -r -p "  correo@gmail.com > " GMAIL_USER
echo ""

GMAIL_APP_PASSWORD=""
if [[ -n "$GMAIL_USER" ]]; then
  ask "→ Contraseña de aplicación Gmail (16 caracteres, sin espacios):"
  echo -e "  ${CYAN}Cómo obtenerla: https://myaccount.google.com/apppasswords${RESET}"
  read -r -p "  > " GMAIL_APP_PASSWORD
  echo ""
fi

ask "→ Puerto para la interfaz web:"
read -r -p "  [3000] > " FRONTEND_PORT
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

ask "→ Puerto para el API backend:"
read -r -p "  [8000] > " BACKEND_PORT
BACKEND_PORT="${BACKEND_PORT:-8000}"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 4. Generar archivo .env
# ─────────────────────────────────────────────────────────────────────────────
POSTGRES_PASSWORD=$(LC_ALL=C tr -dc 'A-Za-z0-9_' < /dev/urandom | head -c 24 2>/dev/null || echo "wunen_$(date +%s)")
ENV_FILE="$DOCKER_DIR/.env"

[[ -f "$ENV_FILE" ]] && cp "$ENV_FILE" "$ENV_FILE.bak" && warn "Backup del .env anterior guardado como .env.bak"

log "Generando archivo de configuración..."
cat > "$ENV_FILE" << EOF
# Generado por install.sh — $(date)

POSTGRES_DB=wunen
POSTGRES_USER=wunen
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}

NEXT_PUBLIC_API_URL=http://localhost:${BACKEND_PORT}
ENVIRONMENT=production

WHATSAPP_DEFAULT_PHONE=${WHATSAPP_PHONE}
WHATSAPP_PAIRING_PHONE=${WHATSAPP_PHONE}

GMAIL_USER=${GMAIL_USER:-}
GMAIL_APP_PASSWORD=${GMAIL_APP_PASSWORD:-}
GMAIL_FROM_NAME=Wunen

FINDJOBIT_MIN_SCORE=50
EOF

ok ".env generado"

# ─────────────────────────────────────────────────────────────────────────────
# 5. Construir e iniciar servicios Docker
# ─────────────────────────────────────────────────────────────────────────────
echo ""
log "Construyendo e iniciando servicios Docker..."
echo -e "${YELLOW}Esto puede tardar varios minutos la primera vez.${RESET}"
echo ""

cd "$DOCKER_DIR"
$COMPOSE_CMD pull db --quiet 2>/dev/null || true
$COMPOSE_CMD build --quiet
$COMPOSE_CMD up -d

echo ""
ok "Servicios Docker iniciados"

# ─────────────────────────────────────────────────────────────────────────────
# 6. Esperar a que el backend esté listo
# ─────────────────────────────────────────────────────────────────────────────
log "Esperando a que el backend esté listo..."
MAX_WAIT=60
WAITED=0
until curl -sf "http://localhost:${BACKEND_PORT}/health" > /dev/null 2>&1; do
  if [[ $WAITED -ge $MAX_WAIT ]]; then
    warn "El backend tardó más de lo esperado. Continúa y verifica con: docker compose logs backend"
    break
  fi
  printf "."
  sleep 2
  WAITED=$((WAITED + 2))
done
echo ""
curl -sf "http://localhost:${BACKEND_PORT}/health" > /dev/null 2>&1 && ok "Backend disponible en http://localhost:${BACKEND_PORT}"

# ─────────────────────────────────────────────────────────────────────────────
# 7. Configurar sesiones de portales (opcional)
# ─────────────────────────────────────────────────────────────────────────────
echo ""
sep
echo ""
ask "¿Deseas configurar ahora las sesiones de los portales con auto-postulación? (s/N)"
echo -e "  ${CYAN}Esto abrirá un navegador por cada portal para que puedas hacer login con Google.${RESET}"
read -r -p "  > " SETUP_SESSIONS
echo ""

if [[ "${SETUP_SESSIONS,,}" == "s" || "${SETUP_SESSIONS,,}" == "si" || "${SETUP_SESSIONS,,}" == "y" || "${SETUP_SESSIONS,,}" == "yes" ]]; then

  if [[ ! -d "$SETUP_DIR" ]]; then
    warn "No se encontró la carpeta setup/. Omitiendo configuración de sesiones."
    warn "Puedes hacerlo manualmente más tarde: cd setup && python3 setup_session.py --lista"
  else
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
      warn "Python 3 no está instalado. No se pueden configurar sesiones ahora."
      warn "Instala Python 3 y luego ejecuta: cd setup && python3 setup_session.py --lista"
    else
      cd "$SETUP_DIR"

      log "Instalando dependencias de setup..."
      python3 -m pip install -q -r requirements.txt 2>/dev/null || {
        warn "Falló pip install. Intenta manualmente: pip3 install -r setup/requirements.txt"
      }

      python3 -m playwright install chromium 2>/dev/null || {
        warn "Falló playwright install. Intenta manualmente: playwright install chromium"
      }

      echo ""
      log "Portales disponibles para autenticar:"
      python3 setup_session.py --lista
      echo ""

      ask "¿Qué portales deseas autenticar? (Enter = todos los que falten, o escribe los nombres separados por coma)"
      echo -e "  ${CYAN}Ej: getonbrd, tecnoempleo   o presiona Enter para todos${RESET}"
      read -r -p "  > " PORTALES_INPUT
      echo ""

      if [[ -z "$PORTALES_INPUT" ]]; then
        # Autenticar todos los que no tienen sesión
        PORTALES_TO_AUTH=$(python3 - << 'PYEOF'
import json, sys
from pathlib import Path
cookies_dir = Path("cookies")
portales = ["findjobit","getonbrd","tecnoempleo","remotelatinos","chiletrabajos","chumiit"]
missing = [p for p in portales if not (cookies_dir / f"{p}_session.json").exists()]
print(",".join(missing))
PYEOF
)
      else
        PORTALES_TO_AUTH="$PORTALES_INPUT"
      fi

      IFS=',' read -ra PORTALES_ARR <<< "$PORTALES_TO_AUTH"
      TOTAL=${#PORTALES_ARR[@]}
      IDX=0

      for portal in "${PORTALES_ARR[@]}"; do
        portal=$(echo "$portal" | tr -d ' ')
        [[ -z "$portal" ]] && continue
        IDX=$((IDX + 1))
        echo ""
        log "[${IDX}/${TOTAL}] Autenticando portal: ${portal}"
        echo -e "  ${YELLOW}Se abrirá el navegador — completa el login con Google y ciérralo cuando termines.${RESET}"
        python3 setup_session.py "$portal" && ok "Sesión de ${portal} capturada" || warn "No se pudo capturar sesión de ${portal}"
      done

      echo ""
      ok "Proceso de autenticación completado"
      cd "$SCRIPT_DIR"
    fi
  fi
else
  echo -e "  Puedes configurar sesiones más tarde:"
  echo -e "  ${CYAN}cd setup && python3 setup_session.py --lista${RESET}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 8. Resumen final
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════╗${RESET}"
echo -e "${GREEN}${BOLD}║         Instalación completada           ║${RESET}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  ${BOLD}Interfaz web:${RESET}  http://localhost:${FRONTEND_PORT}"
echo -e "  ${BOLD}API / Backend:${RESET} http://localhost:${BACKEND_PORT}"
echo -e "  ${BOLD}API Docs:${RESET}      http://localhost:${BACKEND_PORT}/docs"
echo ""
echo -e "  ${BOLD}Carpeta documentos/:${RESET}"
echo -e "    ${SCRIPT_DIR}/documentos/"
echo -e "    ├── portales.json  ← lista de portales (editable)"
echo -e "    ├── cv_data.json   ← datos CV español (se genera al guardar desde web)"
echo -e "    ├── cv_data_en.json"
echo -e "    ├── perfil_data.json"
echo -e "    └── settings.json  ← teléfono WA y emails"
echo ""
echo -e "  ${BOLD}Próximos pasos:${RESET}"
echo -e "    1. Abre http://localhost:${FRONTEND_PORT} en tu navegador"
echo -e "    2. Ve a ${BOLD}Acerca de mí${RESET} y completa tu CV y perfil"
echo -e "    3. Ve a ${BOLD}Portales${RESET} para ver el estado de las sesiones"
echo -e "    4. Presiona ${BOLD}Buscar ofertas${RESET} en la home"
echo ""
echo -e "  ${BOLD}Comandos útiles:${RESET}"
echo -e "    cd docker && docker compose logs -f"
echo -e "    cd docker && docker compose down"
echo -e "    cd setup  && python3 setup_session.py --lista"
echo ""

[[ -z "${ANTHROPIC_API_KEY:-}" ]] && \
  echo -e "  ${YELLOW}⚠  Sin API key — agrega ANTHROPIC_API_KEY en docker/.env y reinicia el backend.${RESET}\n"

if command -v claude &> /dev/null; then
  echo -e "  ${BOLD}Claude Code disponible:${RESET}"
  echo -e "    ${CYAN}claude /valida <url>${RESET}   — verifica si un portal es automatizable"
  echo -e "    ${CYAN}claude /autentica${RESET}       — configura sesiones de todos los portales"
  echo ""
fi
