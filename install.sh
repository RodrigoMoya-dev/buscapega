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
  {"name": "FindJobIT",      "url": "https://findjobit.com",          "auto_apply": true,  "market": "Internacional", "session_key": "findjobit", "demo_active": true},
  {"name": "Tecnoempleo",    "url": "https://www.tecnoempleo.com",    "auto_apply": true,  "market": "España",        "session_key": "tecnoempleo"},
  {"name": "ChileTrabajos",  "url": "https://www.chiletrabajos.cl",   "auto_apply": true,  "market": "Chile",         "session_key": "chiletrabajos"},
  {"name": "Chumi-IT",       "url": "https://chumi-it.com",           "auto_apply": true,  "market": "LATAM/España",  "session_key": "chumiit"},
  {"name": "RemoteLatinos",  "url": "https://www.remotelatinos.com",  "auto_apply": true,  "market": "LATAM/EEUU",    "session_key": "remotelatinos"},
  {"name": "GetOnBrd",       "url": "https://www.getonbrd.com",       "auto_apply": true,  "market": "LATAM/Chile",   "session_key": "getonbrd"},
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

ask "→ Tu nombre (se usará para saludarte en la web, ej: Rodrigo):"
read -r -p "  > " USER_NAME
[[ -z "$USER_NAME" ]] && warn "Sin nombre — podrás agregarlo luego en la web (Configuración) o en documentos/settings.json."
echo ""

ask "→ Anthropic API Key  [OPCIONAL — puedes dejarlo vacío y presionar Enter]:"
echo -e "  ${CYAN}No es obligatoria.${RESET} La evaluación de ofertas funciona sin ella (scoring por"
echo -e "  keywords). Para evaluación con IA, lo recomendado es usar ${BOLD}Claude Code${RESET} (no requiere"
echo -e "  esta key). Solo complétala si prefieres usar la API de pago de Anthropic (console.anthropic.com)."
read -r -p "  sk-ant-... > " ANTHROPIC_API_KEY
[[ -z "$ANTHROPIC_API_KEY" ]] && ok "Sin API key (opción válida) — se usará scoring por keywords o Claude Code."
echo ""

