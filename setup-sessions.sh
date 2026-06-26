#!/usr/bin/env bash
# Wrapper en la raíz para setup/setup_session.py (login en portales con auto-postulación).
# Usa el entorno virtual de setup/.venv para que Playwright esté disponible: si se llama
# a python3 del sistema sin el venv, falla con "ModuleNotFoundError: No module named 'playwright'".
# Uso: ./setup-sessions.sh [--lista | <portal>]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETUP_DIR="$SCRIPT_DIR/setup"
VENV_DIR="$SETUP_DIR/.venv"

# 1) Validar que Python 3 esté instalado en el sistema.
if ! command -v python3 &>/dev/null; then
  echo "✗ ERROR: Python 3 no está instalado en este sistema." >&2
  echo "  Instálalo antes de continuar:" >&2
  echo "    macOS:  brew install python3   (o https://www.python.org/downloads/)" >&2
  echo "    Linux:  sudo apt install python3 python3-venv" >&2
  exit 1
fi

# 2) Crear el entorno virtual si aún no existe.
if [ ! -d "$VENV_DIR" ]; then
  echo "🔧 Creando entorno virtual de Python en setup/.venv..."
  python3 -m venv "$VENV_DIR"
fi

# 3) Activar el venv e instalar las dependencias si faltan.
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
if ! python -c "import playwright" 2>/dev/null; then
  echo "📦 Faltan dependencias de Python (Playwright). Instalando..."
  pip install -q -r "$SETUP_DIR/requirements.txt"
  echo "🌐 Instalando Chromium para Playwright..."
  playwright install chromium
fi

# 4) Ejecutar la captura de sesión con el Python del venv (no el del sistema).
exec python "$SETUP_DIR/setup_session.py" "$@"
