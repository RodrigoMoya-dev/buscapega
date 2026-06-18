# Validación post-cambios (`smoke-test.sh`)

Script en la **raíz del proyecto** que verifica que un cambio no haya roto nada.
Es la primera línea de defensa antes de desplegar a Presto.

## Qué hace

Dos fases:

1. **Estática** (no requiere servicios levantados):
   - Sintaxis de todos los scripts `.sh` con `bash -n` (excluye `.venv/`, `node_modules/`, `test/`, `demo/`).
   - `shellcheck -S error` sobre cada script, si está instalado (opcional).
   - `docker compose config -q` para validar `docker/docker-compose.yml`.
   - Validez del JSON de `documentos/settings.json` (si existe).
2. **Dinámica** (requiere los contenedores corriendo):
   - `GET backend /health` → 200
   - `GET scraper /health` → 200
   - `GET frontend /` → 200
   - `GET backend /api/settings` → debe contener `user_name`

Imprime un resumen `N OK · M fallidas` y devuelve código de salida `0`/`1`.

## Uso

```bash
./smoke-test.sh            # local (frontend 3000, backend 8000, scraper 8001)
./smoke-test.sh --presto   # presto (frontend 3020, backend 8020, scraper 8021)
./smoke-test.sh --static   # solo fase estática (sin Docker corriendo)
HOST=192.168.100.6 ./smoke-test.sh   # host arbitrario con puertos por defecto
```

Variables de entorno: `HOST`, `BACKEND_PORT`, `SCRAPER_PORT`, `FRONTEND_PORT`.

## Cuándo correrlo

- Después de cualquier cambio de código o de scripts.
- Antes de hacer `git push` y antes de desplegar a Presto.
- Puede encadenarse en un git hook (`pre-push`) o en CI porque devuelve código de salida.

## Tecnologías y por qué

- **Bash + curl**: cero dependencias nuevas, corre igual en Mac y Presto.
- **`bash -n` / `shellcheck`**: detectan errores de sintaxis y bugs comunes sin ejecutar.
- **`docker compose config`**: valida el compose antes del `up`.
- **A futuro**: `pytest` + `httpx` (TestClient) para la lógica del backend, y Playwright
  para E2E del frontend (el stack ya usa Playwright en los applicators).

Ver también: [[docker-compose]], [[instalador]].
