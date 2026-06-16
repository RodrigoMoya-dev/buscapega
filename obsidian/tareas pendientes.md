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




## Sesión 15/06/2026 — Plan de trabajo

- [x] **Tarea 3**: Datos del instalador (teléfono y correo) no aparecen en la web → Fix: además del `.env`, también escribir `documentos/settings.json` al final de `install.sh`
- [x] **Tarea 2**: Validar formato de teléfono (solo dígitos, mínimo 10) y email (contiene @ y .) en `install.sh`
- [x] **Tarea 1**: Script bash `setup/whatsapp-qr.sh` para obtener el QR de sincronización de WhatsApp + README.md con instrucciones
- [x] **Tarea 4**: Subir archivos PDF de CV en "Acerca de mí": endpoints `POST /api/cv/es/upload` y `POST /api/cv/en/upload` en backend + componente CvPdfUpload en frontend

**Pendiente de deploy:** Push a Gitea desde Presto (gitea.presto no es alcanzable desde la Mac local)
- Hacer desde Presto: `git push http://claude:Temporal2026!@gitea.presto/moya.dev/wunen.git feature_ui_mejoras_15062026`
- Luego rebuild del backend en Presto: `cd ~/docker/wunen && docker compose up -d --build backend frontend`

---

## Tareas originales — Completadas
