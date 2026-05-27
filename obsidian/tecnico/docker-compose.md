# Artefacto: docker-compose.yml

**Archivo:** `/docker-compose.yml`  
**Versión:** Docker Compose v3.9

---

## Descripción

Orquesta los 5 servicios principales del sistema Wunen. Cada servicio corre en su propio contenedor aislado, comunicándose por la red interna de Docker.

---

## Servicios

### `db` — Base de datos PostgreSQL
- **Imagen:** `postgres:16-alpine`
- **Puerto expuesto:** `5432`
- **Volumen persistente:** `db_data` — los datos sobreviven reinicios del contenedor
- **Health check:** verifica que Postgres esté listo antes de iniciar servicios dependientes

### `backend` — API REST (FastAPI)
- **Build:** desde `./backend/Dockerfile`
- **Puerto expuesto:** `8000`
- **Depende de:** `db` (espera health check)
- **Variables clave:** `DATABASE_URL`, `ANTHROPIC_API_KEY`
- **Hot reload:** montaje de `./backend` como volumen para desarrollo

### `scraper` — Scraper headless (Playwright)
- **Build:** desde `./scraper/Dockerfile`
- **Sin puerto expuesto** — es invocado por el backend, no recibe tráfico externo
- **Volumen compartido:** `playwright_cookies` — compartido con backend para persistir sesiones

### `frontend` — Bandeja de revisión (Next.js)
- **Build:** desde `./frontend/Dockerfile`
- **Puerto expuesto:** `3000`
- **Depende de:** `backend`
- **Hot reload:** montaje de `./frontend` como volumen para desarrollo

---

## Volúmenes

| Nombre | Usado por | Propósito |
|---|---|---|
| `db_data` | `db` | Persistencia de datos PostgreSQL |
| `playwright_cookies` | `scraper`, `backend` | Cookies de sesión para portales que requieren login |

---

## Variables de entorno

Definidas en `.env` (copiar desde `.env.example`):

| Variable | Servicio | Descripción |
|---|---|---|
| `POSTGRES_DB` | `db`, `backend` | Nombre de la base de datos |
| `POSTGRES_USER` | `db`, `backend` | Usuario de PostgreSQL |
| `POSTGRES_PASSWORD` | `db`, `backend` | Contraseña de PostgreSQL |
| `ANTHROPIC_API_KEY` | `backend` | Clave API de Claude (Anthropic) |
| `NEXT_PUBLIC_API_URL` | `frontend` | URL del backend desde el navegador |
| `ENVIRONMENT` | `backend` | `development` o `production` |

---

## Comandos útiles

```bash
# Levantar todos los servicios
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f

# Reconstruir imagen de un servicio
docker compose build backend

# Ejecutar migraciones de BD
docker compose exec backend alembic upgrade head

# Abrir shell en el contenedor del backend
docker compose exec backend bash

# Detener y eliminar contenedores (datos se conservan en volúmenes)
docker compose down
```

---

## Próximo paso

Crear los `Dockerfile` individuales para `backend`, `scraper` y `frontend`.
