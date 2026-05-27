# Portal: FlexJobs.com

**URL:** https://www.flexjobs.com  
**País:** Internacional (origen EEUU)  
**Enfoque:** Trabajos remotos, flexibles y part-time de alta calidad  
**Logo:** `https://www.flexjobs.com/favicon.ico`

---

## Método de acceso

**Método probable:** Playwright con sesión (requiere suscripción paga)  
**Estado:** Por explorar — **IMPORTANTE: portal de pago**

### ¿Tiene RSS o API?
- No tiene API pública ni RSS.
- Todo el contenido está detrás de muro de pago.

### ¿Requiere login para ver ofertas completas?
- **Sí. Requiere suscripción paga** (aprox. USD 24.95/mes o USD 49.95/trimestre).
- Sin suscripción, solo se ven títulos y empresa; no hay descripción completa ni enlace de postulación.

### Parámetros de búsqueda (URL pattern)
```
https://www.flexjobs.com/jobs/search?search=<keywords>&location=&remote_level[]=<nivel>
```
*(Solo accesible con sesión activa)*

### Estructura HTML (selectores CSS — pendiente verificar con sesión)
| Campo | Selector probable |
|---|---|
| Listado | `.job-listing` |
| Título | `h2.job-title` |
| Empresa | `.company-name` |
| Descripción | `.job-description` |
| Tags | `.job-tags` |

### ¿Tiene CAPTCHA o bloqueo anti-bot?
- Probable. Al ser de pago, tienen incentivo para proteger el contenido.
- Playwright con delays aleatorios y sesión real de usuario.
- Guardar cookies en volumen Docker.

### ¿Cómo se postula?
- Redirección al portal de la empresa (mayoría de casos) o formulario propio de FlexJobs (minoría).
- Comportamiento mixto e impredecible por oferta. Requiere suscripción paga activa.
- **Tipo botón UI:** `Acceder (Abre una ventana nueva)` — demasiado variable para automatizar de forma confiable.

---

## Plan de implementación

1. **Decisión previa:** ¿Vale la pena la suscripción? Evaluar costo/beneficio.
2. Si se decide usar: crear cuenta, guardar cookies de sesión autenticada.
3. Implementar scraper con Playwright usando la sesión guardada.
4. Renovar cookies cuando expire la sesión.

---

## Notas adicionales

- Portal de muy alta calidad de ofertas. Todas las ofertas están verificadas como legítimas.
- Alto porcentaje de trabajos en USD para empresas de EEUU/Canadá.
- La suscripción se puede cancelar y renovar según necesidad.
- **Recomendación:** Implementar en Fase 2, después de tener los portales gratuitos funcionando.
