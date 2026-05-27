#!/bin/bash
# Wunen — Setup de sesión (maneja venv automáticamente)
# Uso: ./run_setup.sh <portal>   ej: ./run_setup.sh findjobit
#      ./run_setup.sh --lista

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Crear venv si no existe
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creando entorno virtual..."
    python3 -m venv "$VENV_DIR"
fi

# Activar venv
source "$VENV_DIR/bin/activate"

# Instalar dependencias si faltan
if ! python -c "import playwright" 2>/dev/null; then
    echo "📦 Instalando dependencias..."
    pip install -q -r "$SCRIPT_DIR/requirements.txt"
    echo "🌐 Instalando Chromium para Playwright..."
    playwright install chromium
fi

# Ejecutar el script de setup con los argumentos pasados
python "$SCRIPT_DIR/setup_session.py" "$@"
