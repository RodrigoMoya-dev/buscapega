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
- [ ] **T15** — Subir ramas a gitea (`origin`) y github (`github`), mergear a `main` (sin `obsidian/`).
- [ ] **T16** — Ejecutar `/prueba`.
