# Portal: ChileTrabajos.cl

**URL:** https://www.chiletrabajos.cl  
**País:** Chile  
**Enfoque:** Empleos generales con sección TI  
**Logo:** `https://www.chiletrabajos.cl/favicon.ico`

---

## Método de acceso

**Método probable:** Playwright headless o scraping directo (pendiente verificar si bloquea)  
**Estado:** Por explorar

### ¿Tiene RSS o API?
- No se conoce API pública documentada.
- Pendiente verificar si hay feed RSS en `/rss` o `/feed`.

### ¿Requiere login para ver ofertas completas?
- Las ofertas suelen ser visibles sin login.
- La postulación requiere cuenta registrada.

### Parámetros de búsqueda (URL pattern)
```
https://www.chiletrabajos.cl/empleos/buscar?q=<keywords>&region=<region>
```
Ejemplo búsqueda remota PHP:
```
https://www.chiletrabajos.cl/empleos/buscar?q=php+remoto
```
*(Pendiente verificar URL pattern real)*

### Estructura HTML (selectores CSS — pendiente verificar)
| Campo | Selector probable |
|---|---|
| Listado de ofertas | `.job-listing` o `.empleo-item` |
| Título | `h2` o `h3` dentro del item |
| Empresa | `.empresa` o `.company-name` |
| Descripción | `.descripcion` |
| Enlace detalle | `a` del título |

### ¿Tiene CAPTCHA o bloqueo anti-bot?
- Pendiente verificar. Probar primero con requests simple antes de Playwright.

### ¿Cómo se postula?
- Formulario propio del portal mediante cuenta registrada.
- Requiere adjuntar CV desde la cuenta del usuario.
- **Tipo botón UI:** `Postular` — tiene formulario propio, automatizable con Playwright + sesión guardada.

---

## Plan de implementación

1. Probar acceso directo con `requests` + BeautifulSoup.
2. Si hay bloqueo, cambiar a Playwright.
3. Filtrar por categoría TI/Informática + keyword PHP/WordPress/Laravel.
4. Extraer detalle de cada oferta relevante.
5. Pasar al agente evaluador.

---

## Notas adicionales

- Portal orientado al mercado chileno. Útil para roles en CLP o híbridos con empresas chilenas.
- Presubir CV en formato PDF una vez que se cree la cuenta.
