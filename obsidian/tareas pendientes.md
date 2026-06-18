# Tareas pendientes

> Las tareas resueltas se eliminan de este archivo. El historial completo queda en los
> commits de git. Aquí solo vive lo que está **pendiente** o las notas vigentes.

---

## Sesión 18/06/2026

- [x] **A. Scripts de validación post-cambios** — creado `smoke-test.sh` en la raíz.
      Valida sintaxis bash + docker-compose + JSON de settings, y la salud HTTP de
      backend/scraper/frontend. Ver "Cómo validar que nada se rompió" más abajo.
- [x] **B. Limpieza de este archivo** — eliminadas las tareas ya resueltas (estaban
      todas en `[x]`); el historial vive en git.
- [x] **C. Mensaje "OPCIONAL" de la Anthropic Key** — ya está en el código y en `main`
      (`install.sh:172-177`, commit `5c49458`). El texto viejo "necesaria para
      evaluación IA de ofertas" **ya no existe** en el repo.
- [x] **D. Nombre de usuario en la web** — pipeline completo y mergeado a `main`:
      `install.sh` pregunta el nombre (línea 167) → escribe `documentos/settings.json`
      → backend `routers/settings.py` lo sirve en `/api/settings` → frontend
      `NavGreeting.tsx` muestra "Hola, {nombre}".

### Causa raíz de C y D (importante)

El usuario corrió un `install.sh` **viejo**: la versión que descargó de GitHub era
anterior al merge `5c49458`. En el `main` actual de GitHub **y** de Gitea ambas
correcciones ya están presentes (verificado con `git show github/main:install.sh`).

**Acción del usuario:** volver a descargar `main` (o `git pull origin main`) y correr
de nuevo `install.sh`. La descarga fresca de hoy ya trae el instalador corregido.

---

## Resultado del `/prueba` (18/06/2026) — bug encontrado y corregido

Se clonó `github/main` (HEAD `d3d72cd`) en `/demo` y se corrió `install.sh`. Confirmado:
el instalador muestra el texto **OPCIONAL** de Anthropic, pregunta el nombre y escribe
`settings.json` con `user_name`. **El `smoke-test.sh` detectó un fallo real:** el backend
no levantaba.

- **Síntoma:** `password authentication failed for user "wunen"` en los logs del backend.
- **Causa:** `install.sh` generaba un `POSTGRES_PASSWORD` aleatorio **en cada corrida**,
  pero el volumen de Postgres (`wunen_db_data`) conserva la contraseña de la PRIMERA
  instalación. Al regenerarla, el backend ya no podía autenticar contra el volumen
  existente. Afecta a re-instalaciones o a equipos con un volumen previo.
- **Fix (rama `fix_install_db_password_18062026`):**
  1. Si ya existe `docker/.env`, se **reutiliza** su `POSTGRES_PASSWORD` (no se regenera).
  2. Tras arrancar, si el backend no responde y los logs muestran el error de
     autenticación, el instalador imprime la remediación exacta
     (`docker compose down -v && docker compose up -d`).
- **Validación:** tras el fix, `./smoke-test.sh` da **6/6 OK** (backend, scraper,
  frontend y `/api/settings` con `user_name`).

---

## Cómo validar que nada se rompió después de un cambio

Se agregó el script **`smoke-test.sh`** en la raíz del proyecto. Responde a la
pregunta "¿se rompió algo después de mis cambios?" con dos fases:

| Fase | Qué valida | ¿Necesita servicios levantados? |
|------|-----------|----------------------------------|
| **Estática** | Sintaxis de todos los scripts `bash -n`, `shellcheck` (si está), validez de `docker-compose.yml`, JSON de `settings.json` | No |
| **Dinámica** | `backend /health`, `scraper /health`, `frontend /`, y que `/api/settings` devuelva `user_name` | Sí |

```bash
./smoke-test.sh            # local (frontend 3000, backend 8000, scraper 8001)
./smoke-test.sh --presto   # presto (frontend 3020, backend 8020, scraper 8021)
./smoke-test.sh --static   # solo fase estática (sin Docker corriendo)
```

Devuelve código de salida `0` si todo pasa y `1` si algo falla, así que sirve para
encadenar en CI o en un git hook.

### Tecnologías recomendadas (y por qué)

- **Bash + `curl` (smoke test):** lo que ya usa `smoke-test.sh`. Cero dependencias
  nuevas, corre igual en el Mac y en Presto. Ideal como primer chequeo rápido.
- **`bash -n` + `shellcheck`:** `bash -n` detecta errores de sintaxis sin ejecutar el
  script (ya integrado); `shellcheck` (opcional, `brew install shellcheck`) detecta
  bugs comunes (variables sin comillas, comparaciones frágiles). El script lo usa si
  está instalado.
- **`docker compose config -q`:** valida que el compose no tenga errores de estructura
  antes de hacer `up`. Ya integrado.
- **pytest (backend, a futuro):** para lógica de negocio del evaluador y los routers
  conviene tests unitarios con `pytest` + `httpx` contra la app FastAPI (`TestClient`).
  Hoy no hay; es la siguiente capa natural si se quiere cubrir lógica, no solo "está vivo".
- **Playwright (frontend E2E, a futuro):** el proyecto ya usa Playwright para los
  applicators; el mismo runtime sirve para un test E2E del flujo de la web (cargar
  inbox, validar sitio, ver "Hola, {nombre}"). Es la opción más coherente con el stack.

**Recomendación de uso:** correr `./smoke-test.sh` después de cada cambio y antes de
desplegar a Presto. Si más adelante se quiere cubrir lógica (no solo disponibilidad),
sumar `pytest` en el backend y un par de pruebas Playwright en el frontend.
