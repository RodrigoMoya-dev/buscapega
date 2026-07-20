#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Buscapega — Smoke test / validación post-cambios
#
# Verifica que NO se haya roto nada después de un cambio. Dos fases:
#   1) Estáticas (no requieren servicios levantados):
#        · sintaxis de todos los scripts bash (bash -n)
#        · shellcheck (si está instalado)
#        · validez del docker-compose.yml (docker compose config -q)
#        · validez del JSON de documentos/settings.json (si existe)
#   2) Dinámicas (requieren los contenedores corriendo):
#        · backend  /health        (HTTP 200)
#        · scraper  /health        (HTTP 200)
#        · frontend /              (HTTP 200)
#        · backend  /api/settings  (devuelve user_name)
#
# Uso:
#   ./configuraciones/smoke-test.sh                 # local (puertos por defecto)
#   ./configuraciones/smoke-test.sh --presto        # presto (frontend 3020, backend 8020, scraper 8021)
#   ./configuraciones/smoke-test.sh --static        # solo fase estática (sin servicios)
#   HOST=192.168.100.6 ./configuraciones/smoke-test.sh   # host remoto con puertos por defecto
#
# Variables de entorno (sobre-escriben los defaults):
#   HOST, BACKEND_PORT, SCRAPER_PORT, FRONTEND_PORT
#
# Código de salida: 0 = todo OK, 1 = al menos una verificación falló.
# ─────────────────────────────────────────────────────────────────────────────
set -uo pipefail

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
RED='\033[0;31m'; RESET='\033[0m'; BOLD='\033[1m'

log()  { echo -e "${CYAN}▶${RESET} $1"; }
ok()   { echo -e "${GREEN}✓${RESET} $1"; }
warn() { echo -e "${YELLOW}!${RESET} $1"; }
bad()  { echo -e "${RED}✗${RESET} $1"; }
sep()  { echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Configuración de host/puertos ────────────────────────────────────────────
HOST="${HOST:-localhost}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
SCRAPER_PORT="${SCRAPER_PORT:-8001}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
STATIC_ONLY=0

for arg in "$@"; do
  case "$arg" in
    --presto)
      HOST="${HOST_PRESTO:-192.168.100.6}"
      BACKEND_PORT=8020; SCRAPER_PORT=8021; FRONTEND_PORT=3020 ;;
    --static) STATIC_ONLY=1 ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) warn "Argumento desconocido: $arg" ;;
  esac
done

PASS=0; FAIL=0
check_pass() { ok "$1"; PASS=$((PASS+1)); }
check_fail() { bad "$1"; FAIL=$((FAIL+1)); }

echo ""
echo -e "${BOLD}Buscapega — Smoke test${RESET}"
sep

# ── FASE 1: verificaciones estáticas ─────────────────────────────────────────
echo ""
log "Fase 1 · Verificaciones estáticas (sin servicios)"
echo ""

# 1a. Sintaxis bash de todos los scripts del proyecto (excluye venv/node_modules)
SH_FILES=$(find "$PROJECT_ROOT" \
  -path "*/.venv/*" -prune -o \
  -path "*/node_modules/*" -prune -o \
  -path "*/test/*" -prune -o \
  -path "*/demo/*" -prune -o \
  -name "*.sh" -print 2>/dev/null)
SYNTAX_OK=1
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  if ! bash -n "$f" 2>/dev/null; then
    check_fail "Error de sintaxis bash en: ${f#"$PROJECT_ROOT"/}"
    SYNTAX_OK=0
  fi
done <<< "$SH_FILES"
[[ $SYNTAX_OK -eq 1 ]] && check_pass "Sintaxis bash OK ($(echo "$SH_FILES" | grep -c . ) scripts)"

# 1b. shellcheck (opcional — solo si está instalado)
if command -v shellcheck >/dev/null 2>&1; then
  SC_OK=1
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    shellcheck -S error "$f" >/dev/null 2>&1 || SC_OK=0
  done <<< "$SH_FILES"
  [[ $SC_OK -eq 1 ]] && check_pass "shellcheck (nivel error) OK" \
                     || check_fail "shellcheck reportó errores — corre: shellcheck <script>"
else
  warn "shellcheck no instalado — se omite (brew install shellcheck)"
fi

# 1c. docker-compose.yml válido
if command -v docker >/dev/null 2>&1; then
  if docker compose -f "$PROJECT_ROOT/docker/docker-compose.yml" config -q 2>/dev/null; then
    check_pass "docker-compose.yml válido"
  else
    check_fail "docker-compose.yml inválido — corre: docker compose -f docker/docker-compose.yml config"
  fi
else
  warn "docker no disponible — se omite validación de compose"
fi

# 1d. settings.json válido (si existe)
SETTINGS="$PROJECT_ROOT/documentos/settings.json"
if [[ -f "$SETTINGS" ]]; then
  if command -v python3 >/dev/null 2>&1 && python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$SETTINGS" 2>/dev/null; then
    check_pass "documentos/settings.json es JSON válido"
  else
    check_fail "documentos/settings.json no es JSON válido"
  fi
else
  warn "documentos/settings.json no existe aún (se crea al correr install.sh)"
fi

if [[ $STATIC_ONLY -eq 1 ]]; then
  echo ""; sep
  echo -e "  ${GREEN}${PASS} OK${RESET}  ·  ${RED}${FAIL} fallidas${RESET}  (solo fase estática)"
  [[ $FAIL -eq 0 ]] && exit 0 || exit 1
fi

# ── FASE 2: verificaciones dinámicas (servicios HTTP) ────────────────────────
echo ""
log "Fase 2 · Servicios HTTP en ${HOST} (backend:${BACKEND_PORT} scraper:${SCRAPER_PORT} frontend:${FRONTEND_PORT})"
echo ""

# http_check <nombre> <url> [<texto-esperado>]
http_check() {
  local name="$1" url="$2" expect="${3:-}"
  local body code
  body=$(curl -fsS --max-time 10 "$url" 2>/dev/null)
  code=$?
  if [[ $code -ne 0 ]]; then
    check_fail "$name — sin respuesta ($url)"
    return
  fi
  if [[ -n "$expect" && "$body" != *"$expect"* ]]; then
    check_fail "$name — responde pero falta '$expect' en el body"
    return
  fi
  check_pass "$name — OK"
}

http_check "backend  /health"       "http://${HOST}:${BACKEND_PORT}/health"
http_check "scraper  /health"       "http://${HOST}:${SCRAPER_PORT}/health"
http_check "frontend /"             "http://${HOST}:${FRONTEND_PORT}/"
http_check "backend  /api/settings" "http://${HOST}:${BACKEND_PORT}/api/settings" "user_name"

# ── Resumen ──────────────────────────────────────────────────────────────────
echo ""
sep
echo -e "  ${GREEN}${PASS} OK${RESET}  ·  ${RED}${FAIL} fallidas${RESET}"
if [[ $FAIL -eq 0 ]]; then
  ok "Smoke test superado — nada parece roto."
  exit 0
else
  bad "Smoke test con fallos — revisa los puntos marcados arriba."
  exit 1
fi
