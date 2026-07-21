# Portal: RemoteLatinos.com

**URL:** https://www.remotelatinos.com  
**País:** Internacional (enfoque Latinoamérica)  
**Enfoque:** Trabajos remotos para profesionales latinoamericanos  
**Logo:** `https://www.remotelatinos.com/favicon.ico`

---

## Método de acceso

**Método probable:** Playwright headless o scraping directo  
**Estado:** Por explorar

### ¿Tiene RSS o API?
- No se conoce API pública.
- Pendiente verificar feed RSS: `https://www.remotelatinos.com/feed` o `/rss`

### ¿Requiere login para ver ofertas completas?
- Pendiente verificar. Es común en este tipo de portales que el detalle completo requiera registro.

### Parámetros de búsqueda (URL pattern)
- Pendiente verificar estructura de URL al realizar búsqueda manual.
- Explorar filtros por categoría (Desarrollo, Backend, PHP, etc.)

### Estructura HTML (selectores CSS — pendiente verificar)
- Pendiente análisis del DOM.

### ¿Tiene CAPTCHA o bloqueo anti-bot?
- Pendiente verificar. Portal mediano, posibilidad baja de protección agresiva.

### ¿Cómo se postula?
- Sistema propio en `app.remotelatinos.com`. Las postulaciones se gestionan completamente dentro de la plataforma.
- Incluye un video de presentación de 2-4 minutos como parte del proceso.
- **Tipo botón UI:** `Postular` — tiene formulario propio, automatizable con Playwright + cuenta registrada.

---

## Plan de implementación

1. Visitar manualmente y documentar estructura del portal.
2. Verificar si hay feed/API antes de implementar scraper.
3. Implementar según los hallazgos.

---

## Notas adicionales

- Relevante especialmente para trabajos con empresas de EEUU que contratan en LATAM.
- Las ofertas suelen estar en inglés o español, con pagos en USD.
- Alto valor para el perfil: muchas empresas buscan zona horaria Latinoamérica.
