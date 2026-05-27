# Portal: InfoJobs

**URL:** https://www.infojobs.net  
**País:** España  
**Enfoque:** El mayor portal de empleo de España — muy activo en tecnología e informática  
**Logo:** `https://www.infojobs.net/favicon.ico`

---

## Método de acceso

**Método probable:** Playwright headless con sesión  
**Estado:** Por implementar

### ¿Tiene RSS o API?
- InfoJobs tiene una API pública (requiere registro de app):
  ```
  https://api.infojobs.net/
  ```
- El acceso a la API requiere OAuth2. Registrar app en `https://developer.infojobs.net/`.
- Alternativa: scraping con Playwright si la API tiene restricciones.

### ¿Requiere login para ver ofertas completas?
- No. Las ofertas son públicas sin login.
- La postulación requiere cuenta de candidato registrada.

### Parámetros de búsqueda (URL pattern)
```
https://www.infojobs.net/ofertas-trabajo/informática-telecomunicaciones?q=<keywords>&locationId=&telecommute=1
```
Ejemplo búsqueda remota PHP:
```
https://www.infojobs.net/ofertas-trabajo/desarrollador-php?telecommute=1
```

### Estructura de URLs de ofertas
```
https://www.infojobs.net/oferta-trabajo/<slug>/<id>.xhtml
```

### ¿Tiene CAPTCHA o bloqueo anti-bot?
- Portal grande, puede tener protección anti-bot moderada.
- Playwright con delays aleatorios y sesión activa reduce el riesgo.
- La API oficial es la opción más confiable.

### ¿Cómo se postula?
- **Formulario propio del portal.** Se postula con el CV subido a InfoJobs y una carta de presentación opcional.
- Soporta múltiples CVs por cuenta.
- Permite ver el estado del proceso de selección.
- **Tipo botón UI:** `Postular` — automatizable con Playwright + sesión guardada.

---

## Plan de implementación

1. Registrar app en `developer.infojobs.net` para acceder a la API oficial.
2. Si la API tiene restricciones, usar Playwright con sesión guardada.
3. Buscar en categoría Informática/Telecomunicaciones con keywords `php`, `laravel`, `wordpress`.
4. Filtrar por modalidad `teletrabajo`.
5. Extraer descripción completa y pasar al agente evaluador.

---

## Notas adicionales

- **Mercado español:** ideal para empresas españolas que pagan en EUR.
- InfoJobs es el portal más grande de España — mayor volumen de ofertas tech.
- Las ofertas suelen incluir rango salarial, lo que facilita el filtrado por expectativa económica.
- Crear cuenta y subir CV en PDF. Guardar cookies de sesión en volumen Docker.
