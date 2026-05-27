# Tecnologías del Proyecto Wunen

Stack completo utilizado para construir el sistema de automatización de postulaciones.

---

## Docker Compose — Servicios

| Servicio | Tecnología | Imagen base | Puerto |
|---|---|---|---|
| `db` | PostgreSQL 16 | `postgres:16-alpine` | 5432 |
| `backend` | FastAPI (Python 3.12) | `python:3.12-slim` | 8000 |
| `scraper` | Playwright + Python | `mcr.microsoft.com/playwright/python` | — |
| `frontend` | Next.js 14 (React) | `node:20-alpine` | 3000 |
| `scheduler` | APScheduler (dentro del backend) | — | — |

---

## Backend (FastAPI)

| Librería | Versión | Uso |
|---|---|---|
| `fastapi` | ^0.111 | Framework web principal |
| `uvicorn` | ^0.29 | Servidor ASGI |
| `sqlalchemy` | ^2.0 | ORM para PostgreSQL |
| `alembic` | ^1.13 | Migraciones de base de datos |
| `psycopg2-binary` | ^2.9 | Driver PostgreSQL |
| `pydantic` | ^2.7 | Validación de datos / schemas |
| `anthropic` | ^0.26 | SDK oficial de Claude API |
| `apscheduler` | ^3.10 | Scheduler de tareas (scraping periódico) |
| `httpx` | ^0.27 | Cliente HTTP async |
| `beautifulsoup4` | ^4.12 | Parsing de HTML scrapeado |
| `python-dotenv` | ^1.0 | Variables de entorno |

---

## Scraper

| Librería | Versión | Uso |
|---|---|---|
| `playwright` | ^1.44 | Browser automation headless |
| `beautifulsoup4` | ^4.12 | Parsing HTML |
| `lxml` | ^5.2 | Parser rápido para BeautifulSoup |
| `requests` | ^2.31 | HTTP simple para portales sin JS |

**Browsers instalados:**
- Chromium (principal)
- Firefox (fallback)

---

## Frontend (Next.js)

| Librería | Versión | Uso |
|---|---|---|
| `next` | 14.x | Framework React con SSR/SSG |
| `react` | 18.x | UI components |
| `react-dom` | 18.x | DOM renderer |
| `tailwindcss` | ^3.4 | Estilos utilitarios |
| `@tanstack/react-query` | ^5 | Fetching y caching de datos de la API |
| `axios` | ^1.6 | Cliente HTTP |
| `shadcn/ui` | latest | Componentes UI accesibles |

---

## Base de Datos (PostgreSQL)

**Motor:** PostgreSQL 16  
**ORM:** SQLAlchemy 2.0 con modelos declarativos  
**Migraciones:** Alembic

### Tablas principales

| Tabla | Descripción |
|---|---|
| `offers` | Ofertas scraped con estado (PENDIENTE, GUARDADA, DESCARTADA, ENVIADA) |
| `companies_blocked` | Empresas bloqueadas por el usuario |
| `applications` | Registro de postulaciones realizadas |
| `portals` | Configuración de los portales activos |

---

## Agente Evaluador (Claude API)

| Componente | Detalle |
|---|---|
| Proveedor | Anthropic |
| Modelo | `claude-sonnet-4-6` (balance costo/calidad) |
| SDK | `anthropic` Python SDK |
| Modo | Tool use / structured output (JSON) |
| Prompt caching | Habilitado para el system prompt (perfil del candidato) |

---

## Infraestructura

| Componente | Herramienta |
|---|---|
| Orquestación de contenedores | Docker Compose v2 |
| Volúmenes persistentes | Docker volumes (db_data, playwright_cookies) |
| Variables de entorno | `.env` file + `python-dotenv` |
| Reverse proxy (producción) | Nginx (pendiente, Fase 2) |

---

## Herramientas de Desarrollo

| Herramienta | Uso |
|---|---|
| VS Code / Cursor | IDE principal |
| Docker Desktop | Gestión visual de contenedores |
| Postman / HTTPie | Testing de endpoints API |
| pgAdmin (opcional) | Gestión visual de PostgreSQL |

---

## Versiones de Runtime

| Runtime | Versión |
|---|---|
| Python | 3.12 |
| Node.js | 20 LTS |
| PostgreSQL | 16 |
| Docker Engine | 26+ |
| Docker Compose | v2.x |
