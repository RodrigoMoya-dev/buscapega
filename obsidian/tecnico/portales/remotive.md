# Portal: Remotive.com

**URL:** https://remotive.com  
**País:** Internacional  
**Enfoque:** Trabajos 100% remotos en empresas tech  
**Logo:** `https://remotive.com/favicon.ico`

---

## Método de acceso

**Método probable:** API pública (JSON) — opción preferida  
**Estado:** Por explorar — **alta prioridad, tiene API gratuita**

### ¿Tiene RSS o API?
- **Sí. Tiene API pública gratuita.**
- Endpoint principal:
  ```
  GET https://remotive.com/api/remote-jobs
  ```
- Parámetros:
  - `category`: categoría (ej. `software-dev`)
  - `search`: keywords (ej. `php laravel`)
  - `limit`: cantidad de resultados

Ejemplo:
```
https://remotive.com/api/remote-jobs?category=software-dev&search=php&limit=50
```

Respuesta en JSON:
```json
{
  "job-count": 12,
  "jobs": [
    {
      "id": 1234,
      "url": "https://remotive.com/remote-jobs/...",
      "title": "Senior PHP Developer",
      "company_name": "Acme Corp",
      "tags": ["php", "laravel", "remote"],
      "description": "<html>...",
      "salary": "$80k–$120k",
      "candidate_required_location": "Worldwide",
      "publication_date": "2026-04-15T10:00:00"
    }
  ]
}
```

### ¿Requiere login para ver ofertas completas?
- **No.** La API es pública y no requiere autenticación.

### ¿Tiene CAPTCHA o bloqueo anti-bot?
- **No aplica** — se usa la API oficial, no scraping.

### ¿Cómo se postula?
- Cada oferta tiene un `url` que lleva al detalle en Remotive o al portal de la empresa.
- La postulación es externa (portal de la empresa).
- **Tipo botón UI:** `Acceder (Abre una ventana nueva)` — no tiene formulario propio.

---

## Plan de implementación

1. Llamar al endpoint de la API con los parámetros de búsqueda relevantes.
2. Parsear el JSON y extraer los campos necesarios.
3. Limpiar el campo `description` (viene en HTML) con un parser.
4. Pasar descripción limpia al agente evaluador (Claude).
5. Guardar en BD.

---

## Notas adicionales

- **Este es el portal más fácil de implementar.** Empezar con este para el prototipo.
- Las ofertas están en inglés. El agente evaluador debe manejar inglés.
- La API no requiere key ni registro. Límite de uso: no documentado, pero razonable para uso personal.
- Categorías disponibles: `software-dev`, `devops-sysadmin`, `product`, `all-others`, etc.
