# Portal: GetOnBrd (Get on Board)

**URL:** https://www.getonbrd.com  
**País:** Chile / Latinoamérica  
**Enfoque:** Empleos tech y startups — la comunidad tech más grande de LATAM (1.4M+ profesionales, 15.000+ empresas)  
**Logo:** `https://www.getonbrd.com/favicon.ico`

---

## Método de acceso

**Método probable:** Scraping directo o Playwright  
**Estado:** Por implementar — **alta prioridad: es el portal tech más relevante de LATAM**

### ¿Tiene RSS o API?
- No tiene API pública documentada.
- Pendiente verificar feed RSS: `https://www.getonbrd.com/feed`

### ¿Requiere login para ver ofertas completas?
- No. Las ofertas son públicas.
- La postulación requiere cuenta registrada.

### Parámetros de búsqueda (URL pattern)
```
https://www.getonbrd.com/jobs/programming?search=<keywords>
```
Ejemplos:
```
https://www.getonbrd.com/jobs/programming?search=php+laravel
https://www.getonbrd.com/jobs/programming?search=wordpress
```

### Estructura de URLs de ofertas
```
https://www.getonbrd.com/jobs/programming/<slug-de-la-oferta>
```

### Estructura HTML (selectores CSS — pendiente verificar)
| Campo | Selector probable |
|---|---|
| Listado de ofertas | `[data-gb-component="job"]` o similar |
| Título | `h2` o `.job-title` |
| Empresa | `.company-name` |
| Tecnologías | `.tags` o `.skills` |
| Enlace detalle | `a` del título |

### ¿Tiene CAPTCHA o bloqueo anti-bot?
- Probabilidad baja. Portal chileno, sin protección agresiva conocida.
- Probar primero con `requests` + BeautifulSoup.

### ¿Cómo se postula?
- **Formulario propio del portal.** El usuario llena un formulario UNA SOLA VEZ y su perfil queda guardado.
- Las postulaciones posteriores toman solo unos minutos reutilizando el perfil.
- Permite seguimiento del estado de cada postulación.
- **Tipo botón UI:** `Postular` — automatizable con Playwright + sesión guardada.

---

## Plan de implementación

1. Probar acceso directo con `requests` + BeautifulSoup.
2. Si hay bloqueo, cambiar a Playwright.
3. Buscar en la sección `/jobs/programming` con keywords `php`, `laravel`, `wordpress`, `backend`, `remote`.
4. Extraer detalle de cada oferta relevante.
5. Pasar al agente evaluador.

---

## Notas adicionales

- **Portal más relevante para el perfil:** enfocado en tech, startups, y con alta presencia de empresas chilenas y LATAM.
- Las ofertas incluyen salario en USD/CLP, modalidad remota/híbrida, y stack tecnológico detallado.
- Frecuencia de nuevas ofertas: alta (varias diarias).
- Crear cuenta en el portal y guardar cookies en volumen Docker para automatizar postulaciones.
