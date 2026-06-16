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





### Web

* Se ha pedido que aparezca el nombre de la persona en el portal, pero aún no aparece. Como "Hola, Rodrigo" por ejemplo. 
* En "Validar sitio" si coloco cualquier cosa me aparece en la consola "Fetch API cannot load http://localhost:8000/api/portals/validate due to access control checks."
* Veo que tampoco valida la estructura de lo escrito. si escribo "sddfgld" lo acepta igual. Al menos debiera tener una estructura tipo "wunen.app" o similar. 
* En "Respuestas automáticas", me aparecen keywords especiales para chiletrabajos, pero el portal no está en el sistema. 
* Respecto a "Respuestas automáticas" ¿Cómo las obtiene desde un sitio web? 
* ¿Puedes dejar por defecto el sitio web findjobit.com activo, para poder mostrar al usuario como funciona? 
* En general, el menú superior funciona mal. Hay que hacer clic varias veces en el enlace para que cambie la vista. Noté que al hacer clic en la ruta, a veces aparece estemensaje "Fetch API cannot load http://localhost:3000/_next/static/webpack/40359f82e66e9dd8.webpack.hot-update.json due to access control checks."
* En configuración, el número de teléfono y el correo de postulaciones son datos que se piden cuando se ejecuta el instalador. Debiera obtenerlos desde ahí. 




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
