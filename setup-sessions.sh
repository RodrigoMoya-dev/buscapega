#!/usr/bin/env bash
# Wrapper en la raíz para la captura de sesiones (login en portales con auto-postulación).
# Uso: ./setup-sessions.sh [--lista | <portal>]
#
# Delega en setup/run_setup.sh, que crea el entorno virtual (setup/.venv) e instala las
# dependencias de Python (playwright + Chromium) automáticamente la primera vez. Así se evita
# el error "ModuleNotFoundError: No module named 'playwright'" que aparece al ejecutar
# `python3 setup/setup_session.py <portal>` con el Python del sistema (sin venv).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/setup/run_setup.sh" "$@"
