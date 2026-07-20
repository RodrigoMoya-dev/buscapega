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

## Resiliencia: diagnóstico y reanudación (20/07/2026)

### El problema

Un build fallaba y el usuario solo veía el volcado crudo de `apt-get` con cientos de
líneas, terminando en `exit code: 100`. Imposible saber si era culpa del proyecto o del
equipo. El caso real que motivó esto era **puramente de red** (`Unable to connect to
deb.debian.org`), no un error de código.

### Diagnóstico automático

`diagnosticar_error()` analiza el log del build fallido y clasifica la causa:

| Causa detectada | Patrones que la disparan |
|---|---|
| **Red** | `unable to connect`, `could not resolve`, `connection timed out`, `failed to fetch`, `i/o timeout` |
| **Disco lleno** | `no space left on device`, `disk quota exceeded` |
| **Memoria** | `killed`, `out of memory`, `exit code: 137` |
| **Permisos** | `permission denied`, `eacces` |
| **Daemon caído** | `cannot connect to the docker daemon` |
| **No reconocida** | *(fallback)* muestra las últimas 12 líneas del log |

Cada caso imprime pasos concretos de solución. La causa "no reconocida" avisa
explícitamente que probablemente sea un error real del proyecto y no del equipo del
usuario — esa distinción era justamente lo que faltaba.

### Reanudación

- Cada build exitoso se anota en `.install-state` (gitignored).
- Al arrancar, si el archivo existe, se ofrece **continuar** o **empezar de cero**.
- `omitir_paso()` solo salta un paso si está marcado **y** el usuario aceptó reanudar.
- Los logs de cada build quedan en `.install-logs/` (gitignored).
- Al terminar con el backend sano se borran ambos, para que la próxima ejecución sea
  limpia y no ofrezca reanudar una instalación que sí terminó.

> **Detalle:** los builds se ejecutan con `| tee` para mostrar progreso en vivo y a la vez
> guardar el log. Se lee `${PIPESTATUS[0]}` y no `$?`, porque con una tubería `$?` sería el
> estado de `tee` (siempre 0) y **todos los fallos de build pasarían desapercibidos**.

### Verificaciones previas de recursos

Antes de empezar (un build que muere a los 10 minutos es mucho más caro de diagnosticar):

- **Disco:** < 5 GB libres pide confirmación; < 10 GB advierte. Las imágenes ocupan ~6 GB.
  Se usa `df -Pk` (POSIX) y no `df -Pg`, que solo existe en BSD/macOS.
- **Memoria de Docker:** < 2 GB advierte sobre posibles OOM (exit 137) en frontend/WhatsApp.

## Decisiones importantes

### Contraseña de aplicación de Gmail es OPCIONAL (20/07/2026)

Antes se pedía sin indicar que se podía omitir. Ahora:

- Se marca `[OPCIONAL — Enter para omitir]` y se explica cómo agregarla después.
- Si se omite, se advierte que las postulaciones por correo quedan desactivadas.
- Si se ingresa, **se le quitan los espacios**: Google la muestra en bloques de 4
  (`abcd efgh ijkl mnop`) y al pegarla tal cual el login SMTP falla con
  *"Username and Password not accepted"*. Si tras limpiarla no mide 16 caracteres, avisa.

**Aviso en la web:** como se puede terminar la instalación sin contraseña, el correo
fallaría en silencio. Por eso:

- `GET /email-status` en el **scraper** (es quien tiene las credenciales; el backend no las
  recibe) informa si el envío está configurado, **sin exponer la credencial**.
- `GET /api/settings/email-status` en el backend lo proxea.
- La vista Configuración muestra un banner naranja cuando falta.

> Si el scraper no responde, el endpoint del backend devuelve `configurado: true` a
> propósito: es preferible no mostrar aviso a mostrar una alarma falsa por un servicio
> momentáneamente caído.

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
`./configuraciones/instalar_dependencias_python.sh`, el instalador de dependencias de la raíz —antes
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
real se hace al terminar la instalación ejecutando `./configuraciones/vincular-whatsapp.sh` y escaneando el QR
(o vinculando por código: `./configuraciones/vincular-whatsapp.sh <host> <port> <telefono>`).

### Comandos de Claude Code siempre visibles
El resumen muestra siempre `claude /valida <url>` y `claude /autentica`, por si el usuario tiene
Claude Code instalado.

## Scripts auxiliares en `configuraciones/`

Desde el 20/07/2026 todos los scripts que **no** son de instalación inicial viven en
`configuraciones/`. En la raíz queda únicamente `install.sh`.

