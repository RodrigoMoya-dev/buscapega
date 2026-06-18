# Instalador — `install.sh`

**Archivo:** `/install.sh` (raíz del proyecto)

---

## Flujo

1. Valida estructura de carpetas y prerrequisitos (Docker, Compose).
2. Crea `documentos/portales.json` y `perfil.md` base si no existen.
3. Configuración interactiva: nombre, Anthropic API key (**opcional**), teléfono WhatsApp,
   correo Gmail + contraseña de aplicación, puertos.
4. Genera `docker/.env` y `documentos/settings.json`.
5. Construye e inicia los servicios Docker.
6. Opcional: captura de sesiones de portales con Playwright.
7. Resumen final con próximos pasos.

## Decisiones importantes

### Anthropic API key es OPCIONAL
El instalador deja claro (en el prompt y en el resumen final) que la key es opcional. Sin ella,
la evaluación usa scoring por keywords; para evaluación con IA se recomienda **Claude Code**
(no requiere API key de pago) o agregar `ANTHROPIC_API_KEY` en `docker/.env`.

### Teléfono y correo editables luego
El resumen indica que se pueden cambiar en la web (Configuración) o en
`documentos/settings.json`.

### Configuración de sesiones de portales usa venv
La captura de sesiones (Playwright) **siempre** instala dependencias dentro de un entorno virtual
`setup/.venv`. Esto evita el error PEP 668 *externally-managed-environment* que rompía
`pip install` y derivaba en `ModuleNotFoundError: No module named 'playwright'` en macOS/Homebrew
y Linux moderno. Todas las llamadas usan `setup/.venv/bin/python` (mismo enfoque que
`setup/run_setup.sh`).

### Comandos de Claude Code siempre visibles
El resumen muestra siempre `claude /valida <url>` y `claude /autentica`, por si el usuario tiene
Claude Code instalado.

## Scripts auxiliares en la raíz

| Script | Propósito |
|---|---|
| `whatsapp-qr.sh` | Vincular WhatsApp (Baileys) escaneando un QR. No se hace en el instalador. |
| `setup-gmail.sh` | Configurar/cambiar el correo Gmail de postulaciones (actualiza `docker/.env` y reinicia el scraper). |
| `setup-sessions.sh` | Estado y captura de sesiones de portales. |

## Cambios sesión 17/06/2026

- Mensaje claro de Anthropic key opcional (prompt + resumen).
- Indicación de dónde editar teléfono/correo (`documentos/settings.json` + web).
- Mención de `./whatsapp-qr.sh` y `./setup-gmail.sh` en el resumen.
- Comandos de Claude Code mostrados siempre.
- Captura de sesiones via venv `setup/.venv` (arregla fallo pip/playwright).
- Nuevo script `setup-gmail.sh`.
