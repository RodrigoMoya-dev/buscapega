#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Wunen — Instalador de dependencias de Python para la captura de sesiones.
#
# Valida que Python 3 esté instalado, crea el entorno virtual en setup/.venv e
# instala las dependencias (Playwright) junto con el navegador Chromium.
#
# Uso: ./instalar_dependencias_python.sh
#
# Después de instalar, captura sesiones con:
#   ./setup-sessions.sh <portal>     (ej: ./setup-sessions.sh getonbrd)
#   ./setup-sessions.sh --lista      (ver portales y estado de sesión)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

CYAN='\033[0;36m'; GREEN='\033[0;32m'; RED='\033[0;31m'; BOLD='\033[1m'; RESET='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETUP_DIR="$SCRIPT_DIR/setup"
VENV_DIR="$SETUP_DIR/.venv"

echo ""
echo -e "${BOLD}Wunen — Instalar dependencias de Python${RESET}"
echo ""

# 1) Validar que Python 3 esté instalado en el sistema.
if ! command -v python3 &>/dev/null; then
  echo -e "${RED}✗ ERROR:${RESET} Python 3 no está instalado en este sistema."
  echo "  Instálalo antes de continuar:"
  echo -e "    macOS:  ${CYAN}brew install python3${RESET}   (o https://www.python.org/downloads/)"
  echo -e "    Linux:  ${CYAN}sudo apt install python3 python3-venv${RESET}"
  exit 1
fi
echo -e "${GREEN}✓${RESET} Python detectado: $(python3 --version)"

# 2) Crear el entorno virtual si no existe.
if [ ! -d "$VENV_DIR" ]; then
  echo -e "${CYAN}▶${RESET} Creando entorno virtual en setup/.venv..."
  python3 -m venv "$VENV_DIR"
else
  echo -e "${GREEN}✓${RESET} Entorno virtual ya existe (setup/.venv)"
fi

# 3) Instalar dependencias en el venv.
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
echo -e "${CYAN}▶${RESET} Instalando dependencias de Python..."
pip install -q --upgrade pip
pip install -q -r "$SETUP_DIR/requirements.txt"
echo -e "${CYAN}▶${RESET} Instalando Chromium para Playwright..."
playwright install chromium

echo ""
echo -e "${GREEN}✓ Dependencias instaladas correctamente.${RESET}"
echo -e "  Captura una sesión con: ${CYAN}./setup-sessions.sh <portal>${RESET}"
echo -e "  Lista los portales con: ${CYAN}./setup-sessions.sh --lista${RESET}"
echo ""
