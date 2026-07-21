# Portal: Tecnoempleo.com

**URL:** https://www.tecnoempleo.com  
**País:** España  
**Enfoque:** Tecnología e informática  
**Logo:** `https://www.tecnoempleo.com/favicon.ico`

---

## Método de acceso

**Método probable:** Playwright headless  
**Estado:** Por explorar

### ¿Tiene RSS o API?
- Revisar si existe feed en `/feed` o `/rss`. Históricamente no expone API pública documentada.
- Pendiente verificar: `https://www.tecnoempleo.com/ofertas-trabajo/rss`

### ¿Requiere login para ver ofertas completas?
- Las ofertas básicas son visibles sin login.
- El detalle completo y el formulario de postulación pueden requerir cuenta.

### Parámetros de búsqueda (URL pattern)
```
https://www.tecnoempleo.com/busqueda-empleo.php?te=<keywords>&tp=<tipo>&pais=<pais>
```
Ejemplo de búsqueda remota PHP:
```
https://www.tecnoempleo.com/busqueda-empleo.php?te=php&tp=teletrabajo
```

### Estructura HTML (selectores CSS — pendiente verificar)
| Campo | Selector probable |
|---|---|
| Listado de ofertas | `.oferta` o `.job-item` |
| Título | `h2 a` dentro del item |
| Empresa | `.empresa` |
| Descripción corta | `.descripcion` |
| Enlace al detalle | `href` del título |

### ¿Tiene CAPTCHA o bloqueo anti-bot?
- Se conoce que devuelve **403** en scraping directo (sin browser real).
- Solución: Playwright con User-Agent real + delays aleatorios entre requests.
- Posible necesidad de rotar User-Agent.

### ¿Cómo se postula?
- Formulario propio en el portal con un clic desde la cuenta del candidato.
- Soporta hasta 5 CVs diferentes por cuenta. Permite ver estado del proceso (rechazado, en proceso, preseleccionado, finalista).
- Puede redirigir al portal de empleo de la empresa en algunos casos.
- **Tipo botón UI:** `Postular` — tiene formulario propio, automatizable con Playwright + sesión guardada.

---

## Plan de implementación

1. Abrir con Playwright la URL de búsqueda.
2. Esperar carga completa (JS rendering).
3. Extraer listado de ofertas con selectores CSS.
4. Por cada oferta, navegar al detalle y extraer texto completo.
5. Pasar texto completo al agente evaluador (Claude).
6. Guardar en BD con estado `PENDIENTE`.

---

## Notas adicionales

- Crear cuenta en el portal para poder postular desde el agente.
- Guardar cookies en volumen Docker para sesión persistente.
- Implementar delay de 3–8 segundos aleatorio entre requests para evitar bloqueo.
