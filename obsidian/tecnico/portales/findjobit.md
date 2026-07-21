# Portal: FindJobIT

**URL:** https://www.findjobit.com  
**Tipo:** Portal de empleo IT para Latinoamérica  
**Scraping:** Playwright (SPA/Next.js)  
**Postulación:** Email vía Gmail SMTP  
**Auto-apply:** ✅ Sí (cuando hay email de contacto disponible)  
**Periodicidad:** Cada 1 hora (workflow n8n)

---

## Criterios de búsqueda

- **País:** Chile (`/jobs/country/chile`)
- **Modalidad:** Remoto (filtrado por presencia de "Remoto" en la descripción)
- **Evaluación:** Claude evalúa la oferta contra el perfil del candidato
- **Score mínimo para aplicar:** 50/100 (configurable via `FINDJOBIT_MIN_SCORE`)

---

## Flujo de postulación

```
[n8n Cron cada 1h]
        │
        ▼
[POST /run/findjobit en scraper]
        │
        ▼
[Playwright → findjobit.com/jobs/country/chile]
        │  páginas 1, 2, 3
        ▼
[Para cada oferta]
        │
        ├─ ¿URL ya existe en BD? → OMITIR
        │
        ▼
[Ingestar en backend → Claude evalúa → score]
        │
        ├─ Score < 50 → OMITIR (guardada como PENDIENTE para revisión manual)
        │
        ▼
[Clic en "Aplicar" → extraer email + asunto del formulario]
        │
        ├─ Sin email → WhatsApp "requiere revisión manual" + OMITIR
        │
        ▼
[Detectar idioma del CV según la descripción]
        │  • "english required" → cv_en.pdf
        │  • por defecto → cv_es.pdf
        ▼
[Generar carta de presentación con Claude (Haiku)]
        │
        ▼
[Enviar email vía Gmail SMTP]
        │
        ├─ ✅ Éxito → WhatsApp "Postulación enviada" + estado = POSTULADA
        │
        └─ ❌ Error → WhatsApp "Error al postular" + estado = FALLIDA
```

---

## Asunto del email

El asunto sigue el formato que establece FindJobIT:

```
[Nombre Apellido] - Aplicar a vacante {Título del cargo} - Findjobit
```

Si el formulario ya provee un asunto, se usa ese (reemplazando `[Nombre]` por `Nombre Apellido`).

---

## Archivos CV

Los CVs deben estar en la raíz del proyecto (montada en `/buscapega` dentro del contenedor):

| Archivo | Idioma | Cuándo se usa |
|---------|--------|---------------|
| `cv_es.pdf` | Español | Por defecto |
| `cv_en.pdf` | Inglés | Cuando la oferta pide inglés explícitamente |
| `cv.pdf` | Fallback | Si no existen los anteriores |

---

## Configuración requerida

### Variables de entorno (en `~/docker/buscapega/.env`)

```env
GMAIL_USER=correo@ejemplo.com
GMAIL_APP_PASSWORD=xxxxxxxxxxxxxxxxxxxx   # App Password de Google
GMAIL_FROM_NAME=Nombre Apellido
WHATSAPP_DEFAULT_PHONE=56912345678
FINDJOBIT_MIN_SCORE=50
```

### Cómo obtener la App Password de Gmail

1. Ir a https://myaccount.google.com/security
2. Activar "Verificación en 2 pasos" (si no está activa)
3. Ir a https://myaccount.google.com/apppasswords
4. Crear: "Otro (nombre personalizado)" → escribir "Buscapega"
5. Copiar los 16 caracteres generados (sin espacios)
6. Pegar en `GMAIL_APP_PASSWORD` del `.env`

---

## Workflow n8n

**Nombre:** `FindJobIT — Postulación automática horaria`  
**Trigger:** Cron cada hora (`0 * * * *`)  
**Acción:** `POST http://localhost:8021/run/findjobit`

Para crear el workflow, importar desde n8n UI o usar la API:

```bash
curl -X POST http://presto:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: n8n_api_407ff1bfdb4df4d649f2e05581039805ac1dcd053d06c9f3" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "FindJobIT — Postulación automática horaria",
    "nodes": [...],
    "active": true
  }'
```

---

## Notificaciones WhatsApp

Todas las notificaciones van al número `+56912345678` vía el servicio Baileys.

| Evento | Mensaje |
|--------|---------|
| Postulación exitosa | ✅ *FindJobIT — Postulación enviada* (cargo, empresa, email destino) |
| Error al enviar email | ❌ *FindJobIT — Error al postular* (motivo) |
| Sin email de contacto | ⚠️ *FindJobIT — Requiere revisión manual* (link) |
| Oferta interesante sin email | 👀 *FindJobIT — Oferta interesante* (score, link) |

---

## Archivos del código

| Archivo | Descripción |
|---------|-------------|
| `docker/scraper/scrapers/findjobit.py` | Scraper Playwright |
| `docker/scraper/applicator/findjobit.py` | Aplicador email Gmail |
| `docker/scraper/main.py` | Endpoint `POST /run/findjobit` |

---

## Comandos útiles

```bash
# Disparar manualmente desde presto
curl -X POST http://localhost:8021/run/findjobit

# Ver logs del scraper
docker logs buscapega_scraper -f

# Verificar ofertas FindJobIT en BD
curl "http://localhost:8020/api/offers?status=POSTULADA" | python3 -m json.tool | grep -A5 '"portal": "FindJobIT"'
```
