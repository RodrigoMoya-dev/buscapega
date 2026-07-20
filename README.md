# Buscapega — Automatización de Búsqueda de Empleo

Buscapega es un sistema self-hosted de automatización para búsqueda y postulaciones de empleos. Es capaz de extraer ofertas de múltiples portales, valida tus capacidades, y ejecuta la postulacion de forma automática y luego te informa a tu whatsapp. Además, te permite revisarlas en una interfaz web y puede postularse automáticamente a los portales compatibles mediante automatización de navegador con Playwright, si el portal lo permite.

## Características

- **Puntuación con IA** — Cada oferta se evalúa contra tu perfil de candidato usando Claude (Anthropic)
- **Interfaz de revisión** — UI web para aceptar, descartar o auto-postularse a ofertas
- **Auto-postulación** — Automatización con Playwright para portales compatibles 
- **Notificaciones WhatsApp** — Recibe un mensaje cuando se envía una postulación
- **Totalmente Dockerizado** — Un solo comando para levantar todo

## Requisitos previos

- [Docker Desktop](https://docs.docker.com/get-docker/) (incluye Docker Compose)
- Python 3.9+ y `pip` (solo para la configuración de sesiones de portales)
- Una [Anthropic API Key](https://console.anthropic.com/) *(opcional)* — sin ella el sistema usa un evaluador local por palabras clave

## Instalación rápida

```bash
git clone https://github.com/RodrigoMoya-dev/buscapega.git
cd buscapega
./install.sh
```

El instalador hará lo siguiente:
1. Verificar que Docker esté disponible
2. Pedirte tu API key y configuración de notificaciones
3. Generar el archivo `docker/.env`
4. Construir e iniciar todos los servicios
5. Opcionalmente guiarte para configurar las sesiones de portales

Una vez finalizado, abre **http://localhost:3000** en tu navegador.

## Instalación manual

Si prefieres configurar el proyecto paso a paso:

**1. Clonar el repositorio**

```bash
git clone https://github.com/RodrigoMoya-dev/buscapega.git
cd buscapega
```

**2. Configurar las variables de entorno**

```bash
cp docker/.env.example docker/.env
```

Edita `docker/.env` y completa los valores requeridos:

| Variable | Obligatoria | Descripción |
|---|---|---|
| `ANTHROPIC_API_KEY` | No | Obtenerla en console.anthropic.com. Sin ella se usa evaluación local |
| `POSTGRES_PASSWORD` | Sí | Elige una contraseña segura |
| `NEXT_PUBLIC_API_URL` | Sí | URL del backend vista desde el navegador (por defecto: `http://localhost:8000`) |
| `GMAIL_USER` / `GMAIL_APP_PASSWORD` | No | Para portales que postulan vía email |
| `WHATSAPP_DEFAULT_PHONE` | No | Número de teléfono para notificaciones (sin el `+`) |

**3. Crear tu perfil de candidato**

```bash
cp perfil.ejemplo.md perfil.md
```

Edita `perfil.md` con tu stack tecnológico, expectativas salariales y preferencias de trabajo. El evaluador de IA usa este archivo para puntuar cada oferta.

**4. Iniciar todos los servicios**

```bash
cd docker
docker compose up -d
```

**5. Verificar que todo está funcionando**

```bash
docker compose ps
```

Los cuatro servicios deben aparecer como `Up`:

| Servicio | Puerto | Descripción |
|---|---|---|
| `db` | 5432 | PostgreSQL 16 |
| `backend` | 8000 | FastAPI — API, evaluador IA, orquestación |
| `scraper` | 8001 | FastAPI — scrapers + aplicadores Playwright |
| `frontend` | 3000 | Interfaz web Next.js 14 |

Abre **http://localhost:3000** para acceder a la interfaz.

## Uso

**Iniciar / detener**

```bash
cd docker

docker compose up -d            # iniciar todos los servicios
docker compose down             # detener todo
docker compose logs -f          # seguir logs (todos los servicios)
docker compose logs -f backend  # seguir logs de un servicio específico
```

**Buscar ofertas**

Haz clic en **Buscar ofertas** en la interfaz web, o dispáralo desde la API:

```bash
curl -X POST http://localhost:8000/api/scraper/trigger
```

**Revisar ofertas**

Abre http://localhost:3000. Las ofertas aparecen en la pestaña **Pendiente** con la puntuación de la IA. Desde ahí puedes:

- **Guardar** — reservar para más tarde
- **Descartar** — desestimar la oferta
- **Auto-postular** — enviar la postulación automáticamente (solo portales compatibles)
- **Marcar como postulado** — registrar una postulación manual

**Documentación del API**

Disponible en http://localhost:8000/docs cuando el backend está en ejecución.

## Configuración de sesiones para auto-postulación

Los portales con auto-postulación requieren una sesión de navegador guardada (cookies). Ejecuta esto en tu **máquina local** — abre un navegador real para que puedas hacer login:

```bash
cd setup
pip3 install -r requirements.txt
playwright install chromium

python3 setup_session.py --lista          # listar portales y estado de sesiones
python3 setup_session.py getonbrd         # capturar sesión de un portal
```

El script copia las cookies al volumen Docker automáticamente al finalizar.

## Portales compatibles

| Portal | Auto-postulación | Mercado |
|---|---|---|
| Tecnoempleo | Sí | España |
| GetOnBrd | Sí | LATAM / Chile |
| ChileTrabajos | Sí | Chile |
| Chumi-IT | Sí | LATAM / España |
| RemoteLatinos | Sí | LATAM / EEUU |
| FindJobIT | Sí | Internacional |
| Torre.ai | No | LATAM / EEUU |
| InfoJobs | No | España |
| Remotive | No | Internacional |
| RemoteOK | No | Internacional |
| LaraJobs | No | Internacional |
| FlexJobs | No | Internacional |

Los portales sin auto-postulación pueden marcarse como postulados manualmente desde la UI.

## Estructura del proyecto

```
buscapega/
├── docker/
│   ├── backend/      # FastAPI — API, evaluador, modelos de BD
│   ├── scraper/      # FastAPI — scrapers + aplicadores Playwright
│   ├── frontend/     # Interfaz web Next.js 14
│   ├── whatsapp/     # Servicio de notificaciones WhatsApp (Baileys)
│   └── docker-compose.yml
├── configuraciones/  # Scripts auxiliares (sesiones, Gmail, WhatsApp, smoke test)
├── grafica/          # Logo y paleta de colores oficiales
├── setup/            # Scripts de captura de sesiones (ejecutar en local)
├── documentos/       # Datos en tiempo de ejecución: portales.json, CV, configuración
├── perfil.md         # Tu perfil de candidato — lo lee el evaluador de IA
├── install.sh        # Instalador interactivo
└── sync-github.sh    # Sincronización con GitHub (uso del mantenedor)
```

## Solución de problemas

**El backend no arranca**
```bash
cd docker && docker compose logs backend
```

**El scraper no encuentra las cookies**

Asegúrate de haber ejecutado `setup_session.py` para ese portal y de que el volumen de cookies está montado correctamente.

**La puntuación IA no funciona**

Verifica que `ANTHROPIC_API_KEY` esté configurada en `docker/.env` y reinicia el backend:
```bash
cd docker && docker compose up -d --build backend
```

**Puerto en uso**

Edita `docker/docker-compose.yml` y cambia el mapeo de puertos del host (`"3000:3000"` → `"3001:3000"`, etc.).

## Licencia

MIT
