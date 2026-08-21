# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is Buscapega

Buscapega is a personal job-search automation system. It scrapes job offers from multiple portals, evaluates each one against a candidate profile using Claude AI, presents them in a review UI, and can auto-apply to supported portals via Playwright browser automation.

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

./configuraciones/setup-sessions.sh --lista          # list portals and session status (root wrapper, cds into setup/)
./configuraciones/setup-sessions.sh getonbrd         # capture session for a portal
```
After capturing, the script auto-rsync's cookies to the deploy server (configurable via the `PRESTO_COOKIES_PATH` env var, e.g. `usuario@servidor:~/docker/buscapega/cookies/`).

**WhatsApp QR linking**: `./configuraciones/vincular-whatsapp.sh [host] [port]` from the project root (self-contained, just curls the whatsapp service).

**API docs** (when backend is running): http://localhost:8000/docs  
**Frontend**: http://localhost:3000

## Installer (`install.sh` + `installer-web/`)

`install.sh` has three modes (single source of truth for all file generation and the build):

- **web** (default): launches a small Python-stdlib HTTP server (`installer-web/server.py`), prints a tokenized URL (both a `localhost` link and, if available, a LAN-IP link), and serves a WordPress-style wizard. On submit it runs `install.sh --apply` and streams its output to the browser via SSE. Works on any machine — a laptop accessed via localhost, or a headless server accessed from another machine over the network.
- **`--cli`**: the classic interactive terminal wizard.
- **`--apply`**: non-interactive mode used by the web installer. Reads answers from `BUSCAPEGA_*` env vars (`BUSCAPEGA_USER_NAME`, `BUSCAPEGA_WHATSAPP_PHONE`, `BUSCAPEGA_FRONTEND_PORT`, etc.), sets `NONINTERACTIVE=true`, and every `read` prompt falls back to a safe default (keep data / abort on conflicts / skip GUI session capture).

Container engine is **agnostic**: prefers Podman, falls back to Docker (`ENGINE=podman|docker` forces one). The web installer port is `BUSCAPEGA_WEB_PORT` (default 8090). The web layer never reimplements install logic — it only collects answers and shells out to `install.sh --apply`.

**Host resolution is machine-agnostic.** `NEXT_PUBLIC_API_URL` is baked as `http://localhost:<backend_port>` but the frontend (`lib/api.ts` → `resolveApiBase()` / exported `API_BASE`) swaps in `window.location.hostname` at runtime, so the app reaches the API via whatever host the browser used (localhost, LAN IP, or domain) with no baked IP and no rebuild if the IP changes. All pages using the API are `"use client"`, so this always runs in the browser.

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
- The evaluator reads the candidate profile from `/buscapega/perfil.md` inside the container. The `docker/docker-compose.yml` mounts the repo root at `/buscapega:ro`, so `perfil.md` must exist at the repo root. The editable source lives in the local docs vault at `../buscapega/persona/perfil.md` (folder `buscapega/`, sibling of the repo, outside version control). Edit it there and copy it to the repo root as `perfil.md` to update the evaluator's profile
- Auto-apply portals (supported): Tecnoempleo, Chumi-IT, ChileTrabajos, RemoteLatinos, GetOnBrd, Torre.ai, InfoJobs
- Portals without auto-apply: LaraJobs, FlexJobs, Remotive, RemoteOK — use "Marcar como postulado" manually
- n8n webhook URL is set via `N8N_WEBHOOK_URL` env var (default: `http://localhost:5678/webhook/buscapega-apply-result`)

### Environment Variables

Copy `docker/.env.example` to `docker/.env` before starting:

```
POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD
ANTHROPIC_API_KEY          # required for Claude evaluation
NEXT_PUBLIC_API_URL        # defaults to http://localhost:8000
N8N_WEBHOOK_URL            # optional, for Telegram notifications
```