while true; do
  ask "→ Número de teléfono para notificaciones WhatsApp (sin el +, ej: 56912345678):"
  read -r -p "  [56912345678] > " WHATSAPP_PHONE
  WHATSAPP_PHONE="${WHATSAPP_PHONE:-56912345678}"
  WHATSAPP_PHONE_CLEAN=$(echo "$WHATSAPP_PHONE" | tr -dc '0-9')
  if [[ ${#WHATSAPP_PHONE_CLEAN} -lt 10 ]]; then
    warn "Teléfono inválido. Debe contener al menos 10 dígitos con código de país (ej: 56912345678)."
  else
    WHATSAPP_PHONE="$WHATSAPP_PHONE_CLEAN"
    break
  fi
done
echo ""

while true; do
  ask "→ Correo Gmail para postulaciones automáticas (para portales que usan email):"
  read -r -p "  correo@gmail.com > " GMAIL_USER
  if [[ -z "$GMAIL_USER" ]]; then
    warn "Sin correo — las postulaciones por email no funcionarán. ¿Continuar sin correo? (s/N)"
    read -r -p "  > " SKIP_EMAIL
    SKIP_EMAIL_L=$(echo "$SKIP_EMAIL" | tr '[:upper:]' '[:lower:]')
    [[ "$SKIP_EMAIL_L" == "s" || "$SKIP_EMAIL_L" == "si" || "$SKIP_EMAIL_L" == "y" ]] && break
  elif [[ "$GMAIL_USER" =~ ^[^@]+@[^@]+\.[^@]+$ ]]; then
    break
  else
    warn "Correo inválido. Usa el formato correo@dominio.com"
  fi
done
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
ENV_FILE="$DOCKER_DIR/.env"

# Reutilizar la contraseña de Postgres si ya existe un .env. El volumen de la base de
# datos se inicializa con la contraseña de la PRIMERA instalación y NO cambia aunque el
# .env se regenere; generar una nueva rompería la autenticación del backend contra ese
# volumen ("password authentication failed for user wunen").
POSTGRES_PASSWORD=""
if [[ -f "$ENV_FILE" ]]; then
  POSTGRES_PASSWORD=$(grep -E '^POSTGRES_PASSWORD=' "$ENV_FILE" | head -1 | cut -d= -f2-)
fi
if [[ -n "$POSTGRES_PASSWORD" ]]; then
  log "Reutilizando POSTGRES_PASSWORD del .env existente (coincide con el volumen de la DB)"
else
  POSTGRES_PASSWORD=$(LC_ALL=C tr -dc 'A-Za-z0-9_' < /dev/urandom | head -c 24 2>/dev/null || echo "wunen_$(date +%s)")
fi

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

# Escribir settings.json para que la interfaz web muestre los datos inmediatamente
SETTINGS_JSON_PATH="$SCRIPT_DIR/documentos/settings.json"
mkdir -p "$SCRIPT_DIR/documentos"
if [[ ! -f "$SETTINGS_JSON_PATH" ]]; then
  cat > "$SETTINGS_JSON_PATH" << EOF
{
  "user_name": "${USER_NAME:-}",
  "whatsapp_phone": "${WHATSAPP_PHONE}",
  "notification_email": "${GMAIL_USER:-}",
  "reply_email": "${GMAIL_USER:-}"
}
EOF
  ok "settings.json creado (visible en Configuración de la web)"
else
  warn "settings.json ya existe — no se sobreescribe. Actualiza teléfono y correo desde la web en Configuración."
fi

# ─────────────────────────────────────────────────────────────────────────────
# 5. Validar puertos disponibles
# ─────────────────────────────────────────────────────────────────────────────
log "Verificando disponibilidad de puertos..."

check_port() {
  local port=$1
  local name=$2
  if lsof -iTCP:"$port" -sTCP:LISTEN -n -P &>/dev/null 2>&1; then
    warn "Puerto ${port} (${name}) ya está en uso:"
    lsof -iTCP:"$port" -sTCP:LISTEN -n -P 2>/dev/null | tail -1
    echo ""
    echo -e "  Opciones:"
    echo -e "  ${CYAN}a)${RESET} Detener el proceso que usa ese puerto"
    echo -e "  ${CYAN}b)${RESET} Editar docker/docker-compose.yml y cambiar el puerto del host"
    echo -e "  ${CYAN}c)${RESET} Continuar igual (puede fallar el servicio ${name})"
    read -r -p "  ¿Continuar de todas formas? (s/N) > " FORCE_PORT
    FORCE_PORT_L=$(echo "$FORCE_PORT" | tr '[:upper:]' '[:lower:]')
    [[ "$FORCE_PORT_L" != "s" && "$FORCE_PORT_L" != "si" && "$FORCE_PORT_L" != "y" ]] && \
      error "Instalación cancelada. Libera el puerto ${port} y vuelve a ejecutar install.sh"
  else
    ok "Puerto ${port} (${name}) disponible"
  fi
}

check_port "$FRONTEND_PORT" "frontend"
check_port "$BACKEND_PORT"  "backend"
check_port 8001             "scraper"
check_port 3001             "whatsapp"
check_port 5432             "postgres"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 6. Construir e iniciar servicios Docker
# ─────────────────────────────────────────────────────────────────────────────
echo ""
log "Construyendo e iniciando servicios Docker..."
echo -e "${YELLOW}  La primera vez puede tardar 5-15 minutos según tu conexión.${RESET}"
echo -e "${CYAN}  Verás el progreso de cada imagen a continuación:${RESET}"
echo ""

cd "$DOCKER_DIR"

log "[1/5] Descargando imagen de base de datos (PostgreSQL)..."
$COMPOSE_CMD pull db --quiet 2>/dev/null || true
ok "Imagen de base de datos lista"
echo ""

log "[2/5] Construyendo backend (Python/FastAPI)..."
$COMPOSE_CMD build backend
echo ""

log "[3/5] Construyendo scraper (Playwright)..."
$COMPOSE_CMD build scraper
echo ""

log "[4/5] Construyendo frontend (Next.js)..."
$COMPOSE_CMD build frontend
echo ""

log "[5/5] Construyendo servicio WhatsApp (Node.js + Chromium)..."
echo -e "${YELLOW}  Este paso instala Chromium y puede demorar más.${RESET}"
$COMPOSE_CMD build whatsapp
echo ""

log "Iniciando todos los servicios..."
$COMPOSE_CMD up -d
echo ""
ok "Servicios Docker iniciados"

# ─────────────────────────────────────────────────────────────────────────────
# 7. Esperar a que el backend esté listo
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
if curl -sf "http://localhost:${BACKEND_PORT}/health" > /dev/null 2>&1; then
  ok "Backend disponible en http://localhost:${BACKEND_PORT}"
elif $COMPOSE_CMD logs backend 2>/dev/null | grep -q "password authentication failed"; then
  # Volumen de DB de una instalación previa con OTRA contraseña: el backend no puede conectar.
  warn "El backend no pudo conectar a la base de datos: la contraseña no coincide."
  warn "Existe un volumen de Postgres de una instalación anterior con otra contraseña."
  echo -e "  ${BOLD}Para resetear la base de datos${RESET} (se borran ofertas/datos previos) ejecuta:"
  echo -e "    ${CYAN}cd \"$DOCKER_DIR\" && $COMPOSE_CMD down -v && $COMPOSE_CMD up -d${RESET}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 8. Configurar sesiones de portales (opcional)
# ─────────────────────────────────────────────────────────────────────────────
echo ""
sep
echo ""
ask "¿Deseas configurar ahora las sesiones de los portales con auto-postulación? (s/N)"
echo -e "  ${CYAN}Esto abrirá un navegador por cada portal para que puedas hacer login con Google.${RESET}"
read -r -p "  > " SETUP_SESSIONS
echo ""

SETUP_SESSIONS_L=$(echo "$SETUP_SESSIONS" | tr '[:upper:]' '[:lower:]')
if [[ "$SETUP_SESSIONS_L" == "s" || "$SETUP_SESSIONS_L" == "si" || "$SETUP_SESSIONS_L" == "y" || "$SETUP_SESSIONS_L" == "yes" ]]; then

  if [[ ! -d "$SETUP_DIR" ]]; then
    warn "No se encontró la carpeta setup/. Omitiendo configuración de sesiones."
    warn "Puedes hacerlo manualmente más tarde: ./setup-sessions.sh --lista"
  else
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
      warn "Python 3 no está instalado. No se pueden configurar sesiones ahora."
      warn "Instala Python 3 y luego ejecuta: ./setup-sessions.sh --lista"
    else
      cd "$SETUP_DIR"
      SETUP_DEPS_OK=true
      VENV_DIR="$SETUP_DIR/.venv"

      # Las dependencias de Playwright se instalan SIEMPRE dentro de un entorno
      # virtual (venv) para evitar el error PEP 668 "externally-managed-environment"
      # que rompe pip en macOS/Homebrew y Linux moderno.
      log "Preparando entorno virtual de Python (setup/.venv)..."
      if [[ ! -d "$VENV_DIR" ]]; then
        if ! python3 -m venv "$VENV_DIR" 2>/tmp/wunen_venv_err.log; then
          warn "No se pudo crear el venv. Detalle: $(tail -n 1 /tmp/wunen_venv_err.log)"
          warn "En Debian/Ubuntu instala: sudo apt install python3-venv"
          SETUP_DEPS_OK=false
        fi
      fi

      VENV_PY="$VENV_DIR/bin/python"

      if $SETUP_DEPS_OK; then
        log "Instalando dependencias de setup en el venv..."
        if ! "$VENV_PY" -m pip install -q --upgrade pip 2>/dev/null; then :; fi
        if ! "$VENV_PY" -m pip install -q -r requirements.txt 2>/tmp/wunen_pip_err.log; then
          warn "Falló pip install. Detalle: $(tail -n 1 /tmp/wunen_pip_err.log)"
          warn "Intenta manualmente: cd setup && ./run_setup.sh --lista"
          SETUP_DEPS_OK=false
        fi
      fi

      if $SETUP_DEPS_OK && ! "$VENV_PY" -c "import playwright" 2>/dev/null; then
        warn "El paquete 'playwright' no quedó instalado tras pip install."
        SETUP_DEPS_OK=false
      fi

      if $SETUP_DEPS_OK && ! "$VENV_PY" -m playwright install chromium 2>/tmp/wunen_pw_err.log; then
        warn "Falló playwright install. Detalle: $(tail -n 1 /tmp/wunen_pw_err.log)"
        warn "Intenta manualmente: cd setup && ./run_setup.sh --lista"
        SETUP_DEPS_OK=false
      fi

      if ! $SETUP_DEPS_OK; then
        warn "Omitiendo configuración de sesiones por dependencias faltantes."
        warn "Una vez resuelto, ejecuta: ./setup-sessions.sh --lista"
      else

      echo ""
      log "Portales disponibles para autenticar:"
      "$VENV_PY" setup_session.py --lista
      echo ""

      ask "¿Qué portales deseas autenticar? (Enter = todos los que falten, o escribe los nombres separados por coma)"
      echo -e "  ${CYAN}Ej: getonbrd, tecnoempleo   o presiona Enter para todos${RESET}"
      read -r -p "  > " PORTALES_INPUT
      echo ""

      if [[ -z "$PORTALES_INPUT" ]]; then
        # Autenticar todos los que no tienen sesión
        PORTALES_TO_AUTH=$("$VENV_PY" - << 'PYEOF'
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
        "$VENV_PY" setup_session.py "$portal" && ok "Sesión de ${portal} capturada" || warn "No se pudo capturar sesión de ${portal}"
      done

      echo ""
      ok "Proceso de autenticación completado"
      cd "$SCRIPT_DIR"
      fi
    fi
  fi
else
  echo -e "  Puedes configurar sesiones más tarde:"
  echo -e "  ${CYAN}./setup-sessions.sh --lista${RESET}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 9. Resumen final
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
echo -e "  ${BOLD}¿Cambiar teléfono o correo más tarde?${RESET}"
echo -e "    Puedes editarlos en cualquier momento desde:"
echo -e "    • La web → sección ${BOLD}Configuración${RESET}"
echo -e "    • O el archivo ${CYAN}${SCRIPT_DIR}/documentos/settings.json${RESET}"
echo ""
echo -e "  ${BOLD}Vincular WhatsApp (Baileys — notificaciones):${RESET}"
echo -e "    WhatsApp NO se configura en el instalador: requiere escanear un QR."
echo -e "    Ejecuta este script y escanea el QR con tu teléfono:"
echo -e "    ${CYAN}./whatsapp-qr.sh${RESET}              (local)"
echo -e "    ${CYAN}./whatsapp-qr.sh presto 3001${RESET}  (servidor remoto Presto)"
echo ""
echo -e "  ${BOLD}Correo Gmail de postulaciones:${RESET}"
echo -e "    Se pidió en este instalador. Para cambiarlo más tarde:"
echo -e "    ${CYAN}./setup-gmail.sh${RESET}"
echo ""
echo -e "  ${BOLD}Comandos útiles:${RESET}"
echo -e "    cd docker && docker compose logs -f"
echo -e "    cd docker && docker compose down"
echo -e "    ./setup-sessions.sh --lista          # estado de sesiones de portales"
echo -e "    ./whatsapp-qr.sh                     # vincular WhatsApp"
echo ""

# La API key de Anthropic es OPCIONAL — recordatorio amable, no una advertencia de error
if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo -e "  ${CYAN}ℹ  Sin Anthropic API key (es ${BOLD}opcional${RESET}${CYAN}):${RESET}"
  echo -e "     La evaluación de ofertas funciona igual con scoring básico por keywords."
  echo -e "     Para evaluación con IA tienes dos opciones:"
  echo -e "       • Usar ${BOLD}Claude Code${RESET} (recomendado — no requiere API key de pago), o"
  echo -e "       • Agregar ANTHROPIC_API_KEY en ${CYAN}docker/.env${RESET} y reiniciar el backend."
  echo ""
fi

# Comandos de Claude Code — se muestran siempre, por si el usuario tiene Claude instalado
echo -e "  ${BOLD}Si tienes Claude Code instalado, puedes usar estos comandos del proyecto:${RESET}"
echo -e "    ${CYAN}claude /valida <url>${RESET}   — verifica si un portal es automatizable"
echo -e "    ${CYAN}claude /autentica${RESET}      — configura sesiones de todos los portales"
echo ""
