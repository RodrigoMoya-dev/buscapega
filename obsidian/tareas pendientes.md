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

## Rama `feature_portales_ui_24062026` — Portales
- [ ] **P1 · Fusionar "Validar sitio" y "Portales"** en una sola vista. El bloque "Validar sitio"
      con un color de fondo destacado; "Portales de empleo" con otro color para diferenciarlos.
      Quitar "Validar sitio" del nav.
- [ ] **P3 · Explicar qué hace "Validar sitio"** antes del texto "Ingresa la URL de un portal…",
      con un ícono de info/pregunta.
- [ ] **P4 · Acordeones por sección** (con auto-postulación / revisables sin auto-postulación /
      sin scraping). Al compactar, mostrar tras el título la cantidad de portales de esa pestaña.
      Reemplaza los cuadros de comandos sueltos.
- [ ] **P5 · Botón "Registrar sesión con Google"** (con ícono) en portales con auto-postulación o
      revisables. Abre un dialog **persistente** con:
      - Texto "Registra tu sesión con Google aquí. Esta sesión quedará guardada sólo en tu equipo."
      - Input con el comando listo (`python3 setup/setup_session.py <login>`).
      - Alternativa con Claude Code.
      - Botón "copiar" en cada input.
- [ ] **P6 · Cambios por fila de portal:**
      - Bandera del país en vez del nombre (tooltip con el nombre al pasar el mouse).
      - Switch Activo/Inactivo. Si es autopostulación manual, aviso bajo el cuadro:
        "Portal activado. Importante: Te llegarán las ofertas pero deberás postular manualmente."
      - En portales sin auto-postulación, botón "Visitar" (con ícono) que abre la página.

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
