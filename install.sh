#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Buscapega — Instalador
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
DIM='\033[2m'

# Paleta Buscapega (grafica/palette.scss) en truecolor. Los terminales que no soportan
# 24-bit ignoran la secuencia y caen al color por defecto, así que es seguro usarlas.
PINE='\033[38;2;41;115;115m'      # $pine-blue   #297373
ORANGE='\033[38;2;200;76;9m'      # $spicy-orange #c84c09
CELADON='\033[38;2;188;216;193m'  # $celadon     #bcd8c1
BLUSH='\033[38;2;250;216;214m'    # $soft-blush  #fad8d6
# Rojo y azul de la bandera chilena, para la insignia del robot
CL_RED='\033[38;2;213;43;30m'
CL_BLUE='\033[38;2;0;57;166m'
# El cantón azul lleva la estrella. Se pinta como FONDO azul + glifo blanco encima, en vez
# de un carácter azul: así la estrella queda recortada dentro del cuadro y no abre un hueco
# negro en el pecho del robot.
CL_BLUE_BG='\033[48;2;0;57;166m'
STAR_WHITE='\033[38;2;255;255;255m'

# Robot compacto: cabeza, cuerpo y piernas apilados y CONECTADOS (los hombros ┴ nacen
# bajo los lados de la cabeza; las piernas ┬ bajo el cuerpo; los brazos █ se adosan al
# cuerpo con ┤├). El pecho lleva la bandera chilena (azul+blanco / rojo). Solo caracteres
# de ancho 1 — se evitan ● ★ ▪ (East Asian Ambiguous), que muchos terminales pintan a
# doble ancho y descuadran el dibujo.
print_header() {
  echo ""
  echo -e "         ${PINE}╻${RESET}"
  echo -e "      ${PINE}╭──┴──╮${RESET}"
  echo -e "      ${PINE}│${RESET} ${CELADON}o${RESET} ${CELADON}o${RESET} ${PINE}│${RESET}"
  echo -e "      ${PINE}│${RESET}  ${BLUSH}‿${RESET}  ${PINE}│${RESET}"
  echo -e "     ${PINE}╭┴─────┴╮${RESET}"
  echo -e "    ${ORANGE}█${PINE}┤${RESET} ${CL_BLUE_BG}${STAR_WHITE}${BOLD}✦${RESET}${CL_BLUE_BG} ${RESET}${BLUSH}▀▀▀${RESET} ${PINE}├${ORANGE}█${RESET}"
  echo -e "    ${ORANGE}█${PINE}┤${RESET} ${CL_RED}▄▄▄▄▄${RESET} ${PINE}├${ORANGE}█${RESET}"
  echo -e "     ${PINE}╰─┬───┬─╯${RESET}"
  echo -e "       ${PINE}╹${RESET}   ${PINE}╹${RESET}"
  echo ""
  echo -e "          ${ORANGE}${BOLD}B U S C A P E G A${RESET}"
  echo -e "   ${CYAN}Automatización de búsqueda de empleo${RESET}"
  echo ""
  echo -e "   ${CL_BLUE}${BOLD}▌${RESET}${BOLD} Hecho desde Chile: ${CL_RED}Si es chileno, es bueno ${CL_BLUE}▐${RESET}"
  echo ""
}