| Script | Propósito |
|---|---|
| `configuraciones/vincular-whatsapp.sh` | Vincular WhatsApp (whatsapp-web.js) por QR o por código. No se hace en el instalador. |
| `configuraciones/setup-gmail.sh` | Configurar/cambiar el correo Gmail de postulaciones (actualiza `docker/.env` y reinicia el scraper). |
| `configuraciones/instalar_dependencias_python.sh` | Instalar dependencias de Python (venv + Playwright + Chromium) para la captura de sesiones. |
| `configuraciones/setup-sessions.sh` | Estado y captura de sesiones de portales (usa `setup/.venv`). |
| `configuraciones/smoke-test.sh` | Validación post-cambios (ver [[validacion]]). |

> **Detalle de implementación:** estos scripts resolvían sus rutas con
> `SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"` asumiendo estar en la raíz. Al moverlos se
> agregó `PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"` y todas las rutas derivadas
> (`setup/`, `docker/`, `documentos/`) cuelgan ahora de `PROJECT_ROOT`. Sin ese ajuste
> buscarían `configuraciones/setup/`, `configuraciones/docker/`, etc.

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

## Cambios sesión 24/06/2026 — volumen Postgres huérfano y falso positivo (fix)

Detectado por el comando `/prueba` (clon limpio de `main` + `install.sh`): el instalador
terminaba con "Instalación completada" pese a que el backend estaba caído por
`password authentication failed`. Causa: volumen `wunen_db_data` de una instalación previa
con otra contraseña, sin `docker/.env` que la conserve.

- **Detección de volumen Postgres huérfano** (`wunen_db_data` sin `.env`): avisa y ofrece
  resetear la base de datos o conservar el volumen.
- **Readiness del backend con diagnóstico real** tras el timeout (password vs. logs).
- **Banner final condicionado a la salud del backend** (verde solo si `/health` responde;
  amarillo "incompleta" si no) → se elimina el falso positivo de éxito.
- **Fix en la generación de `POSTGRES_PASSWORD`**: ya no concatena aleatorio + fallback por
  SIGPIPE.

### Detección de volumen Postgres huérfano (fix 24/06/2026)
El volumen `wunen_db_data` se inicializa con la contraseña de la PRIMERA instalación y la
conserva para siempre. Si se hace un **clon nuevo** del repo (o se borra `docker/.env`)
sobre un volumen viejo, `install.sh` genera una contraseña NUEVA que **no coincide** con la
del volumen → el backend falla con `password authentication failed for user "wunen"`.

- Cuando **existía** un `docker/.env` al iniciar, su `POSTGRES_PASSWORD` se **reutiliza**
  (lógica previa) y no hay conflicto.
- Cuando **NO** existía `.env` pero **sí** está el volumen `wunen_db_data`, el instalador lo
  detecta antes de `compose up` y ofrece: **a)** resetear la base de datos
  (`docker volume rm wunen_db_data`, se pierden datos previos) o **b)** conservarla
  (el usuario debe restaurar el `.env` original a mano). Esto evita el backend caído
  silencioso en reinstalaciones.

### Verificación de readiness del backend más robusta (fix 24/06/2026)
- Tras la espera de 60 s, si el backend no responde `/health` se **diagnostica la causa**:
  si los logs muestran `password authentication failed` se indica la remediación concreta
  (`compose down -v && up -d`); en otro caso se apunta a `compose logs backend`. Ya no se
  muestra el warning genérico "tardó más de lo esperado" sin contexto.
- El banner final **solo muestra "Instalación completada" en verde si el backend respondió
  `/health`**. Si no, muestra "Instalación incompleta — backend caído" en amarillo, evitando
  el falso positivo de éxito que se daba antes.

### Generación de `POSTGRES_PASSWORD` (fix 24/06/2026)
`tr -dc ... < /dev/urandom | head -c 24 || echo "wunen_$(date)"` concatenaba el valor
aleatorio Y el fallback: `head` cierra el pipe, `tr` recibe SIGPIPE (exit 141) y disparaba
el `||`. Ahora se captura primero (`... | head -c 24 || true`) y el fallback solo actúa si
el resultado quedó vacío (`[[ -z ]]`).

## Cambios sesión 26/06/2026 — scripts de setup

- `setup-sessions.sh` ahora valida que **Python 3** esté instalado y usa `setup/.venv`
  (creándolo e instalando Playwright/Chromium si faltan). Antes invocaba `python3` del sistema y
  fallaba con `ModuleNotFoundError: No module named 'playwright'`. (fix)
- `setup/run_setup.sh` se movió a la raíz como `instalar_dependencias_python.sh` (instalador de
  dependencias dedicado, con validación de Python). (feature)
- `whatsapp-qr.sh` se renombró a `vincular-whatsapp.sh`. (feature)
