# Vista: Ofertas

**Ruta web:** `/` (home)
**Archivo:** `docker/frontend/app/page.tsx` + `components/OfferCard.tsx`
**API:** `GET /api/offers`, `GET /api/stats`, `POST /api/scraper/trigger`, `GET /api/portals`

---

## ¿Qué es?
Bandeja de propuestas de trabajo con pestañas (Pendientes / Enviadas / Descartadas), filtros por
auto-postulación y tecnología, y el botón **"Buscar ofertas"** que dispara el scraping.

## Búsqueda de ofertas con diálogo de progreso (fix 24/06/2026)
Antes, "Buscar ofertas" disparaba el scraping y esperaba 5 s fijos sin feedback → parecía que
"no hacía nada". Ahora:

- Al pulsar el botón se abre un **diálogo modal** con un spinner flat y el texto "Cargando…".
- Debajo va mostrando **"Buscando en _&lt;nombre del portal&gt;_…"**, recorriendo la lista de
  portales (`GET /api/portals`) mientras el backend hace el scraping en segundo plano.
- Al terminar el recorrido muestra "Finalizando…", cierra el diálogo y recarga las ofertas.

> El scraping real corre asíncrono en el backend; el recorrido portal-por-portal es la
> representación visible del progreso (no hay aún eventos en tiempo real por portal).

## Aviso de postulaciones (mejoras 24/06/2026)
- El banner de stats se movió **bajo el título "Ofertas"** (antes estaba arriba del todo).
- Lleva un **ícono de robot** flat.
- Texto corregido: **"Has postulado a N postulación(es)"** con pluralización correcta
  (antes decía "1 oferta laborale.."). Usa `stats.total_sent` (+ "N esta semana" si aplica).
- Incluye el enlace **"Ver mis postulaciones"** que cambia a la pestaña **Enviadas**.
- Solo se muestra cuando hay al menos una postulación (`total_sent > 0`).

## Filtro por portal y resumen por portal (mejoras 24/06/2026)
- **Resumen por portal (bajo el título):** una tarjeta muestra cuántas ofertas hay en la pestaña
  actual desglosadas por portal (`offersByPortal`, contadas desde la lista cargada). Se actualiza
  con la pestaña (Pendientes / Enviadas / Descartadas).
- **Checkboxes de portales activos (filtro):** en el bloque de filtros, además de
  "Solo autopostulación" y Tecnología, hay una fila **Portal** con un checkbox por cada portal
  **activo** (`getPortals()` filtrado por `active`). Seleccionar uno o varios filtra las ofertas a
  esos portales (`selectedPortals`). El botón "Limpiar" deselecciona todos.

## Tarjeta de oferta (`OfferCard.tsx`, mejoras 24/06/2026)
- Se **quitaron los botones "Descartar" y "Bloquear empresa"**.
- Portales con auto-postulación: botón **"Postular"** (ancho completo).
- Portales sin auto-postulación: en vez de botón, el texto _"Esta oferta no fue posible
  postularla de forma automática, aunque puedes hacerlo usando una API KEY de Anthropic."_
  (el título de la tarjeta sigue enlazando a la oferta).
