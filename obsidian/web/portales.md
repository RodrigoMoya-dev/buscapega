# Vista: Portales

**Ruta web:** `/authenticate`
**Archivo:** `docker/frontend/app/authenticate/page.tsx`
**API:** `GET /api/portals` (`docker/backend/app/routers/portals.py`)

---

## ¿Qué es?

Lista los portales registrados, separados en "con auto-postulación" y "manuales", con el estado
de la sesión (Activo / Inactivo) y el conteo de postulaciones realizadas.

## Estado de sesión (`session_active`)

Un portal aparece **Activo** si existe el archivo de cookies
`cookies/{session_key}_session.json` capturado con `setup_session.py`.

### Demo: FindJobIT activo por defecto

Para poder demostrar el flujo sin capturar una sesión real, FindJobIT se marca como **Activo**
por defecto mediante el flag `demo_active`:

- En `portales.json` / `DEFAULT_PORTAL_LIST`: `"demo_active": true`.
- En `portals.py`, `_is_demo_active()` también fuerza esto por `session_key` (`DEMO_ACTIVE_KEYS`),
  de modo que funciona incluso en instalaciones cuyo `portales.json` no incluya el flag.
- El flag `demo_active` no se expone en la respuesta de la API (se filtra junto con `session_key`).

## Orden de portales

Definido en `documentos/portales.json` (o `DEFAULT_PORTAL_LIST` si no existe). FindJobIT primero.

## Cambios sesión 17/06/2026

- FindJobIT activo por defecto (demo) vía `demo_active` / `DEMO_ACTIVE_KEYS`.
