# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is Wunen

Wunen is a personal job-search automation system. It scrapes job offers from multiple portals, evaluates each one against a candidate profile using Claude AI, presents them in a review UI, and can auto-apply to supported portals via Playwright browser automation.

## Commands

All Docker commands must run from the `docker/` directory (the canonical compose file is `docker/docker-compose.yml`):

```bash
cd docker

# Start all services
docker compose up -d

# Start a single service
docker compose up -d backend

# View logs
docker compose logs -f backend
docker compose logs -f scraper

# Restart after code changes (hot-reload is active in dev mode, but for Dockerfile changes)
docker compose up -d --build backend

# Stop everything
docker compose down
```

**Session setup** (runs on the local Mac, not in Docker — opens a visible browser):
```bash
cd setup
pip3 install -r requirements.txt
playwright install chromium

./setup-sessions.sh --lista          # list portals and session status (root wrapper, cds into setup/)
./setup-sessions.sh getonbrd         # capture session for a portal
```
After capturing, the script auto-rsync's cookies to `rodrigo@presto:~/docker/wunen/cookies/`.

**WhatsApp QR linking**: `./whatsapp-qr.sh [host] [port]` from the project root (self-contained, just curls the whatsapp service).

**API docs** (when backend is running): http://localhost:8000/docs  
**Frontend**: http://localhost:3000

## Architecture

### Services

| Service | Directory | Port | Description |
|---------|-----------|------|-------------|
| `db` | — | 5432 | PostgreSQL 16 |
| `backend` | `docker/backend/` | 8000 | FastAPI — API, evaluator, orchestration |
| `scraper` | `docker/scraper/` | 8001 | FastAPI — scrapers + Playwright applicators |
| `frontend` | `docker/frontend/` | 3000 | Next.js 14 review UI |

### Backend (`docker/backend/app/`)

- `main.py` — FastAPI app with CORS, creates tables on startup via `Base.metadata.create_all`
- `models.py` — SQLAlchemy models: `Offer`, `BlockedCompany`, `Application`
- `schemas.py` — Pydantic: `OfferIngest` (scraper → backend), `OfferResponse` (backend → frontend)
- `evaluator.py` — Calls `claude-sonnet-4-6` with **prompt caching** on the system prompt (candidate profile). Falls back to a local keyword-based scorer if `ANTHROPIC_API_KEY` is missing
- `routers/offers.py` — Full offer lifecycle: ingest, list, save, discard, autoapply
- `routers/scraper.py` — Proxies trigger to the scraper service
- `routers/companies.py` — Block/unblock companies

**Offer status lifecycle:**
```
PENDIENTE → GUARDADA | DESCARTADA | POSTULANDO → POSTULADA | PARCIAL | FALLIDA | ENVIADA
```

### Scraper (`docker/scraper/`)

- `main.py` — FastAPI with `/run`, `/run/<portal>`, `/apply` endpoints
- `scrapers/` — Portal scrapers: `remotive.py` and `remoteok.py` use public APIs; `getonbrd.py` uses HTTP
- `applicator/` — Auto-application system:
  - `base.py` — `BaseApplicator` abstract class: loads Playwright session from cookies file, validates session, detects CAPTCHA, calls `_do_apply()`, saves updated cookies
  - `result.py` — `ApplyResult` dataclass (`status: ok|parcial|fallido`, `requiere_humano`, `motivo`, `paso_alcanzado`, `url_continuar`)
  - `registry.py` — Maps portal name strings to applicator classes
  - Individual applicators: `getonbrd.py`, `tecnoempleo.py`, `remotelatinos.py`, `chiletrabajos.py`, `chumiit.py`
  - `cover_letter.py` — Generates cover letters via Claude API

### Frontend (`docker/frontend/`)

- `app/page.tsx` — Main inbox: tabs (Pendiente / Enviada / Descartada), filters by auto-apply portal and technology, auto-refreshes every 30 seconds
- `components/OfferCard.tsx` — Individual offer card with Save / Discard / Block company / Auto-apply actions
- `lib/api.ts` — Typed API client using `fetch`; base URL from `NEXT_PUBLIC_API_URL`

### Key Data Flows

**Scraping:** Frontend "Buscar ofertas" → `POST /api/scraper/trigger` → backend calls `scraper:8001/run` in background → scrapers fetch offers → each pushed to `POST /api/offers/ingest` → evaluator scores with Claude → saved as `PENDIENTE`

**Auto-apply:** `POST /api/offers/{id}/autoapply` → backend marks `POSTULANDO`, spawns background task → calls `scraper:8001/apply` (180s timeout) → portal applicator uses Playwright with stored session cookies → result saved to `applications` table + offer status updated → webhook fired to n8n → Telegram notification sent

**Session management:** Cookies live in Docker volume `playwright_cookies` (mounted at `/app/cookies` in scraper). `setup/setup_session.py` captures sessions locally in `setup/cookies/`, then rsync's to Presto where the volume is populated.

### Important Details

- `technologies` on `Offer` is stored as a JSON string (not JSONB): always `JSON.parse()` / `json.dumps()` when reading or writing
- The evaluator reads the candidate profile from `/wunen/perfil.md` inside the container. The `docker/docker-compose.yml` mounts the project root at `/wunen:ro`, so `perfil.md` must exist at the project root (not inside `obsidian/`). Edit `obsidian/persona/perfil.md` and copy/symlink to root to update the evaluator's profile
- Auto-apply portals (supported): Tecnoempleo, Chumi-IT, ChileTrabajos, RemoteLatinos, GetOnBrd, Torre.ai, InfoJobs
- Portals without auto-apply: LaraJobs, FlexJobs, Remotive, RemoteOK — use "Marcar como postulado" manually
- n8n webhook URL is set via `N8N_WEBHOOK_URL` env var (default: `http://localhost:5678/webhook/wunen-apply-result`)

### Environment Variables

Copy `docker/.env.example` to `docker/.env` before starting:

```
POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD
ANTHROPIC_API_KEY          # required for Claude evaluation
NEXT_PUBLIC_API_URL        # defaults to http://localhost:8000
N8N_WEBHOOK_URL            # optional, for Telegram notifications
```
