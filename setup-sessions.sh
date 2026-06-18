#!/usr/bin/env bash
# Wrapper en la raíz para setup/setup_session.py (login en portales con auto-postulación).
# Uso: ./setup-sessions.sh [--lista | <portal>]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/setup"
exec python3 setup_session.py "$@"
