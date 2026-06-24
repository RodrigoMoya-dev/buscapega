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
