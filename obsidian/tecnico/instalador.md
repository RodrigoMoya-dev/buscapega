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

### Detección de Docker y de instalaciones previas
- **Daemon de Docker:** además de verificar que el binario exista (`command -v docker`),
  el instalador comprueba que el **daemon responda** con `docker info`. Si Docker Desktop
  está cerrado, aborta con un mensaje claro en vez de fallar más tarde en `compose build`.
- **Instalación previa de Wunen:** antes de validar puertos, detecta contenedores
  `wunen_*` existentes (`docker ps -a --filter name=wunen_`) y avisa que es una
  reinstalación (los datos en volúmenes se conservan; `compose up -d` recrea los
  contenedores).
- **`check_port` no da falsos positivos:** si un puerto está en uso pero lo ocupa un
  contenedor de Wunen corriendo (match `^wunen_.*:<port>->` en `docker ps`), lo reporta
  como "se recreará al reiniciar" en lugar de marcarlo como conflicto. Un conflicto real
  (otro proceso ajeno) sigue mostrando las opciones a/b/c.

### Las sesiones de portales se cargan LOCALMENTE (no a Presto)
Wunen funciona 100% en el equipo de quien lo instala. La captura de sesión
(`setup/setup_session.py`) guarda las cookies en `setup/cookies/` y luego las copia
al volumen del contenedor local con `docker cp ... wunen_scraper:/app/cookies/`
(función `sincronizar_local`). **No** se sincroniza a ningún servidor remoto durante
la instalación.

La sincronización a Presto vía `rsync` quedó como opción **interna del desarrollador**:
solo se ejecuta si se pasa el flag `--presto` a `setup_session.py`. Sin ese flag, el
instalador no toca Presto.

### Vinculación de WhatsApp se hace después por QR
En el prompt del teléfono se aclara que ahí **solo se guarda el número**; la vinculación
real se hace al terminar la instalación ejecutando `./whatsapp-qr.sh` y escaneando el QR.

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

## Cambios sesión 19/06/2026 — instalador 100% local (fix)

- **Sesiones de portales ya NO se sincronizan a Presto durante la instalación.**
  `setup_session.py` ahora copia las cookies al contenedor local (`wunen_scraper`)
  vía `docker cp` (`sincronizar_local`). El `rsync` a Presto pasó a ser opcional
  con `--presto` (uso interno del desarrollador).
- Mensajes corregidos: ya no dice "La sesión está lista en Presto"; ahora dice
  "guardada localmente".
- El prompt del teléfono de WhatsApp aclara que solo se guarda el número y que la
  vinculación se hace después con `./whatsapp-qr.sh` (QR).

## Cambios sesión 19/06/2026 — detección de Docker/instalación previa (feature)

- Verificación del **daemon de Docker** con `docker info` (antes solo se comprobaba el
  binario). Si el daemon no responde, aborta con mensaje claro.
- **Detección de instalación previa de Wunen** (contenedores `wunen_*`) antes de validar
  puertos, avisando que es una reinstalación.
- `check_port` ya no marca como conflicto los puertos ocupados por contenedores de Wunen
  corriendo (reinstalación); solo alerta ante procesos ajenos.
