# Portal: RemoteOK.com

**URL:** https://remoteok.com  
**País:** Internacional  
**Enfoque:** Trabajos remotos en tecnología  
**Logo:** `https://remoteok.com/favicon.ico`

---

## Método de acceso

**Método probable:** API pública (JSON) — opción preferida  
**Estado:** Por explorar — **tiene API pública**

### ¿Tiene RSS o API?
- **Sí. Tiene API pública JSON.**
- Endpoint:
  ```
  GET https://remoteok.com/api
  ```
- Devuelve todas las ofertas recientes en JSON (sin filtros de búsqueda directos en la API, se filtran localmente).

Ejemplo de respuesta (objeto por oferta):
```json
{
  "id": "remote-ok-12345",
  "url": "https://remoteok.com/remote-jobs/...",
  "title": "Senior PHP Developer",
  "company": "Acme Corp",
  "tags": ["php", "laravel", "backend"],
  "description": "<p>...",
  "salary_min": 60000,
  "salary_max": 100000,
  "date": "2026-04-15T10:00:00"
}
```

### ¿Requiere login para ver ofertas completas?
- **No.** La API es pública y no requiere autenticación.

### ¿Tiene CAPTCHA o bloqueo anti-bot?
- No aplica para la API. Sin embargo, RemoteOK puede rate-limitar requests muy frecuentes.
- Respetar un intervalo mínimo de 1–2 minutos entre consultas.
- La API tiene un primer elemento "legal" que no es una oferta — hay que ignorarlo.

### ¿Cómo se postula?
- Cada oferta tiene una `url` que lleva al portal de la empresa.
- La postulación es completamente externa.

---

## Plan de implementación

1. Llamar a `https://remoteok.com/api` (con header `User-Agent` para evitar bloqueo).
2. Ignorar el primer elemento del array (es el aviso legal de RemoteOK).
3. Filtrar localmente por `tags` relevantes: `php`, `laravel`, `wordpress`, `backend`, `remote`.
4. Limpiar el campo `description` (HTML) con un parser.
5. Pasar al agente evaluador.

```python
import requests

headers = {"User-Agent": "Mozilla/5.0 (compatible; Wunen/1.0; job-scraper for personal use)"}
response = requests.get("https://remoteok.com/api", headers=headers)
jobs = response.json()[1:]  # skip first legal notice
```

### ¿Cómo se postula?
- Redirección directa al portal de la empresa (Greenhouse, Lever, etc.). No hay formulario propio.
- **Tipo botón UI:** `Acceder (Abre una ventana nueva)` — confirmado, redirige a sistema externo de la empresa.

---

## Notas adicionales

- **Segunda opción más fácil de implementar** (después de Remotive) por tener API.
- Las ofertas están en inglés, orientadas a empresas globales.
- El salary_min/salary_max suele estar en USD anuales (no por hora). Convertir al comparar con expectativas.
- Frecuencia de actualización: alta (varias ofertas diarias).
