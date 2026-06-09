# Tareas Pendientes — Sesión 09/06/2026

## Objetivo
Ordenar la aplicación para que pueda ser usada por cualquier usuario, tenga o no acceso a Claude Code. Crear instalador, comandos Claude y nueva interfaz web.

---

## Lista de tareas

### Backend
- [ ] Endpoint `/api/stats` — resumen de postulaciones (semana, total, por portal)
- [ ] Router `cv.py` — leer/guardar datos de CV y perfil (cv_data.json, cv_data_en.json, perfil_data.json)
- [ ] Router `settings.py` — leer/guardar configuración (settings.json: teléfono WA, emails)
- [ ] Router `portals.py` — listar portales con estado y conteo de postulaciones
- [ ] Registrar nuevos routers en `main.py`

### Frontend
- [ ] Actualizar `layout.tsx` — navegación completa con todas las páginas
- [ ] Actualizar `page.tsx` — agregar banner resumen de postulaciones semanales
- [ ] Crear `app/validate/page.tsx` — página "Validar sitio" con botón para ejecutar /valida
- [ ] Crear `app/authenticate/page.tsx` — página "Autenticar portales" con listado y estado
- [ ] Crear `app/about/page.tsx` — página "Acerca de mí" con 3 tabs (CV español, CV inglés, Perfil)
- [ ] Crear `app/settings/page.tsx` — página "Configuración" (teléfono WA, email)
- [ ] Actualizar `lib/api.ts` — agregar funciones para nuevos endpoints

### Comandos Claude Code
- [ ] Crear `.claude/commands/valida.md` — comando `/valida <url>`
- [ ] Crear `.claude/commands/autentica.md` — comando `/autentica`

### Instalador
- [ ] Crear `install.sh` — instalador Docker completo con prompts interactivos

### Deploy
- [ ] Commit y push a Gitea (rama: `feature_wunen_presto_whatsapp_findjobit_26052026`)

---

## Notas técnicas
- Los datos del CV se guardarán como JSON en `/wunen/cv_data.json` (ES), `/wunen/cv_data_en.json` (EN)
- El perfil se guarda en `/wunen/perfil_data.json` (structured) y regenera `perfil.md`
- Los settings van en `/wunen/settings.json`
- Los archivos se montan desde el host vía volume en docker-compose
- La validación de portales hace: check robots.txt + check Google OAuth en la página
- "Ejecutar desde web" = el backend llama al subprocess claude CLI o implementa la lógica directamente en Python
