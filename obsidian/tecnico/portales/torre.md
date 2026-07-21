# Portal: Torre.ai

**URL:** https://torre.ai  
**País:** Internacional (fuerte presencia LATAM y EEUU)  
**Enfoque:** Empleos tech remotos — matching con IA, perfil profesional detallado  
**Logo:** `https://torre.ai/favicon.ico`

---

## Método de acceso

**Método probable:** Scraping con Playwright o API pública  
**Estado:** Por implementar

### ¿Tiene RSS o API?
- Torre expone una API pública para búsqueda de empleos.
- Endpoint de búsqueda:
  ```
  POST https://search.torre.ai/opportunities/_search
  ```
  Body JSON con filtros de skills, modalidad, etc.
- Pendiente verificar documentación actualizada en `https://torre.ai/developers`.

### ¿Requiere login para ver ofertas completas?
- No. Las ofertas son públicas.
- La postulación requiere cuenta registrada con perfil completo.

### Parámetros de búsqueda (URL pattern)
```
https://torre.ai/jobs?skills=php,laravel&remote=true
```

### Estructura de URLs de ofertas
```
https://torre.ai/post/<slug-de-la-oferta>
```

### ¿Tiene CAPTCHA o bloqueo anti-bot?
- Tiene cierta protección. Usar Playwright con delays y User-Agent real.
- La API pública es más confiable que el scraping de HTML.

### ¿Cómo se postula?
- **Plataforma propia.** Se postula desde el perfil de Torre, que incluye habilidades, experiencia, objetivos y disponibilidad.
- El sistema de IA de Torre rankea candidatos según la compatibilidad con la oferta.
- Los screening questions se responden dentro de la plataforma.
- **Tipo botón UI:** `Postular` — automatizable con Playwright + cuenta registrada con perfil completo.

---

## Plan de implementación

1. Explorar la API pública de Torre (`search.torre.ai/opportunities/_search`).
2. Filtrar por skills: `php`, `laravel`, `wordpress`, `backend`.
3. Filtrar por `remote: true` y zona horaria LATAM.
4. Extraer descripción y requisitos de cada oferta.
5. Pasar al agente evaluador.

---

## Notas adicionales

- Torre tiene un enfoque de "perfil profesional profundo" — requiere completar el perfil con detalle para aparecer bien rankeado.
- Muchas empresas de EEUU contratan talento LATAM a través de Torre.
- Pagos en USD muy frecuentes.
- El perfil de Torre actúa como CV vivo — vale la pena mantenerlo actualizado.
