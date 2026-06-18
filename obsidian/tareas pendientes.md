* Revisa si todas las tareas de este documento están realizadas, y en caso de estarlo márcalas como completadas. 

---

## Plan de trabajo — sesión 17/06/2026 (rama `feature_ui_mejoras_17062026`)

### Instalador
- [x] 1. Mensaje claro de que la Anthropic Key es OPCIONAL (no obligatoria) — también en el resumen final
- [x] 2. Indicar que teléfono y correo se pueden editar luego en `documentos/settings.json` o en la web (Configuración)
- [x] 3. Indicar el script para sincronizar WhatsApp (`./whatsapp-qr.sh`)
- [x] 4. Mostrar siempre el apartado con los dos comandos de Claude Code (`/valida`, `/autentica`)
- [x] 5. Arreglar fallo pip/playwright al configurar sesiones (ahora usa venv en `setup/.venv`)

### Web
- [x] 6. Mostrar el nombre de la persona ("Hola, Rodrigo") — ya implementado vía settings.json; se corrige al desplegar build actualizado
- [x] 7. Validación de estructura de URL en "Validar sitio" (cliente + servidor) y manejo de error de red/CORS
- [x] 8. Aclarar/generalizar las "keywords especiales para ChileTrabajos" en Auto respuestas
- [x] 9. Explicar en la UI cómo funcionan las respuestas automáticas (no se obtienen de un sitio web)
- [x] 10. Dejar findjobit.com activo por defecto (demo) — flag `demo_active` en backend
- [x] 11. Menú superior: causa raíz era el modo dev (frontend ahora corre en modo producción) + resaltado de enlace activo
- [x] 12. Configuración: teléfono y correo vienen del instalador (settings.json) — se corrige al desplegar
- [x] 13. Quitar/aclarar que la API de Anthropic es necesaria (mensaje del instalador aclarado; la web no la pide)
- [x] 14. Baileys (WhatsApp `./whatsapp-qr.sh`) y Gmail (`./setup-gmail.sh`): scripts en la raíz + aclaración en instalador

### Cierre
- [x] 15. Actualizar documentación en `/obsidian` (web/, tecnico/instalador.md, docker-compose.md)
- [ ] 16. Commit + push a gitea (origin)
- [ ] 17. Deploy a Presto

---

# Instalador 

* Sigue sin aparecer algun mensaje que indique que agregar una Key de Anthropic es opcional, no obligatorio. 
* Debiera indicar que en caso de no llenar los datos del teléfono y el correo, después puede modificarlos en --Colocar la ruta del archivo--
* En el instalador falta indicar el script para poder sincronizar el teléfono con whatsapp
* También sería bueno colocar un apartado de que, en el caso deque el usuario tenga Claude, mu
* estre los dos comandos creados para este proyecto que funcionan con Claude Code. 

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


