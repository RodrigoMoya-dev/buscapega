# Wunen — Kickoff: Automatización de Postulaciones a Empleo

## Idea central

Sistema semi-automático que busca ofertas de empleo en múltiples portales, las evalúa con Claude contra el perfil del candidato, y presenta una bandeja de revisión donde el usuario aprueba o descarta antes de postular.

---

## Flujo semi-automático definido

```
[Cron / Scheduler]
        │  (cada N horas)
        ▼
[Scraper por portal]   ──── extrae ofertas nuevas (Playwright o RSS/API)
        │
        ▼
[Agente evaluador]     ──── Claude analiza oferta vs perfil candidato
        │                   output: resumen, tecnologías, score, valor hora
        ▼
[Base de datos]        ──── guarda oferta con estado: PENDIENTE
        │
        ▼
[Frontend de revisión] ──── usuario ve bandeja, Guarda o Descarta
        │
        ▼
[Agente de postulación] ── genera carta personalizada + rellena formulario
        │
        ▼
[Registro CRM]         ──── estado: ENVIADA, fecha, respuesta recibida
```

---

## Servicios Docker Compose

```
services:
  db          # PostgreSQL — ofertas, empresas bloqueadas, historial
  backend     # FastAPI (Python) — orquesta agentes, expone API REST
  scraper     # Playwright headless — corre bajo demanda o por cron
  frontend    # React/Next.js — bandeja de revisión
  scheduler   # Cron interno (APScheduler o cron container)
```

### Por qué PostgreSQL y no SQLite
Múltiples servicios acceden a la BD simultáneamente (scraper escribe, backend lee, frontend consulta). SQLite no soporta escrituras concurrentes.

---

## Frontend — Bandeja de revisión

Cada tarjeta de oferta muestra:

| Campo | Fuente |
|---|---|
| Portal de origen | metadato del scraper |
| Título + empresa | scrapeado |
| Resumen del perfil buscado | generado por Claude |
| Tecnologías requeridas | extraídas por Claude (lista de tags) |
| Valor hora / salario | scrapeado si aparece, "No indicado" si no |
| Score de encaje (0–100) | calculado por Claude vs perfil |
| Enlace a la oferta original | URL scrapeada |

Acciones por oferta:
- **Guardar** → pasa a cola de postulación
- **Descartar** → archivada, no vuelve a aparecer
- **Bloquear empresa** → todas las futuras ofertas de esa empresa se descartan automáticamente

---

## Estrategia de scraping por portal

### Opción A — RSS/API (preferida si existe)
Algunos portales exponen feeds RSS o APIs públicas. Más estables, no requieren browser.

### Opción B — Playwright headless
Abre el portal como un usuario real. Requiere gestionar cookies/sesión. Más frágil pero universal.

### Opción C — Email digest
Algunos portales envían alertas por email. Se puede parsear el email en lugar de scrapear.

Para cada portal nuevo se necesita saber:
1. ¿Tiene RSS o API? (URL del feed)
2. ¿Requiere login para ver ofertas completas?
3. ¿Cuáles son los parámetros de búsqueda (URL pattern)?
4. ¿Cómo está estructurado el HTML de una oferta (selectores CSS)?
5. ¿Tiene CAPTCHA o bloqueo anti-bot?
6. ¿Cómo se postula — formulario propio, redirección externa, email?

---

## Portales objetivo y estado

| Portal | País | Método probable | Estado |
|---|---|---|---|
| tecnoempleo.com | España | Playwright (403 en scraping directo) | Por explorar |
| InfoJobs | España | API parcial disponible | Por explorar |
| LinkedIn Jobs | Global | Playwright con sesión | Complejo, fase 2 |
| Manfred | España | API pública | Por explorar |

---

## Agente evaluador (Claude)

Recibe el texto completo de la oferta y el perfil del candidato. Devuelve JSON:

```json
{
  "resumen": "Buscan desarrollador WordPress senior para ecommerce...",
  "tecnologias": ["WordPress", "PHP", "WooCommerce", "MySQL"],
  "modalidad": "remoto",
  "salario_estimado": "30–40€/h",
  "score": 82,
  "razon": "Encaja en stack principal, piden inglés B2 que cumples, salario dentro de rango"
}
```

---

## Perfil del candidato (a definir en `profile.md`)

- Stack tecnológico con nivel de experiencia
- Modalidad preferida
- Ubicación / disponibilidad geográfica
- Salario mínimo esperado
- Sectores o tipos de empresa preferidos/excluidos
- Idiomas

---

## Barreras técnicas conocidas

| Barrera | Impacto | Mitigación |
|---|---|---|
| Anti-bot / 403 | Alto | Playwright con browser real, delays aleatorios |
| Login requerido | Alto | Cookies persistentes en volumen Docker |
| CAPTCHA en postulación | Alto | Flujo semi-auto: usuario completa el envío final si hay CAPTCHA |
| CV upload programático | Medio | Presubir CV al portal una vez, reutilizar referencia |

---

## Próximos pasos

- [ ] Definir perfil del candidato en `profile.md`
- [ ] Investigar RSS/API de tecnoempleo.com e InfoJobs
- [ ] Definir schema de BD (tablas: `offers`, `companies_blocked`, `applications`)
- [ ] Scaffolding de Docker Compose con los 5 servicios
- [ ] Prototipo de scraper para tecnoempleo.com
- [ ] Prototipo de agente evaluador con Claude API
- [ ] UI básica de bandeja de revisión
