# Wunen — Job Search Automation

Wunen is a self-hosted job search automation system. It scrapes offers from multiple portals, scores each one against your profile using Claude AI, lets you review them in a web UI, and can automatically apply to supported portals via Playwright browser automation.

## Features

- **Multi-portal scraping** — Remotive, RemoteOK, GetOnBrd, Tecnoempleo, ChileTrabajos, and more
- **AI-powered scoring** — Each offer is evaluated against your candidate profile using Claude (Anthropic)
- **Review UI** — Web interface to accept, discard, or auto-apply to offers
- **Auto-apply** — Playwright-based automation for supported portals (Tecnoempleo, GetOnBrd, ChileTrabajos, Chumi-IT, RemoteLatinos, FindJobIT)
- **WhatsApp notifications** — Get notified when an application is submitted
- **Fully Dockerized** — One command to start everything

## Prerequisites

- [Docker Desktop](https://docs.docker.com/get-docker/) (includes Docker Compose)
- An [Anthropic API Key](https://console.anthropic.com/) (required for AI scoring)
- Python 3.9+ and `pip` (only needed for portal session setup)

## Quick Install

```bash
git clone https://github.com/RodrigoMoya-dev/wunen.git
cd wunen
./install.sh
```

The installer will:
1. Check for Docker
2. Ask for your API key and notification settings
3. Generate `docker/.env`
4. Build and start all services
5. Optionally walk you through portal session setup

Once done, open **http://localhost:3000** in your browser.

## Manual Installation

If you prefer to set things up step by step:

**1. Clone the repository**

```bash
git clone https://github.com/RodrigoMoya-dev/wunen.git
cd wunen
```

**2. Configure environment variables**

```bash
cp docker/.env.example docker/.env
```

Edit `docker/.env` and fill in the required values:

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Get it at console.anthropic.com |
| `POSTGRES_PASSWORD` | Yes | Choose a secure password |
| `NEXT_PUBLIC_API_URL` | Yes | Backend URL seen from the browser (default: `http://localhost:8000`) |
| `GMAIL_USER` / `GMAIL_APP_PASSWORD` | No | For portals that apply via email |
| `WHATSAPP_DEFAULT_PHONE` | No | Phone number for notifications (no `+`) |

**3. Create your candidate profile**

```bash
cp perfil.ejemplo.md perfil.md   # if the file doesn't exist yet
```

Edit `perfil.md` with your tech stack, salary expectations, and work preferences. The AI evaluator reads this file to score each offer.

**4. Start all services**

```bash
cd docker
docker compose up -d
```

**5. Verify everything is running**

```bash
docker compose ps
```

All four services should show as `Up`:

| Service | Port | Description |
|---|---|---|
| `db` | 5432 | PostgreSQL 16 |
| `backend` | 8000 | FastAPI — API, AI evaluator, orchestration |
| `scraper` | 8001 | FastAPI — scrapers + Playwright applicators |
| `frontend` | 3000 | Next.js review UI |

Open **http://localhost:3000** to access the interface.

## Usage

**Start / stop**

```bash
cd docker

docker compose up -d       # start all services
docker compose down        # stop everything
docker compose logs -f     # follow logs (all services)
docker compose logs -f backend   # follow a single service
```

**Scrape offers**

Click **Buscar ofertas** in the web UI, or trigger it via the API:

```bash
curl -X POST http://localhost:8000/api/scraper/trigger
```

**Review offers**

Open http://localhost:3000. Offers appear in the **Pendiente** tab scored by the AI. You can:
- **Guardar** — save for later
- **Descartar** — dismiss
- **Auto-postular** — submit the application automatically (supported portals only)
- **Marcar como postulado** — mark as applied manually

**API documentation**

Available at http://localhost:8000/docs when the backend is running.

## Portal Session Setup (for Auto-Apply)

Auto-apply portals require a stored browser session (cookies). Run this on your **local machine** — it opens a real browser window so you can log in:

```bash
cd setup
pip3 install -r requirements.txt
playwright install chromium

python3 setup_session.py --lista           # list portals and session status
python3 setup_session.py getonbrd          # capture session for one portal
```

After capturing, the script copies the cookies to the Docker volume automatically.

## Supported Portals

| Portal | Auto-Apply | Market |
|---|---|---|
| Tecnoempleo | Yes | Spain |
| GetOnBrd | Yes | LATAM / Chile |
| ChileTrabajos | Yes | Chile |
| Chumi-IT | Yes | LATAM / Spain |
| RemoteLatinos | Yes | LATAM / USA |
| FindJobIT | Yes | International |
| Torre.ai | No | LATAM / USA |
| InfoJobs | No | Spain |
| Remotive | No | International |
| RemoteOK | No | International |
| LaraJobs | No | International |
| FlexJobs | No | International |

Portals without auto-apply can be marked as applied manually from the UI.

## Project Structure

```
wunen/
├── docker/
│   ├── backend/      # FastAPI — API, evaluator, DB models
│   ├── scraper/      # FastAPI — scrapers + Playwright applicators
│   ├── frontend/     # Next.js 14 review UI
│   ├── whatsapp/     # WhatsApp notification service (Baileys)
│   └── docker-compose.yml
├── setup/            # Portal session capture scripts (run locally)
├── documentos/       # Runtime data: portales.json, CV, settings
├── perfil.md         # Your candidate profile — read by the AI evaluator
├── install.sh        # Interactive installer
└── sync-github.sh    # Sync to GitHub (maintainer use)
```

## Troubleshooting

**Backend not starting**
```bash
cd docker && docker compose logs backend
```

**Scraper can't find cookies**

Make sure you ran `setup_session.py` for the portal and that the cookies volume is mounted correctly.

**AI scoring not working**

Check that `ANTHROPIC_API_KEY` is set in `docker/.env` and restart the backend:
```bash
cd docker && docker compose up -d --build backend
```

**Port already in use**

Edit `docker/docker-compose.yml` and change the host port mappings (`"3000:3000"` → `"3001:3000"`, etc.).

## License

MIT
