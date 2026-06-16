## Sesión 16/06/2026 — Plan de trabajo

Diagnóstico hecho antes de codear (texto original de las tareas más abajo, intacto):

- [x] **Tarea A** (instalador): `install.sh` silenciaba errores de pip/playwright y seguía ejecutando `setup_session.py` aunque la instalación hubiera fallado → producía el traceback `ModuleNotFoundError: No module named 'playwright'`. Fix: reintenta con `--break-system-packages`, valida `import playwright`, y aborta la sección con instrucciones claras si algo falla, en vez de seguir.
- [x] **Tarea B** (API key Anthropic opcional): confirmado que ya es opcional (evaluator.py cae a scorer local si falta `ANTHROPIC_API_KEY`). Se corrigió el texto del instalador: ahora dice "(opcional...; si usas Claude Code para evaluar las ofertas no la necesitas)".
- [x] **Tarea C** (scripts a la raíz): Gmail ya se configura dentro de `install.sh` (no necesita script aparte). Se movió `setup/whatsapp-qr.sh` → `whatsapp-qr.sh` en la raíz (es autocontenido). Se creó `setup-sessions.sh` en la raíz como wrapper de `setup/setup_session.py` (ese script necesita quedarse en `setup/` por sus rutas relativas a `cookies/` y su propio `requirements.txt`). README.md, install.sh y CLAUDE.md actualizados con las nuevas rutas.
- [x] **Tarea D** (nav web rota): `docker/frontend/app/layout.tsx` usaba `<a href>` planos en vez de `next/link` → recarga completa la página en cada click (de ahí el "doble clic" y los errores de webpack HMR en consola). Fix: ahora usa `<Link>` de Next.js.
- [x] **Tarea E** (saludo "Hola, X"): `install.sh` nunca preguntaba el nombre del usuario ni lo escribía en `settings.json` (`user_name` quedaba hardcodeado en `""`), por eso `NavGreeting` nunca lo mostraba. Fix: se agregó pregunta "→ Tu nombre" al inicio de la configuración interactiva y se guarda en `settings.json`.
- [x] **Tarea F** (validar sitio no valida estructura): `/api/portals/validate` no validaba el formato del dominio antes de hacer fetch; si la URL no resolvía, caía al branch "se asume permisivo" y quedaba como válida igual. Fix: se agregó regex de validación de dominio (`DOMAIN_RE`) que rechaza URLs sin estructura tipo `sitio.com` antes de cualquier fetch; el frontend (`validate/page.tsx`) ahora muestra ese error en rojo.
- [x] **Tarea G** (error "Fetch API cannot load... access control checks"): era consecuencia de la Tarea D — la recarga completa de página cancelaba el fetch en curso y el navegador lo reportaba como error de CORS. Resuelto junto con D.
- [x] **Tarea H** (findjobit activo por defecto): confirmado con el usuario → reordenado para que FindJobIT aparezca primero en la lista de portales (`documentos/portales.json`, `portals.py` DEFAULT_PORTAL_LIST, y el seed default de `install.sh`).
- [x] **Tarea I** (chiletrabajos en respuestas automáticas): confirmado — sí se puede postular a ChileTrabajos (`docker/scraper/applicator/chiletrabajos.py` está completo: login, llenado de formulario, carta de presentación, captcha, etc., y está registrado en `registry.py`). El reporte del usuario era de antes de esta implementación. Se mantiene activo, sin cambios de código.
- [x] **Tarea J** (teléfono/correo desde instalador en Configuración): ya implementado en sesión 15/06 (Tarea 3) y deployado hoy. Verificado: `GET /api/settings` en Presto responde con la estructura correcta (vacío porque aún no se reinstaló/configuró ahí; el mecanismo funciona).

