# Portal: Chumi-IT.com

**URL:** https://chumi-it.com  
**País:** España / Internacional  
**Enfoque:** Empleos IT para freelancers y remotos  
**Logo:** `https://chumi-it.com/favicon.ico`

---

## Método de acceso

**Método probable:** Scraping directo o Playwright  
**Estado:** Por explorar

### ¿Tiene RSS o API?
- Pendiente verificar: `https://chumi-it.com/feed` o `https://chumi-it.com/rss`
- Portal mediano, posibilidad baja de tener API pública.

### ¿Requiere login para ver ofertas completas?
- Pendiente verificar. Algunos portales de freelance requieren login para ver tarifas o contacto.

### Parámetros de búsqueda (URL pattern)
- Pendiente verificar estructura de URLs de búsqueda.
- Explorar manualmente la URL al hacer una búsqueda de "php remoto".

### Estructura HTML (selectores CSS — pendiente verificar)
- Pendiente análisis del DOM con DevTools.

### ¿Tiene CAPTCHA o bloqueo anti-bot?
- Pendiente verificar.

### ¿Cómo se postula?
- Plataforma propia: se crea cuenta, se sube CV y se postula directamente desde el portal.
- Incluye feedback de IA y alertas personalizadas. Los reclutadores pueden contactar al candidato directamente.
- **Tipo botón UI:** `Postular` — tiene formulario propio, automatizable con Playwright + cuenta registrada.

---

## Plan de implementación

1. Visitar manualmente el portal y documentar:
   - URL pattern de búsqueda
   - Estructura HTML del listado y detalle
   - Si requiere login
   - Método de postulación
2. Implementar scraper según los hallazgos.

---

## Notas adicionales

- Portal enfocado en perfiles IT en España. Relevante para trabajos con empresas españolas.
- Pendiente mayor investigación antes de implementar el scraper.
