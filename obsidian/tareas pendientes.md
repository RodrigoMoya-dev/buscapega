# Tareas de la sesión (24/06/2026)

> Checklist de trabajo. Se va tachando a medida que se completa. Si se acaban los tokens,
> se retoma desde la primera tarea sin tachar.

## Documentación
- [x] **T0** — Revisar carpeta `/tecnico`: identificar info redundante/desactualizada y limpiar.

## Ofertas (`/`)
- [x] **T1** — Colección de checkboxes con portales **activos** para filtrar las ofertas por portal.
- [x] **T2** — Resumen bajo el título "Ofertas" con los trabajos encontrados en cada portal.

## Portales de empleo (`/authenticate`)
- [x] **T3** — Buscador en la zona superior (entre "Validar sitio" y "Portales de empleo") para buscar un portal por nombre.
- [x] **T4** — Cambiar el texto "Sin sesión" → "Sesión no iniciada".
- [x] **T5** — En "Validar sitio": si el sitio cumple (scraping + Google auth), permitir **agregarlo** a los portales, determinando automáticamente la categoría.
- [x] **T6** — Botón para **compartir** el portal recién agregado en el GitHub público.
- [x] **T7** — Texto que indique que con Claude Code se puede validar desde la terminal: `claude /valida <sitio>`.

## Registrar sesión con Google
- [x] **T8** — En el comando `/prueba`: validar que las librerías de Python (playwright, etc.) estén instaladas correctamente.

## Configuración (`/settings`)
- [x] **T9** — Al cambiar el nombre, recargar el saludo del menú superior automáticamente (sin recargar la página).
- [x] **T10** — "Enviar mensaje de prueba": validar que Baileys/WhatsApp esté configurado y activo; mensaje de error claro (no solo "error 503").
- [x] **T11** — Correo reply-to: checkbox para duplicar la información del correo de envío.

## Configura tu perfil (`/about`)
- [x] **T12** — Indicador de porcentaje de llenado del perfil (archivos + tecnologías + modalidades + todo = 100%).

## Reportar problema
- [x] **T13** — Tooltip que avise al usuario que abrirá una página de GitHub para subir el problema.

## Cierre
- [x] **T14** — Actualizar documentación en `obsidian/web/`.
- [x] **T15** — Subir ramas a gitea (`origin`) y github (`github`), mergear a `main` (sin `obsidian/`).
- [x] **T16** — Ejecutar `/prueba`.

---

# Resultado de `/prueba` (24/06/2026)

**Clon fresco de `main` (github) + `install.sh` → EXIT 0.** Todas las imágenes se construyeron y los
servicios arrancaron sanos. Validado en vivo:
- `GET /health` → ok · `GET /` (frontend) → HTTP 200.
- `GET /api/settings` → `user_name: "Test Prueba"` (lo escribió el instalador).
- `GET /api/portals` → expone `allows_scraping` en todos los portales (cambio de esta sesión).
- `POST /api/settings/test-whatsapp` → mensaje claro: _"WhatsApp no está vinculado (estado:
  waiting_qr). Escanea el código QR…"_ (antes solo "error 503"). ✓ T10
- `POST /api/portals/add` (scraping+Google) → categoría `auto_apply`. ✓ T5

> Contenedores de la demo quedaron arriba en :3000/:8000. Para bajarlos:
> `cd demo/docker && docker compose down`.

## ⚠️ Problema detectado — librerías de Python del host (a resolver por el usuario)

La validación de librerías (T8) detectó el error que reportaste:

```
$ python3 setup/setup_session.py <portal>
ModuleNotFoundError: No module named 'playwright'
```

**Causa raíz (corregida):** el comando que falla usa el `python3` del **sistema**, sin venv. El
instalador SÍ instala las dependencias, pero (a) solo si aceptas "configurar sesiones" y (b) en un
venv dedicado (`setup/.venv`). Los puntos de entrada `python3 setup/setup_session.py` y el wrapper
raíz `setup-sessions.sh` se saltaban ese venv.

**✅ Resuelto (rama `fix_setup_venv_24062026`, mergeada a `main`):**
- `setup-sessions.sh` ahora delega en `setup/run_setup.sh`, que crea `setup/.venv` e instala
  `playwright` + Chromium **automáticamente la primera vez**.
- El diálogo "Registrar sesión con Google" de la web ahora muestra `./setup-sessions.sh <slug>`
  (antes `python3 setup/setup_session.py <slug>`, que fallaba).

**Para el usuario:** ya no hace falta instalar nada a mano. Basta ejecutar, desde la raíz:
```bash
./setup-sessions.sh <portal>     # ej: ./setup-sessions.sh chiletrabajos
```
La primera ejecución crea el venv e instala las dependencias sola.
