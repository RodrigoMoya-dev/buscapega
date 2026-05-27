# Portal: LaraJobs.com

**URL:** https://larajobs.com  
**País:** Internacional (enfoque Laravel/PHP)  
**Enfoque:** Empleos específicos para desarrolladores Laravel  
**Logo:** `https://larajobs.com/favicon.ico`

---

## Método de acceso

**Método probable:** Scraping directo (HTML estático) o RSS  
**Estado:** Por explorar — portal relativamente simple, baja probabilidad de anti-bot agresivo

### ¿Tiene RSS o API?
- LaraJobs históricamente ha tenido feed RSS.
- Verificar: `https://larajobs.com/feed` o `https://larajobs.com/rss`
- Si existe, esta es la opción preferida (más estable que scraping).

### ¿Requiere login para ver ofertas completas?
- No. Las ofertas son públicas sin login.
- La postulación redirige al sitio de la empresa o a un email.

### Parámetros de búsqueda (URL pattern)
```
https://larajobs.com/?search=<keywords>
```
Ejemplo búsqueda remota:
```
https://larajobs.com/?search=remote+php
```

### Estructura HTML (selectores CSS — pendiente verificar)
| Campo | Selector probable |
|---|---|
| Listado de ofertas | `.job` o `article` |
| Título | `h2` o `.job-title` |
| Empresa | `.company` |
| Tags/tecnologías | `.tags span` |
| Enlace detalle | `a` del título |

### ¿Tiene CAPTCHA o bloqueo anti-bot?
- Probabilidad baja. Portal pequeño y sin JS rendering complejo.
- Probar con `requests` + BeautifulSoup primero.

### ¿Cómo se postula?
- Enlace externo al portal de la empresa (Greenhouse, Lever, etc.) o email directo al empleador.
- LaraJobs actúa solo como directorio; no tiene formulario propio.
- **Tipo botón UI:** `Acceder (Abre una ventana nueva)` — sin formulario propio, redirige al sistema del empleador.

---

## Plan de implementación

1. Verificar si existe RSS/feed → usar como primera opción.
2. Si no hay RSS: scraping con `requests` + BeautifulSoup.
3. Filtrar ofertas con tags de interés: `php`, `laravel`, `remote`.
4. Extraer descripción completa desde el detalle de cada oferta.
5. Pasar al agente evaluador.

---

## Notas adicionales

- Portal muy especializado en Laravel. Alta relevancia para el perfil.
- Las ofertas suelen venir en inglés. El agente evaluador debe manejar ambos idiomas.
- Frecuencia de nuevas ofertas: media (no diaria). Scraping cada 12–24h es suficiente.