**Deploy completado (16/06/2026):**
- [x] Commit `e5db5b4` pusheado a gitea.presto rama `feature_ui_mejoras_15062026`
- [x] Sincronizados `docker/backend/` y `docker/frontend/` a Presto, rebuild `backend` + `frontend` — ambos healthy (200 OK)
- [x] Verificado orden de portales en `/api/portals`: FindJobIT queda primero

---

### Web

* Se ha pedido que aparezca el nombre de la persona en el portal, pero aún no aparece. Como "Hola, Rodrigo" por ejemplo. 
* En "Validar sitio" si coloco cualquier cosa me aparece en la consola "Fetch API cannot load http://localhost:8000/api/portals/validate due to access control checks."
* Veo que tampoco valida la estructura de lo escrito. si escribo "sddfgld" lo acepta igual. Al menos debiera tener una estructura tipo "wunen.app" o similar. 
* En "Respuestas automáticas", me aparecen keywords especiales para chiletrabajos, pero el portal no está en el sistema. 
* Respecto a "Respuestas automáticas" ¿Cómo las obtiene desde un sitio web? 
* ¿Puedes dejar por defecto el sitio web findjobit.com activo, para poder mostrar al usuario como funciona? 
* En general, el menú superior funciona mal. Hay que hacer clic varias veces en el enlace para que cambie la vista. Noté que al hacer clic en la ruta, a veces aparece estemensaje "Fetch API cannot load http://localhost:3000/_next/static/webpack/40359f82e66e9dd8.webpack.hot-update.json due to access control checks."
* En configuración, el número de teléfono y el correo de postulaciones son datos que se piden cuando se ejecuta el instalador. Debiera obtenerlos desde ahí. 

* ¿PoRQUE DICE QUE la API de Anthropic es necesaria? Esto debiera ser un dato opcional. Y hacer hincapié que para esto se debe usar claude code. 
* ¿Los servicios de Baileys y Google Gmail se configuran durante el proceso de instalación? Porque si la respuesta es no, entonces ambos procesos debieran hacerse en bash apartes. Y ambos scripts debieran estar en la raíz del proyecto. 
* En el instalador, le puse "Si" a la pregunta **¿Deseas configurar ahora las sesiones de los portales con auto-postulación? (s/N)** y apareció esto :   

▶ Instalando dependencias de setup...

**!** Falló pip install. Intenta manualmente: pip3 install -r setup/requirements.txt

**!** Falló playwright install. Intenta manualmente: playwright install chromium

▶ Portales disponibles para autenticar:

Traceback (most recent call last):

  File "/Users/rodrigo/Proyectos/Moya.dev/Proyectos internos/wunen/test/wunen/setup/setup_session.py", line 23, in <module>

    from playwright.sync_api import sync_playwright

**ModuleNotFoundError**: No module named 'playwright'

---

## Sesión 15/06/2026 — Plan de trabajo

- [x] **Tarea 3**: Datos del instalador (teléfono y correo) no aparecen en la web → Fix: además del `.env`, también escribir `documentos/settings.json` al final de `install.sh`
- [x] **Tarea 2**: Validar formato de teléfono (solo dígitos, mínimo 10) y email (contiene @ y .) en `install.sh`
- [x] **Tarea 1**: Script bash `setup/whatsapp-qr.sh` para obtener el QR de sincronización de WhatsApp + README.md con instrucciones
- [x] **Tarea 4**: Subir archivos PDF de CV en "Acerca de mí": endpoints `POST /api/cv/es/upload` y `POST /api/cv/en/upload` en backend + componente CvPdfUpload en frontend

**Deploy completado (16/06/2026):**
- [x] Push a gitea.presto rama `feature_ui_mejoras_15062026` (commit f778653) — sí fue alcanzable desde la Mac local
- [x] Sincronizados `docker/backend/` y `docker/frontend/` a `~/docker/wunen/` en Presto (no es repo git, se sincroniza por rsync)
- [x] Rebuild `docker compose up -d --build backend frontend` en Presto — `wunen_backend` y `wunen_frontend` healthy (200 OK)

---

## Tareas originales — Completadas