log()   { echo -e "${CYAN}▶${RESET} $1"; }
ok()    { echo -e "${GREEN}✓${RESET} $1"; }
warn()  { echo -e "${YELLOW}!${RESET} $1"; }
error() { echo -e "${RED}✗ ERROR:${RESET} $1"; exit 1; }
ask()   { echo -e "${BOLD}$1${RESET}"; }
sep()   { echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"; }

# Error NO fatal (dato mal ingresado que se vuelve a preguntar). Antes esto usaba warn(),
# igual que los avisos informativos: ambos salían en amarillo con "!" y no se distinguía a
# primera vista que algo había fallado. Va en ROJO y con "✗", como error(), pero SIN exit:
# el bucle de validación vuelve a preguntar.
fail()  { echo -e "${RED}${BOLD}✗${RESET} ${RED}$1${RESET}"; }

# Información del paso que viene (p. ej. "esto instala Chromium y puede demorar"). Antes se
# imprimía en amarillo tenue y se perdía entre el ruido del build de Docker. Se marca con la
# barra naranja de la marca: contrasta sobre fondo negro mucho mejor que el azul, y no se
# confunde con el ▶ cian del paso ni con el ! amarillo de los avisos.
nota()  { echo -e "  ${ORANGE}${BOLD}▐${RESET} ${BOLD}$1${RESET}"; }

# ─────────────────────────────────────────────────────────────────────────────
# Red de seguridad: mensaje claro si el instalador termina antes de completarse
# ─────────────────────────────────────────────────────────────────────────────
# Antes, si algo cortaba el script (p. ej. `set -e` por una función que retornaba != 0),
# se salía a la terminal SIN avisar y el usuario no sabía si la instalación fue exitosa.
# Este trap se dispara en CUALQUIER salida: si no se llegó al final (REACHED_END=false),
# imprime un aviso inequívoco. Así siempre queda claro el resultado.
REACHED_END=false
on_exit() {
  local code=$?
  $REACHED_END && return 0
  echo ""
  echo -e "${RED}${BOLD}╔══════════════════════════════════════════╗${RESET}"
  echo -e "${RED}${BOLD}║      Instalación NO completada           ║${RESET}"
  echo -e "${RED}${BOLD}╚══════════════════════════════════════════╝${RESET}"
  echo -e "  El instalador se detuvo antes de terminar (código de salida: ${code})."
  echo -e "  Revisa el último mensaje o diagnóstico de más arriba."
  echo -e "  Vuelve a ejecutar ${CYAN}bash install.sh${RESET} — retomará donde quedó."
  echo ""
}
trap on_exit EXIT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$SCRIPT_DIR/docker"
DOCS_DIR="$SCRIPT_DIR/documentos"
SETUP_DIR="$SCRIPT_DIR/setup"

# ─────────────────────────────────────────────────────────────────────────────
# Estado de instalación (permite reanudar tras un fallo)
# ─────────────────────────────────────────────────────────────────────────────
# Cada paso costoso que termina bien se anota en este archivo. Si el instalador se
# corta a medias (típicamente durante un build de Docker), la siguiente ejecución
# ofrece saltarse lo ya hecho en vez de repetir 15 minutos de descargas.
STATE_FILE="$SCRIPT_DIR/.install-state"
LOG_DIR="$SCRIPT_DIR/.install-logs"
# Datos que el usuario ingresó (nombre, teléfono, correo, puertos…). Se guardan aquí para
# que al reanudar NO se vuelvan a pedir. Es un archivo de KEY='valor' que se puede 'source'.
CONFIG_FILE="$SCRIPT_DIR/.install-config"
RESUME=false

paso_hecho()   { [[ -f "$STATE_FILE" ]] && grep -qxF "$1" "$STATE_FILE"; }
marcar_paso()  { echo "$1" >> "$STATE_FILE"; }
# Se salta el paso solo si está marcado Y el usuario aceptó reanudar.
omitir_paso()  { $RESUME && paso_hecho "$1"; }

# Guarda la configuración ingresada con comillas seguras (soporta caracteres especiales en
# contraseñas). Al reanudar se lee con 'source' para no volver a preguntar.
guardar_config() {
  {
    for var in USER_NAME ANTHROPIC_API_KEY WHATSAPP_PHONE GMAIL_USER \
               GMAIL_APP_PASSWORD FRONTEND_PORT BACKEND_PORT; do
      printf '%s=%q\n' "$var" "${!var-}"
    done
  } > "$CONFIG_FILE"
  chmod 600 "$CONFIG_FILE" 2>/dev/null || true  # contiene la contraseña de Gmail
}

# ─────────────────────────────────────────────────────────────────────────────
# Diagnóstico de errores
# ─────────────────────────────────────────────────────────────────────────────
# Traduce el log de un build fallido a una causa concreta. Sin esto el usuario solo
# ve el volcado crudo de apt/npm/pip y no puede distinguir un problema de su equipo
# (sin disco, sin red) de un error real del proyecto.
diagnosticar_error() {
  local logfile="$1"
  local etiqueta="$2"
  [[ -f "$logfile" ]] || return 0

  echo ""
  echo -e "${RED}${BOLD}  ┌─ Diagnóstico ─────────────────────────────────────────┐${RESET}"

  if grep -qiE "unable to connect|could not connect|could not resolve|temporary failure in name resolution|connection timed out|network is unreachable|failed to fetch|TLS handshake timeout|i/o timeout" "$logfile"; then
    echo -e "${RED}  CAUSA: problema de RED (no es un error del proyecto).${RESET}"
    echo -e "    El build no pudo descargar paquetes desde internet."
    echo -e "    ${BOLD}Qué revisar:${RESET}"
    echo -e "      • Que tengas conexión:  ${CYAN}ping -c2 deb.debian.org${RESET}"
    echo -e "      • DNS de Docker: reinicia Docker Desktop, o agrega en"
    echo -e "        Settings → Docker Engine:  ${CYAN}\"dns\": [\"8.8.8.8\", \"1.1.1.1\"]${RESET}"
    echo -e "      • Si estás tras VPN/proxy corporativo, desactívalo y reintenta."
    echo -e "      • A veces el espejo de Debian falla un rato: reintenta en unos minutos."
    echo -e "    ${GREEN}Es seguro reintentar: el instalador retomará donde quedó.${RESET}"

  elif grep -qiE "no space left on device|disk quota exceeded|write error: no space" "$logfile"; then
    echo -e "${RED}  CAUSA: te quedaste sin ESPACIO EN DISCO.${RESET}"
    echo -e "    ${BOLD}Cómo liberar espacio de Docker:${RESET}"
    echo -e "      ${CYAN}docker system df${RESET}         # ver cuánto ocupa Docker"
    echo -e "      ${CYAN}docker system prune -a${RESET}   # borra imágenes/cachés sin usar"
    echo -e "    Docker Desktop además tiene un límite propio de disco en"
    echo -e "    Settings → Resources → Disk image size."

  elif grep -qiE "killed|out of memory|oom|cannot allocate memory|signal: killed|exit code: 137" "$logfile"; then
    echo -e "${RED}  CAUSA: el build se quedó sin MEMORIA (proceso terminado por el sistema).${RESET}"
    echo -e "    El build de frontend/WhatsApp es el que más RAM consume."
    echo -e "    ${BOLD}Qué hacer:${RESET}"
    echo -e "      • Docker Desktop → Settings → Resources → sube la memoria a 4 GB o más."
    echo -e "      • Cierra otras aplicaciones pesadas y reintenta."

  elif grep -qiE "permission denied|operation not permitted|eacces" "$logfile"; then
    echo -e "${RED}  CAUSA: problema de PERMISOS.${RESET}"
    echo -e "    ${BOLD}Qué revisar:${RESET}"
    echo -e "      • Que tu usuario pueda usar Docker:  ${CYAN}docker ps${RESET}"
    echo -e "      • En Linux, que estés en el grupo docker:"
    echo -e "        ${CYAN}sudo usermod -aG docker \$USER${RESET}  (y vuelve a iniciar sesión)"
    echo -e "      • Que tengas permiso de escritura en ${CYAN}${SCRIPT_DIR}${RESET}"

  elif grep -qiE "cannot connect to the docker daemon|docker daemon is not running|is the docker daemon running" "$logfile"; then
    echo -e "${RED}  CAUSA: el DAEMON de Docker se detuvo durante la instalación.${RESET}"
    echo -e "    Abre Docker Desktop, espera a que quede en verde y reintenta."

  elif grep -qiE "failed to prepare extraction snapshot|parent snapshot .* does not exist|snapshot .* does not exist|failed to prepare .* snapshot|content digest .* not found|no such file or directory.* snapshot" "$logfile"; then
    echo -e "${RED}  CAUSA: la caché de compilación de Docker (BuildKit) está CORRUPTA.${RESET}"
    echo -e "    No es un error del proyecto ni de tu código: a Docker se le dañó un"
    echo -e "    'snapshot' interno (suele pasar si un build previo se cortó a la mitad o"
    echo -e "    si dos builds corrieron a la vez sobre el mismo Docker)."
    echo -e "    ${BOLD}Cómo repararlo (de menos a más agresivo):${RESET}"
    echo -e "      ${CYAN}1.${RESET} Limpiar la caché de compilación:"
    echo -e "         ${CYAN}docker builder prune -af${RESET}"
    echo -e "      ${CYAN}2.${RESET} Si sigue: reinicia Docker Desktop (Quit y vuelve a abrir) y reintenta."
    echo -e "      ${CYAN}3.${RESET} Si aún persiste: limpieza profunda ${YELLOW}(borra imágenes sin usar)${RESET}:"
    echo -e "         ${CYAN}docker system prune -af${RESET}"
    echo -e "    ${GREEN}Luego vuelve a ejecutar el instalador: retomará donde quedó.${RESET}"

  else
    echo -e "${YELLOW}  CAUSA: no reconocida automáticamente.${RESET}"
    echo -e "    Probablemente sea un error real del proyecto y no de tu equipo."
    echo -e "    ${BOLD}Últimas líneas del log:${RESET}"
    grep -viE '^\s*$' "$logfile" | tail -12 | sed 's/^/      /'
  fi

  echo -e "${RED}${BOLD}  └───────────────────────────────────────────────────────┘${RESET}"
  echo ""
  echo -e "  ${BOLD}Log completo:${RESET} ${CYAN}${logfile}${RESET}"
  echo -e "  ${BOLD}Paso que falló:${RESET} ${etiqueta}"
  echo ""
  echo -e "  ${GREEN}${BOLD}Para reanudar, vuelve a ejecutar:${RESET} ${CYAN}bash install.sh${RESET}"
  echo -e "  Te ofrecerá continuar desde este punto sin repetir lo ya construido."
  echo ""
}

# Ejecuta un build de compose capturando la salida para poder diagnosticarla.
# Se usa `tee` para que el usuario siga viendo el progreso en vivo.
ejecutar_build() {
  local servicio="$1"
  local etiqueta="$2"
  local paso="build_${servicio}"

  if omitir_paso "$paso"; then
    ok "${etiqueta} — ya construido (omitido)"
    return 0
  fi

  mkdir -p "$LOG_DIR"
  local logfile="$LOG_DIR/build_${servicio}.log"

  # PIPESTATUS: con `| tee`, $? sería el estado de tee (siempre 0) y los fallos de
  # build pasarían desapercibidos.
  set +e
  $COMPOSE_CMD build "$servicio" 2>&1 | tee "$logfile"
  local estado=${PIPESTATUS[0]}
  set -e

  if [[ $estado -ne 0 ]]; then
    echo ""
    echo -e "${RED}✗ Falló la construcción de ${etiqueta}${RESET}"
    diagnosticar_error "$logfile" "$etiqueta"
    exit 1
  fi

  marcar_paso "$paso"
  return 0
}

print_header

# ─────────────────────────────────────────────────────────────────────────────
# 0. ¿Hay una instalación a medio terminar?
# ─────────────────────────────────────────────────────────────────────────────
if [[ -f "$STATE_FILE" ]]; then
  warn "Detecté una instalación anterior que no terminó."
  echo -e "  Pasos ya completados:"
  sed 's/^/      ✓ /' "$STATE_FILE"
  echo ""
  echo -e "  ${CYAN}a)${RESET} Continuar desde donde quedó (no repite los builds ya hechos)"
  echo -e "  ${CYAN}b)${RESET} Empezar de cero (reconstruye todo)"
  read -r -p "  ¿Continuar desde donde quedó? (S/n) > " RESP_RESUME
  RESP_RESUME_L=$(echo "$RESP_RESUME" | tr '[:upper:]' '[:lower:]')
  if [[ "$RESP_RESUME_L" == "n" || "$RESP_RESUME_L" == "no" ]]; then
    rm -f "$STATE_FILE" "$CONFIG_FILE"
    ok "Se reiniciará la instalación desde cero"
  else
    RESUME=true
    ok "Se reanudará la instalación"
  fi
  echo ""
fi

# ¿Hay datos ya ingresados de una ejecución anterior?
# OJO: esto va SEPARADO del bloque de arriba a propósito. Antes la reutilización de
# .install-config dependía de RESUME, y RESUME solo se activaba si existía STATE_FILE.
# Pero STATE_FILE solo aparece cuando termina el primer paso COSTOSO: si el instalador
# moría antes (p. ej. en el chequeo de puertos), quedaba un .install-config perfectamente
# válido que nunca se leía, y el cuestionario completo se repetía desde cero.
# Ahora los datos se reutilizan por sí solos, exista o no STATE_FILE, y se pueden cambiar
# sin obligar a "empezar de cero" (que además borraría los builds ya hechos).
USAR_CONFIG=false
if [[ -f "$CONFIG_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$CONFIG_FILE"
  ok "Encontré los datos que ingresaste antes:"
  echo -e "    • Nombre:   ${CYAN}${USER_NAME:-(sin definir)}${RESET}"
  echo -e "    • WhatsApp: ${CYAN}${WHATSAPP_PHONE:-(sin definir)}${RESET}"
  echo -e "    • Correo:   ${CYAN}${GMAIL_USER:-(sin definir)}${RESET}"
  echo -e "    • Puertos:  ${CYAN}web ${FRONTEND_PORT:-3000} / API ${BACKEND_PORT:-8000}${RESET}"
  echo ""
  read -r -p "  ¿Usar estos datos? (S/n, «n» los vuelve a preguntar) > " RESP_CFG
  RESP_CFG_L=$(echo "$RESP_CFG" | tr '[:upper:]' '[:lower:]')
  if [[ "$RESP_CFG_L" == "n" || "$RESP_CFG_L" == "no" ]]; then
    ok "Se volverán a pedir los datos"
  else
    USAR_CONFIG=true
    ok "Se reutilizan los datos anteriores"
  fi
  echo ""
fi

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

  Asegúrate de estar ejecutando install.sh desde la raíz del proyecto Buscapega."
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

# El binario existe, pero el daemon puede estar apagado (Docker Desktop cerrado).
# Sin daemon, los 'docker compose build/up' fallan más adelante con errores confusos.
if ! docker info &> /dev/null 2>&1; then
  error "Docker está instalado pero el daemon no responde.
  Inicia Docker Desktop (o el servicio docker) y vuelve a ejecutar install.sh."
fi
ok "Docker daemon activo"

# ── Recursos del sistema ─────────────────────────────────────────────────────
# Se comprueban ANTES de empezar: un build que muere a los 10 minutos por falta de
# disco o RAM es mucho más caro de diagnosticar que un aviso al inicio.

# Espacio libre en disco. Las imágenes completas (Playwright + Chromium + Node)
# rondan los 6 GB, así que por debajo de 10 GB el riesgo es real.
# `df -Pk` (bloques de 1K) es POSIX y funciona igual en macOS/BSD y Linux; `df -Pg`
# solo existe en BSD y en Linux devolvería basura.
ESPACIO_LIBRE_GB=$(df -Pk "$SCRIPT_DIR" 2>/dev/null | awk 'NR==2 {printf "%d", $4/1024/1024}')
if [[ -n "${ESPACIO_LIBRE_GB:-}" ]] && [[ "$ESPACIO_LIBRE_GB" =~ ^[0-9]+$ ]]; then
  if [[ $ESPACIO_LIBRE_GB -lt 5 ]]; then
    warn "Solo quedan ${ESPACIO_LIBRE_GB} GB libres en disco. Las imágenes ocupan ~6 GB."
    warn "Libera espacio (${CYAN}docker system prune -a${RESET}) o el build fallará a mitad de camino."
    read -r -p "  ¿Continuar de todas formas? (s/N) > " SEGUIR_DISCO
    SEGUIR_DISCO_L=$(echo "$SEGUIR_DISCO" | tr '[:upper:]' '[:lower:]')
    [[ "$SEGUIR_DISCO_L" != "s" && "$SEGUIR_DISCO_L" != "si" && "$SEGUIR_DISCO_L" != "y" ]] && \
      error "Instalación cancelada por falta de espacio en disco."
  elif [[ $ESPACIO_LIBRE_GB -lt 10 ]]; then
    warn "Quedan ${ESPACIO_LIBRE_GB} GB libres — justo. Las imágenes ocupan ~6 GB."
  else
    ok "Espacio en disco disponible: ${ESPACIO_LIBRE_GB} GB"
  fi
fi

# Memoria asignada a Docker. Con menos de 2 GB el build de frontend/WhatsApp suele
# morir por OOM (exit 137), que se ve como un fallo inexplicable.
DOCKER_MEM_BYTES=$(docker info --format '{{.MemTotal}}' 2>/dev/null || echo "")
if [[ -n "$DOCKER_MEM_BYTES" ]] && [[ "$DOCKER_MEM_BYTES" =~ ^[0-9]+$ ]]; then
  DOCKER_MEM_GB=$((DOCKER_MEM_BYTES / 1024 / 1024 / 1024))
  if [[ $DOCKER_MEM_GB -lt 2 ]]; then
    warn "Docker tiene solo ${DOCKER_MEM_GB} GB de memoria asignada."
    warn "El build de frontend/WhatsApp puede morir por falta de memoria (exit 137)."
    warn "Súbela en Docker Desktop → Settings → Resources → Memory (4 GB recomendado)."
  else
    ok "Memoria disponible para Docker: ${DOCKER_MEM_GB} GB"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# 3. Configuración interactiva
# ─────────────────────────────────────────────────────────────────────────────
# Si el usuario aceptó reutilizar los datos guardados (paso 0), ya están cargados en las
# variables y se omite todo el cuestionario. Si dijo que no, o no había .install-config,
# se pregunta normalmente.
if $USAR_CONFIG; then
  echo ""
  echo -e "${BOLD}Configuración inicial${RESET}"
  sep
  ok "Se usan los datos que confirmaste más arriba — no se vuelven a pedir."
  echo -e "  ${CYAN}Para cambiarlos: vuelve a ejecutar el instalador y responde «n»${RESET}"
  echo -e "  ${CYAN}en «¿Usar estos datos?», o edítalos desde la web en Configuración.${RESET}"
  echo ""
else
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
  echo -e "  ${CYAN}Aquí solo se guarda el número. La vinculación se hace DESPUÉS escaneando${RESET}"
  echo -e "  ${CYAN}un QR: al terminar la instalación ejecuta ./configuraciones/vincular-whatsapp.sh y escanéalo.${RESET}"
  read -r -p "  [56912345678] > " WHATSAPP_PHONE
  WHATSAPP_PHONE="${WHATSAPP_PHONE:-56912345678}"
  WHATSAPP_PHONE_CLEAN=$(echo "$WHATSAPP_PHONE" | tr -dc '0-9')
  if [[ ${#WHATSAPP_PHONE_CLEAN} -lt 10 ]]; then
    fail "Teléfono inválido. Debe contener al menos 10 dígitos con código de país (ej: 56912345678)."
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
    fail "Correo inválido. Usa el formato correo@dominio.com"
  fi
done
echo ""

GMAIL_APP_PASSWORD=""
if [[ -n "$GMAIL_USER" ]]; then
  ask "→ Contraseña de aplicación Gmail  [OPCIONAL — Enter para omitir]:"
  echo -e "  ${CYAN}Son 16 caracteres, sin espacios.${RESET} Se obtiene en:"
  echo -e "  ${CYAN}https://myaccount.google.com/apppasswords${RESET}"
  echo -e "  Puedes dejarla vacía ahora y agregarla después con"
  echo -e "  ${CYAN}./configuraciones/setup-gmail.sh${RESET} o desde la web en Configuración."
  read -r -p "  > " GMAIL_APP_PASSWORD
  if [[ -z "$GMAIL_APP_PASSWORD" ]]; then
    warn "Sin contraseña de aplicación — las postulaciones por correo quedarán desactivadas."
    warn "La web te lo recordará en Configuración hasta que la agregues."
  else
    # Google la muestra en bloques de 4 ("abcd efgh ijkl mnop"); al pegarla se copian los
    # espacios y el login SMTP falla con "Username and Password not accepted".
    GMAIL_APP_PASSWORD="${GMAIL_APP_PASSWORD// /}"
    if [[ ${#GMAIL_APP_PASSWORD} -ne 16 ]]; then
      warn "La contraseña tiene ${#GMAIL_APP_PASSWORD} caracteres y se esperaban 16."
      warn "Se guardará igual, pero si el envío falla revísala con ./configuraciones/setup-gmail.sh"
    fi
  fi
  echo ""
fi

ask "→ Puerto para la interfaz web:"
read -r -p "  [3000] > " FRONTEND_PORT
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

ask "→ Puerto para el API backend:"
read -r -p "  [8000] > " BACKEND_PORT
BACKEND_PORT="${BACKEND_PORT:-8000}"
echo ""

# Persistir lo ingresado para no volver a preguntarlo si hay que reanudar tras un fallo.
guardar_config
fi

# ─────────────────────────────────────────────────────────────────────────────
# 4. Generar archivo .env
# ─────────────────────────────────────────────────────────────────────────────
ENV_FILE="$DOCKER_DIR/.env"

# ¿Existía ya un .env al iniciar? Se usa más abajo para detectar el caso peligroso de
# "volumen de DB sin .env" (clon nuevo sobre datos viejos → contraseña irrecuperable).
ENV_PREEXISTING=false
[[ -f "$ENV_FILE" ]] && ENV_PREEXISTING=true

# Reutilizar la contraseña de Postgres si ya existe un .env. El volumen de la base de
# datos se inicializa con la contraseña de la PRIMERA instalación y NO cambia aunque el
# .env se regenere; generar una nueva rompería la autenticación del backend contra ese
# volumen ("password authentication failed for user buscapega").
POSTGRES_PASSWORD=""
if [[ -f "$ENV_FILE" ]]; then
  POSTGRES_PASSWORD=$(grep -E '^POSTGRES_PASSWORD=' "$ENV_FILE" | head -1 | cut -d= -f2-)
fi
if [[ -n "$POSTGRES_PASSWORD" ]]; then
  log "Reutilizando POSTGRES_PASSWORD del .env existente (coincide con el volumen de la DB)"
else
  # `head -c 24` cierra el pipe y `tr` recibe SIGPIPE (exit 141). El `|| true` evita que
  # `set -o pipefail` aborte el script y, sobre todo, que el fallback se concatene al
  # valor aleatorio (antes salía "<aleatorio>buscapega_<timestamp>" en un mismo string).
  POSTGRES_PASSWORD="$(LC_ALL=C tr -dc 'A-Za-z0-9_' < /dev/urandom 2>/dev/null | head -c 24 || true)"
  [[ -z "$POSTGRES_PASSWORD" ]] && POSTGRES_PASSWORD="buscapega_$(date +%s)"
fi

[[ -f "$ENV_FILE" ]] && cp "$ENV_FILE" "$ENV_FILE.bak" && warn "Backup del .env anterior guardado como .env.bak"

log "Generando archivo de configuración..."
cat > "$ENV_FILE" << EOF
# Generado por install.sh — $(date)

POSTGRES_DB=buscapega
POSTGRES_USER=buscapega
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}

NEXT_PUBLIC_API_URL=http://localhost:${BACKEND_PORT}
ENVIRONMENT=production

WHATSAPP_DEFAULT_PHONE=${WHATSAPP_PHONE}
WHATSAPP_PAIRING_PHONE=${WHATSAPP_PHONE}

GMAIL_USER=${GMAIL_USER:-}
GMAIL_APP_PASSWORD=${GMAIL_APP_PASSWORD:-}
GMAIL_FROM_NAME=Buscapega

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

# ── Restos de la versión anterior, cuando el proyecto se llamaba "wunen" ──────
# El proyecto de compose pasó de `wunen` a `buscapega`. Ese nombre prefija contenedores
# y volúmenes, así que los `wunen_*` de una instalación anterior NO se reutilizan ni se
# borran solos: quedan ocupando puertos y espacio, y confunden en `docker ps`. Se ofrece
# limpiarlos. Los volúmenes viejos contienen la base de datos, las cookies de sesión y la
# vinculación de WhatsApp anteriores; con el cambio de nombre ya no se leen, y se parte
# limpio (decisión tomada al planificar el rebranding).
LEGADO_CONT=$(docker ps -a --filter "name=wunen_" --format "{{.Names}}" 2>/dev/null || true)
LEGADO_VOL=$(docker volume ls --format '{{.Name}}' 2>/dev/null | grep -E '^wunen_' || true)
if [[ -n "$LEGADO_CONT" || -n "$LEGADO_VOL" ]]; then
  warn "Encontré restos de la versión anterior del proyecto (se llamaba «wunen»):"
  # `|| true`: sin él, un `[[ ]] && …` falso devuelve 1 y bajo `set -e` puede cortar el
  # instalador (el bug de la ronda 3). Aquí solo listamos, nunca debe abortar.
  [[ -n "$LEGADO_CONT" ]] && echo "$LEGADO_CONT" | sed 's/^/      • contenedor  /' || true
  [[ -n "$LEGADO_VOL" ]]  && echo "$LEGADO_VOL"  | sed 's/^/      • volumen     /' || true
  echo ""
  echo -e "  Ahora los contenedores se llaman ${CYAN}buscapega_*${RESET}, así que estos ya no se usan."
  nota "Los volúmenes «wunen» guardan la base de datos, las sesiones de los portales y"
  nota "la vinculación de WhatsApp ANTERIORES. Al borrarlos habrá que volver a capturar"
  nota "las sesiones y a escanear el QR de WhatsApp."
  echo ""
  read -r -p "  ¿Eliminar los restos de «wunen»? (s/N) > " LIMPIAR_LEGADO
  LIMPIAR_LEGADO_L=$(echo "$LIMPIAR_LEGADO" | tr '[:upper:]' '[:lower:]')
  if [[ "$LIMPIAR_LEGADO_L" == "s" || "$LIMPIAR_LEGADO_L" == "si" || "$LIMPIAR_LEGADO_L" == "y" ]]; then
    if [[ -n "$LEGADO_CONT" ]]; then
      echo "$LEGADO_CONT" | xargs -r docker rm -f >/dev/null 2>&1 || true
      ok "Contenedores «wunen» eliminados"
    fi
    if [[ -n "$LEGADO_VOL" ]]; then
      # Si algún volumen sigue en uso, docker se niega: se informa en vez de fallar.
      if echo "$LEGADO_VOL" | xargs -r docker volume rm >/dev/null 2>&1; then
        ok "Volúmenes «wunen» eliminados"
      else
        fail "Algún volumen «wunen» no se pudo eliminar (¿lo usa un contenedor en marcha?)."
        warn "Puedes borrarlos luego con: docker volume rm \$(docker volume ls -q -f name=wunen_)"
      fi
    fi
  else
    warn "Se conservan. Ocuparán espacio y sus puertos pueden chocar con los nuevos."
    warn "Para borrarlos después: docker rm -f \$(docker ps -aq -f name=wunen_)"
  fi
  echo ""
fi

# Detectar una instalación previa de Buscapega (contenedores ya creados o corriendo).
# Sirve para no asustar con falsos "puerto en uso" cuando el puerto lo ocupa el
# propio Buscapega: en ese caso es una reinstalación y 'compose up -d' lo recrea.
BUSCAPEGA_EXISTING=$(docker ps -a --filter "name=buscapega_" --format "{{.Names}}" 2>/dev/null || true)
if [[ -n "$BUSCAPEGA_EXISTING" ]]; then
  warn "Detecté una instalación previa de Buscapega (contenedores existentes):"
  echo "$BUSCAPEGA_EXISTING" | sed 's/^/      • /'
  echo -e "  ${CYAN}Se recrearán con la nueva configuración al iniciar los servicios.${RESET}"
  echo -e "  ${CYAN}Tus datos (base de datos, cookies) se conservan en los volúmenes.${RESET}"
  echo ""
fi

# Volumen de base de datos huérfano: existe el volumen de Postgres de una instalación
# previa pero NO había un docker/.env que conserve su contraseña (caso típico: clon nuevo
# sobre datos viejos, o se borró el .env). El volumen guarda la contraseña ORIGINAL, pero
# install.sh acaba de generar una NUEVA → el backend fallará con "password authentication
# failed". Sin el .env original esa contraseña es irrecuperable: hay que resetear el
# volumen o restaurar el .env. (Si el .env preexistía, su contraseña se reutiliza arriba y
# no hay conflicto, así que no preguntamos.)
DB_VOLUME_HUERFANO=$(docker volume ls --format '{{.Name}}' 2>/dev/null | grep -Fx "buscapega_db_data" || true)
if [[ -n "$DB_VOLUME_HUERFANO" && "$ENV_PREEXISTING" == "false" ]]; then
  warn "Detecté un volumen de base de datos de una instalación anterior (buscapega_db_data)"
  echo -e "  pero no hay un ${CYAN}docker/.env${RESET} que conserve su contraseña. La contraseña nueva"
  echo -e "  generada NO coincidirá con la del volumen y el backend no podrá autenticar."
  echo ""
  echo -e "  ${CYAN}a)${RESET} Resetear la base de datos (borra ofertas/datos previos del volumen)"
  echo -e "  ${CYAN}b)${RESET} Conservar el volumen (deberás restaurar el docker/.env original a mano)"
  read -r -p "  ¿Resetear la base de datos para una instalación limpia? (s/N) > " RESET_DB
  RESET_DB_L=$(echo "$RESET_DB" | tr '[:upper:]' '[:lower:]')
  if [[ "$RESET_DB_L" == "s" || "$RESET_DB_L" == "si" || "$RESET_DB_L" == "y" ]]; then
    log "Eliminando volumen buscapega_db_data..."
    if docker volume rm buscapega_db_data >/dev/null 2>&1; then
      ok "Volumen eliminado — la base de datos se creará limpia con la nueva contraseña"
    else
      fail "No se pudo eliminar el volumen (¿lo usa un contenedor en marcha?)."
      warn "Detén Buscapega y reintenta: cd \"$DOCKER_DIR\" && $COMPOSE_CMD down -v"
    fi
  else
    warn "Conservando el volumen. Si el backend falla con 'password authentication failed',"
    warn "restaura el docker/.env original o ejecuta: cd \"$DOCKER_DIR\" && $COMPOSE_CMD down -v && $COMPOSE_CMD up -d"
  fi
  echo ""
fi

check_port() {
  local port=$1
  local name=$2
  if lsof -iTCP:"$port" -sTCP:LISTEN -n -P &>/dev/null 2>&1; then
    # ¿El puerto lo ocupa un contenedor de Buscapega ya corriendo? Entonces es una
    # reinstalación, no un conflicto real: 'compose up -d' recreará el contenedor.
    if docker ps --format '{{.Names}} {{.Ports}}' 2>/dev/null | grep -qE "^buscapega_.*:${port}->"; then
      ok "Puerto ${port} (${name}) lo usa tu Buscapega actual — se recreará al reiniciar"
      return
    fi
    fail "Puerto ${port} (${name}) ya está en uso."
    # Antes solo se volcaba la línea cruda de lsof, ilegible sin encabezado. Se extrae
    # el proceso concreto: nombre, PID, usuario y —si es un contenedor— su nombre.
    local pinfo pcmd ppid puser cont
    pinfo=$(lsof -iTCP:"$port" -sTCP:LISTEN -n -P 2>/dev/null | awk 'NR==2 {print $1"|"$2"|"$3}')
    if [[ -n "$pinfo" ]]; then
      pcmd=${pinfo%%|*}; ppid=$(echo "$pinfo" | cut -d'|' -f2); puser=${pinfo##*|}
      echo -e "    Lo ocupa: ${BOLD}${pcmd}${RESET} (PID ${BOLD}${ppid}${RESET}, usuario ${puser})"
      # Si el puerto lo publica Docker, el PID es del proxy y no dice nada útil:
      # se busca el contenedor que realmente lo expone.
      cont=$(docker ps --format '{{.Names}} {{.Ports}}' 2>/dev/null | grep -E ":${port}->" | awk '{print $1}' | head -1 || true)
      # if explícito en vez de `[[ ]] && echo`: ese idiom devuelve 1 cuando la condición es
      # falsa y, si alguna vez queda como última línea de la función, `set -e` mataría el
      # instalador en silencio (es el bug que se corrigió en la ronda 3).
      if [[ -n "$cont" ]]; then
        # OJO: aquí NO se sugiere `kill $ppid`. Cuando el puerto lo publica Docker, ese PID
        # es el proxy de Docker Desktop (com.docker.backend), COMPARTIDO por todos los
        # contenedores: matarlo tumbaría Docker entero, no solo este servicio. Lo correcto
        # es detener el contenedor concreto.
        echo -e "    Contenedor Docker: ${BOLD}${cont}${RESET}"
        echo -e "    Para liberarlo:  ${CYAN}docker stop ${cont}${RESET}"
      # `com.dock*` y no `com.docker*`: lsof trunca la columna COMMAND a 9 caracteres, así
      # que "com.docker.backend" llega como "com.docke" y el patrón más largo nunca casaría.
      elif [[ "$pcmd" == com.dock* || "$pcmd" == docker* || "$pcmd" == Docker* ]]; then
        # Lo publica Docker pero no se pudo resolver qué contenedor (p. ej. lo expone un
        # compose ajeno). Tampoco aquí sirve matar el PID.
        echo -e "    Lo publica Docker, pero no pude identificar el contenedor."
        echo -e "    Búscalo con:     ${CYAN}docker ps --filter publish=${port}${RESET}"
      else
        echo -e "    Para liberarlo:  ${CYAN}kill ${ppid}${RESET}"
      fi
    fi
    echo ""
    echo -e "  Opciones:"
    echo -e "  ${CYAN}a)${RESET} Detener el proceso que usa ese puerto"
    echo -e "  ${CYAN}b)${RESET} Editar docker/docker-compose.yml y cambiar el puerto del host"
    echo -e "  ${CYAN}c)${RESET} Continuar igual (puede fallar el servicio ${name})"
    read -r -p "  ¿Continuar de todas formas? (s/N) > " FORCE_PORT
    FORCE_PORT_L=$(echo "$FORCE_PORT" | tr '[:upper:]' '[:lower:]')
    # OJO: NO usar `[[ cond ]] && error` como última línea de la función. Cuando el usuario
    # SÍ continúa, el `[[ ]]` es falso → la función retornaría 1 y, con `set -e`, el llamador
    # `check_port ...` mataría el script EN SILENCIO (antes de `compose up` y del resumen).
    # Por eso va un if explícito y un `return 0` al final que garantiza éxito al continuar.
    if [[ "$FORCE_PORT_L" != "s" && "$FORCE_PORT_L" != "si" && "$FORCE_PORT_L" != "y" ]]; then
      error "Instalación cancelada. Libera el puerto ${port} y vuelve a ejecutar install.sh"
    fi
    warn "Continuando con el puerto ${port} en uso — el servicio ${name} podría no levantar."
  else
    ok "Puerto ${port} (${name}) disponible"
  fi
  return 0
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
nota "La primera vez puede tardar 5-15 minutos según tu conexión."
echo -e "${CYAN}  Verás el progreso de cada imagen a continuación:${RESET}"
echo ""

cd "$DOCKER_DIR"

log "[1/5] Descargando imagen de base de datos (PostgreSQL)..."
$COMPOSE_CMD pull db --quiet 2>/dev/null || true
ok "Imagen de base de datos lista"
echo ""

log "[2/5] Construyendo backend (Python/FastAPI)..."
ejecutar_build backend "backend (Python/FastAPI)"
echo ""

log "[3/5] Construyendo scraper (Playwright)..."
ejecutar_build scraper "scraper (Playwright)"
echo ""

log "[4/5] Construyendo frontend (Next.js)..."
ejecutar_build frontend "frontend (Next.js)"
echo ""

log "[5/5] Construyendo servicio WhatsApp (Node.js + Chromium)..."
nota "Este paso instala Chromium y puede demorar más."
ejecutar_build whatsapp "servicio WhatsApp (Node.js + Chromium)"
echo ""

log "Iniciando todos los servicios..."
mkdir -p "$LOG_DIR"
set +e
$COMPOSE_CMD up -d 2>&1 | tee "$LOG_DIR/up.log"
UP_ESTADO=${PIPESTATUS[0]}
set -e
if [[ $UP_ESTADO -ne 0 ]]; then
  echo ""
  echo -e "${RED}✗ Los servicios no pudieron iniciarse${RESET}"
  diagnosticar_error "$LOG_DIR/up.log" "arranque de los servicios (compose up)"
  exit 1
fi
echo ""
ok "Servicios Docker iniciados"
marcar_paso "servicios_iniciados"

# ─────────────────────────────────────────────────────────────────────────────
# 7. Esperar a que el backend esté listo
# ─────────────────────────────────────────────────────────────────────────────
log "Esperando a que el backend esté listo..."
MAX_WAIT=60
WAITED=0
BACKEND_OK=false
until curl -sf "http://localhost:${BACKEND_PORT}/health" > /dev/null 2>&1; do
  if [[ $WAITED -ge $MAX_WAIT ]]; then
    break
  fi
  printf "."
  sleep 2
  WAITED=$((WAITED + 2))
done
echo ""
if curl -sf "http://localhost:${BACKEND_PORT}/health" > /dev/null 2>&1; then
  BACKEND_OK=true
  ok "Backend disponible en http://localhost:${BACKEND_PORT}"
elif $COMPOSE_CMD logs backend 2>/dev/null | grep -q "password authentication failed"; then
  # Volumen de DB de una instalación previa con OTRA contraseña: el backend no puede conectar.
  warn "El backend NO está disponible: la contraseña de Postgres no coincide con el volumen."
  warn "Existe un volumen de una instalación anterior (buscapega_db_data) con otra contraseña."
  echo -e "  ${BOLD}Para resetear la base de datos${RESET} (se borran ofertas/datos previos) ejecuta:"
  echo -e "    ${CYAN}cd \"$DOCKER_DIR\" && $COMPOSE_CMD down -v && $COMPOSE_CMD up -d${RESET}"
else
  # El backend no respondió y no es un problema de contraseña conocido: apuntar a los logs.
  warn "El backend no respondió en ${MAX_WAIT}s y no está sano. Revisa los logs:"
  echo -e "    ${CYAN}cd \"$DOCKER_DIR\" && $COMPOSE_CMD logs backend${RESET}"
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
    warn "Puedes hacerlo manualmente más tarde: ./configuraciones/setup-sessions.sh --lista"
  else
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
      warn "Python 3 no está instalado. No se pueden configurar sesiones ahora."
      warn "Instala Python 3 y luego ejecuta: ./configuraciones/setup-sessions.sh --lista"
    else
      cd "$SETUP_DIR"
      SETUP_DEPS_OK=true
      VENV_DIR="$SETUP_DIR/.venv"

      # Las dependencias de Playwright se instalan SIEMPRE dentro de un entorno
      # virtual (venv) para evitar el error PEP 668 "externally-managed-environment"
      # que rompe pip en macOS/Homebrew y Linux moderno.
      log "Preparando entorno virtual de Python (setup/.venv)..."
      if [[ ! -d "$VENV_DIR" ]]; then
        if ! python3 -m venv "$VENV_DIR" 2>/tmp/buscapega_venv_err.log; then
          fail "No se pudo crear el venv. Detalle: $(tail -n 1 /tmp/buscapega_venv_err.log)"
          warn "En Debian/Ubuntu instala: sudo apt install python3-venv"
          SETUP_DEPS_OK=false
        fi
      fi

      VENV_PY="$VENV_DIR/bin/python"

      if $SETUP_DEPS_OK; then
        log "Instalando dependencias de setup en el venv..."
        if ! "$VENV_PY" -m pip install -q --upgrade pip 2>/dev/null; then :; fi
        if ! "$VENV_PY" -m pip install -q -r requirements.txt 2>/tmp/buscapega_pip_err.log; then
          warn "Falló pip install. Detalle: $(tail -n 1 /tmp/buscapega_pip_err.log)"
          warn "Intenta manualmente: ./configuraciones/instalar_dependencias_python.sh"
          SETUP_DEPS_OK=false
        fi
      fi

      if $SETUP_DEPS_OK && ! "$VENV_PY" -c "import playwright" 2>/dev/null; then
        warn "El paquete 'playwright' no quedó instalado tras pip install."
        SETUP_DEPS_OK=false
      fi

      if $SETUP_DEPS_OK && ! "$VENV_PY" -m playwright install chromium 2>/tmp/buscapega_pw_err.log; then
        warn "Falló playwright install. Detalle: $(tail -n 1 /tmp/buscapega_pw_err.log)"
        warn "Intenta manualmente: ./configuraciones/instalar_dependencias_python.sh"
        SETUP_DEPS_OK=false
      fi

      if ! $SETUP_DEPS_OK; then
        warn "Omitiendo configuración de sesiones por dependencias faltantes."
        warn "Una vez resuelto, ejecuta: ./configuraciones/setup-sessions.sh --lista"
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
        nota "Se abrirá el navegador — completa el login con Google y ciérralo cuando termines."
        "$VENV_PY" setup_session.py "$portal" && ok "Sesión de ${portal} capturada" || fail "No se pudo capturar sesión de ${portal}"
      done

      echo ""
      ok "Proceso de autenticación completado"
      cd "$SCRIPT_DIR"
      fi
    fi
  fi
else
  echo -e "  Puedes configurar sesiones más tarde:"
  echo -e "  ${CYAN}./configuraciones/setup-sessions.sh --lista${RESET}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 9. Resumen final
# ─────────────────────────────────────────────────────────────────────────────
echo ""
if [[ "${BACKEND_OK:-false}" == "true" ]]; then
  # La instalación llegó al final con el backend sano: se descarta el estado (incluida la
  # config con la contraseña de Gmail) para que la próxima ejecución sea limpia y no ofrezca
  # "reanudar".
  rm -f "$STATE_FILE" "$CONFIG_FILE"
  rm -rf "$LOG_DIR"
  echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════╗${RESET}"
  echo -e "${GREEN}${BOLD}║         Instalación completada           ║${RESET}"
  echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════╝${RESET}"
  echo ""
  # URL del administrador, bien destacada: es lo primero que el usuario necesita saber.
  echo -e "  ${GREEN}${BOLD}👉  Abre el administrador en tu navegador:${RESET}"
  echo -e "      ${CYAN}${BOLD}http://localhost:${FRONTEND_PORT}${RESET}"
else
  echo -e "${YELLOW}${BOLD}╔══════════════════════════════════════════╗${RESET}"
  echo -e "${YELLOW}${BOLD}║   Instalación incompleta — backend caído ║${RESET}"
  echo -e "${YELLOW}${BOLD}╚══════════════════════════════════════════╝${RESET}"
  echo ""
  echo -e "  ${YELLOW}Los servicios se levantaron, pero el backend (${BACKEND_PORT}) no responde /health.${RESET}"
  echo -e "  ${YELLOW}Revisa el aviso de más arriba antes de usar la interfaz web.${RESET}"
  echo ""
  echo -e "  Cuando el backend responda, el administrador estará en:"
  echo -e "      ${CYAN}${BOLD}http://localhost:${FRONTEND_PORT}${RESET}"
fi
echo ""
echo -e "  ${BOLD}Interfaz web (administrador):${RESET}  http://localhost:${FRONTEND_PORT}"
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
echo -e "    ${CYAN}./configuraciones/vincular-whatsapp.sh${RESET}"
echo ""
echo -e "  ${BOLD}Correo Gmail de postulaciones:${RESET}"
echo -e "    Se pidió en este instalador. Para cambiarlo más tarde:"
echo -e "    ${CYAN}./configuraciones/setup-gmail.sh${RESET}"
echo ""
echo -e "  ${BOLD}Comandos útiles:${RESET}"
echo -e "    cd docker && docker compose logs -f"
echo -e "    cd docker && docker compose down"
echo -e "    ./configuraciones/setup-sessions.sh --lista          # estado de sesiones de portales"
echo -e "    ./configuraciones/vincular-whatsapp.sh                     # vincular WhatsApp"
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

# El script llegó al final de forma normal: el trap on_exit NO debe mostrar el aviso de
# "instalación no completada". (El resumen de arriba ya indicó si el backend quedó sano.)
REACHED_END=true
