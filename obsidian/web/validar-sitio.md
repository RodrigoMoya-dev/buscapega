# Vista: Validar sitio

> **Fusionada en Portales (24/06/2026):** desde esta fecha "Validar sitio" es un bloque dentro de
> la vista **Portales** (`/authenticate`). La ruta `/validate` ahora **redirige** a `/authenticate`.
> La lógica de validación (criterios, factibilidad) sigue siendo la documentada aquí.

**Ruta web:** `/validate` → redirige a `/authenticate` (bloque "Validar sitio")
**Archivo:** `docker/frontend/app/authenticate/page.tsx` (componente `ValidateSection`)
**API:** `POST /api/portals/validate` (`docker/backend/app/routers/portals.py`)

---

## ¿Qué es?

Permite ingresar la URL de un portal de empleo y evaluar si es automatizable. Verifica dos
criterios: que el sitio permita scraping (`robots.txt`) y que tenga autenticación con Google.

## Validación de estructura de URL

- **Cliente:** antes de llamar al backend se valida con un regex que la URL tenga estructura
  tipo `sitio.com` (dominio con punto y TLD). Si se escribe algo como `sddfgld`, se muestra
  el error de inmediato sin llamar al servidor.
- **Servidor:** `_has_valid_domain()` aplica el mismo criterio como segunda barrera.
- La URL se normaliza agregando `https://` si falta.

## Manejo de errores de red / CORS

Si `validatePortal()` devuelve `null` (backend caído, error de red o CORS), la UI ahora muestra
un mensaje claro ("No se pudo contactar al servidor de validación...") en lugar de quedarse
en silencio. El backend tiene CORS abierto (`allow_origins=["*"]` en `main.py`); el error
"Fetch API cannot load ... due to access control checks" en Safari aparecía cuando el backend
servía una versión vieja del código → se resuelve desplegando el build actualizado.

## Atajo con Claude Code

`claude /valida <url>` ejecuta la misma validación desde la terminal.

## Cambios sesión 17/06/2026

- Validación de estructura de URL en el cliente (feedback inmediato).
- Mensaje de error explícito cuando la petición de validación falla.
