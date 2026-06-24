# Tareas pendientes — Overhaul UI web (24/06/2026)

> Lote de mejoras de la interfaz web pedido por el usuario. Organizado por **rama por área
> de vista** (decisión del usuario). Cada área: se desarrolla local → push a gitea + github →
> merge a `main` (sin `obsidian/`) → push `main`. Al final: `./smoke-test.sh`.
> Se va tachando cada subtarea al completarla para poder retomar.

Decisiones tomadas:
- **Issue GitHub (General):** enlace directo prellenado a `issues/new` (sin token en frontend).
- **Subida colaborativa de portales:** DIFERIDA → ver "Prompt próxima iteración" al final.

---

## Rama `feature_header_iconos_24062026` — Header / navegación + General ✅
- [x] **H1 · Íconos flat en el menú.** SVG inline por enlace (Ofertas/Portales/Perfil/Configuración).
- [x] **A1 · Ocultar "Auto respuestas"** del nav. La página `/respuestas` queda, sin entrada en el menú.
- [x] **G1 · Reportar problema (issue GitHub).** Enlace en el header → `issues/new` con
      título/cuerpo prellenados por URL (sin token).
- [x] **D1 · Docs `obsidian/web/`** ya usan el nombre textual de cada vista en su título
      (no se renombran archivos para no romper enlaces). Verificado.

## Rama `fix_buscar_ofertas_24062026` — Ofertas (corrección) ✅
- [x] **O3 · "Buscar ofertas" parecía no hacer nada.** Dialog modal con spinner flat "Cargando…"
      y debajo "Buscando en --portal--" recorriendo `GET /api/portals`; cierra al terminar y recarga.

## Rama `feature_ofertas_ui_24062026` — Ofertas (mejoras) ✅
- [x] **O1 · Aviso de postulaciones bajo el título "Ofertas"** (banner movido debajo del encabezado).
- [x] **O2 · Ícono de robot** flat en ese cuadro de aviso.
- [x] **O4 · Quitar botones "Descartar" y "Bloquear empresa"** de la tarjeta. Portales sin
      auto-postulación muestran el texto del mensaje de API KEY de Anthropic.
- [x] **O5 · Mensaje corregido** → "Has postulado a N postulación(es)" (pluralización) + enlace
      "Ver mis postulaciones" que abre la pestaña "Enviadas".

## Rama `feature_portales_ui_24062026` — Portales ✅
- [x] **P1 · Fusionar "Validar sitio" y "Portales"** en `/authenticate`. Bloque "Validar sitio"
      con fondo índigo destacado; "Portales de empleo" con fondo slate. `/validate` redirige.
      "Validar sitio" ya quitado del nav (rama header).
- [x] **P3 · Explicación de "Validar sitio"** antes del campo URL, con ícono **(?)** que
      despliega ayuda.
- [x] **P4 · Acordeones por sección** (auto-postulación / revisables / sin scraping[vacío]) con
      conteo al compactar. La 3ª categoría queda vacía: el backend aún no la distingue (follow-up).
- [x] **P5 · Botón "Registrar sesión con Google"** (ícono Google) → diálogo persistente con el
      texto, comando `python3 setup/setup_session.py <slug>`, alternativa `claude /autentica` y
      botones de copiar.
- [x] **P6 · Fila de portal:** bandera con tooltip; **switch** Activo/Inactivo persistido vía
      `PATCH /api/portals/toggle` (backend: nuevo campo `active` + endpoint, probado en vivo);
      aviso de revisión manual al activar portales revisables; botón "Visitar" en los sin
      auto-postulación.

## Rama `feature_perfil_ui_24062026` — Configura tu perfil
- [ ] **C1 · Quitar las pestañas** CV (Español), CV (English) y Perfil. En su lugar: dos input
      file (CV español y CV inglés) y a continuación el formulario de perfil.

---

## Prompt próxima iteración — Subida colaborativa de portales (P2, diferido)

> **Objetivo:** hacer Wunen "colaborativo": cuando un usuario valida una URL de portal que NO
> está entre los precargados, ofrecerle subir ese portal nuevo al proyecto de GitHub para que
> pase a formar parte de los portales por defecto que ven todos.
>
> **Prompt:** "Implementa el flujo colaborativo de portales nuevos. En la vista Portales, cuando
> el usuario valida una URL y el portal no existe en `documentos/portales.json` (ni en los
> precargados), mostrar la opción 'Aportar este portal al proyecto'. Al confirmar, el backend
> debe: (1) generar la definición del portal (nombre, url, market, auto_apply, session_key) a
> partir de la validación; (2) crear una rama `portal_<slug>_<fecha>` en el repo GitHub
> `RodrigoMoya-dev/wunen` y abrir un PR con esa definición añadida a `documentos/portales.json`
> (o al catálogo de portales). Definir dónde vive el `GITHUB_TOKEN` (variable de entorno del
> backend, scope `repo`/`pull_request`), el manejo de errores (token ausente, rama existente,
> rate limit) y la UX de feedback (enlace al PR creado). Documentar en `obsidian/web/portales.md`
> y `obsidian/tecnico/`."
>
> **Notas/decisiones a resolver en esa iteración:** ¿validación previa automática del portal
> antes de permitir el aporte? ¿moderación de PRs? ¿evitar duplicados por dominio?
