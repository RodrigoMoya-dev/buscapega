# Vista: Portales

**Ruta web:** `/authenticate` (la antigua `/validate` ahora **redirige** aquí)
**Archivo:** `docker/frontend/app/authenticate/page.tsx`
**API:** `GET /api/portals`, `POST /api/portals/validate`, `PATCH /api/portals/toggle`
(`docker/backend/app/routers/portals.py`)

---

## ¿Qué es?

Vista unificada que **fusiona "Validar sitio" y "Portales"** (24/06/2026). Tiene dos bloques con
colores de fondo distintos:

1. **Validar sitio** (fondo índigo destacado): valida si un portal nuevo es automatizable
   (scraping + Google auth). Incluye un botón de ayuda **(?)** que explica qué hace la validación
   antes del campo de URL. Ver `obsidian/web/validar-sitio.md`.
2. **Portales de empleo** (fondo slate): lista los portales registrados en **acordeones**.

## Acordeones por categoría (P4)
- **Portales con auto-postulación** (`auto_apply = true`) — abierto por defecto.
- **Portales revisables (sin auto-postulación)** (`auto_apply = false`).
- **Portales que no permiten scraping** — vacío por ahora (el backend aún no distingue esta
  categoría; queda como pendiente añadir el dato al catálogo).

Al compactar, cada acordeón muestra la **cantidad de portales** junto al título.

## Fila de portal (P6)
- **Bandera** del mercado/país (emoji) con el nombre como tooltip (en vez del texto del país).
- **Switch Activo/Inactivo**: persiste el flag `active` del portal vía `PATCH /api/portals/toggle`
  (optimista; revierte si la petición falla). _Nota:_ que el scraper respete `active` queda como
  follow-up.
  - Si el portal **revisable** (sin auto-postulación) queda activo, se muestra el aviso:
    "Portal activado. Importante: te llegarán las ofertas pero deberás postular manualmente."
- Portales **sin auto-postulación**: botón **"Visitar"** (con ícono) que abre el sitio.
- Botón **"Registrar sesión con Google"** (ícono de Google) que abre un **diálogo persistente**
  (P5) con: el texto de ayuda, el comando `python3 setup/setup_session.py <slug>`, la alternativa
  `claude /autentica`, y botones de copiar. El diálogo solo se cierra con la X o "Cerrar".

## Estado de sesión (`session_active`) vs. `active`
- `session_active`: hay cookies capturadas (`cookies/{session_key}_session.json`). Se muestra como
  "Sesión activa / Sin sesión" en portales con auto-postulación.
- `active`: el portal participa de la búsqueda (lo controla el switch). Persistido en `portales.json`.

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

## Mejoras 24/06/2026 — buscador, agregar/compartir portal y estados

### Buscador de portales (entre "Validar sitio" y "Portales de empleo")
Input de búsqueda que filtra los portales por **nombre o URL** (`search`). Al escribir, los
acordeones se reabren (su `key` incluye el query) para mostrar los resultados; si nada coincide,
muestra "Ningún portal coincide con …".

### Texto de sesión
"Sin sesión" → **"Sesión no iniciada"** en la fila de portal.

### Agregar un sitio validado a los portales (Validar sitio)
Si la validación da **automatizable** y el sitio **no está ya registrado**, aparece el botón
**"Agregar a mis portales"** → `POST /api/portals/add`. El backend determina la categoría
automáticamente:
- `allows_scraping` + Google auth → **auto-postulación** (`auto_apply=true`, con `session_key`).
- `allows_scraping` sin Google auth → **revisable** (`auto_apply=false`).
- sin scraping → **no permite scraping** (`allows_scraping=false`).

El listado (`GET /api/portals`) ahora expone `allows_scraping`; la vista usa ese flag para poblar
el acordeón "Portales que no permiten scraping".

### Compartir en GitHub (T6)
Tras agregar el portal, un botón **"Compartir en GitHub"** abre un issue prellenado en el repo
público (`RodrigoMoya-dev/wunen`) con la URL y los resultados de la validación, para proponerlo a
la comunidad. Lleva tooltip que avisa que abrirá GitHub.

### Atajo Claude Code (T7)
Bajo el campo de URL: aviso de que con Claude Code se puede validar desde la terminal con
`claude /valida <sitio>`.

## Cambios sesión 24/06/2026 — fusión Validar+Portales y rediseño

- Se fusionó "Validar sitio" en esta vista (`/validate` redirige a `/authenticate`).
- Acordeones por categoría con conteo; switch de activación (`PATCH /api/portals/toggle`,
  nuevo campo `active`); banderas con tooltip; botón "Visitar"; diálogo persistente de
  registro de sesión con Google.
- Backend: `list_portals` ahora devuelve `active`; nuevo endpoint `toggle_portal`.
