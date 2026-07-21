
### Instalador 

* ¿Puedes darle un efecto de "estrella" al color azul que tiene el robot? Para darle el efecto de bandera chilena. 

* Los mensajes de error del instalador ¿Los puedes colocar de otro color? No se entiende a primera vista que es un error. Adjunto evidencia. ![[Pasted image 20260721142909.png]]
* ¿Es posible, si un puerto está usado, informar cual es? 
* Volví a ejecutar el instalador una vez recomenzó y me vuelve a pedir los datos. ¿No es posible guardarlos en un archivo de texto cuando se van registrando, y que se moifiquen solo si el usuario lo elije? 
* Dos cosas adicionales que se ven en la imagen : 
	* Los contenedores dicen wunen- algo, cuando debiera salir buscapega- algo. 
	* ¿Es posible que a la información del paso siguiente, se coloque un color más notorio? 


	![[Pasted image 20260721143427.png]]


# Web 

### Ofertas 

* En los portales sólo debiera mostrar portales donde el usuario se haya autenticado, o el portal no requiera autentificación. 

### Portales de empleo 

* Falta un mensaje destacado en los portales donde la sesión con Google no esté iniciada. También, agregar bajo el titulo "Portales con autopostulación" una explicación de porqué se debe registrar la sesión con Google (Si se registra el sistema puede buscar postulaciones y autopostular según los criterios). 


### Configuración 

* ¿Es posible que los mensajes de aviso, por ejemplo el que aparece al mandar mensaje de prueba por whatsapp, queden fijos y tengan un botón de cierre? 
* El texto bajo "Configurar Whatsapp (Baileys)" hace mención a presto, pero el proyecto está funcionando local bajo una carpeta local. NO DEBE HABER NINGUNA REFERENCIA A PRESTO. 
* También veo que el docker dice "wunen_whatsapp". Todas las menciones de  wunen debieran decir "buscapega" que es el nuevo nombre. 



### Otros 

¿Puedes hacer un manual para la creación de una página en github pages? Para crear una página llamada buscapega . No sé si puede ser buscapega.github.io 

Crealo bajo el nombre "Creación de página github.md"

---

# PLAN DE TRABAJO — sesión 21/07/2026

Hallazgos del análisis previo, antes de tocar código:

- **El bug de "vuelve a pedir los datos" está localizado.** Ya existe `.install-config`
  y la función `guardar_config()` (install.sh:105). El fallo está en `install.sh:423`:
  la condición es `if $RESUME && [[ -f "$CONFIG_FILE" ]]`, y `RESUME` solo se pone en
  `true` dentro del bloque `if [[ -f "$STATE_FILE" ]]` (línea 235). Si el instalador
  muere **antes** de marcar el primer paso costoso, no hay `STATE_FILE` → nunca se
  ofrece reanudar → `RESUME=false` → **se ignora el `.install-config` que sí existe**
  y se repregunta todo. Hay que desacoplar la reutilización de config del `STATE_FILE`.
- **`warn()` se usa tanto para avisos como para errores no fatales** (install.sh:53),
  ambos en amarillo con `!`. Por eso "Teléfono inválido" no se lee como error. Hace
  falta una función `fail()` en rojo, distinta de `error()` (que además hace `exit 1`).
- **Rebranding: 93 ocurrencias de `wunen`** en 22 archivos versionados. Incluye
  `name: wunen` (proyecto compose), 5 `container_name`, el mount `..:/wunen` y la ruta
  `/wunen/perfil.md` que lee el evaluador. **Riesgo de pérdida de datos** — ver abajo.

## ⚠️ Decisión bloqueante: volúmenes de Docker

`docker/docker-compose.yml:1` declara `name: wunen`. Ese nombre **prefija los volúmenes**:
`wunen_db_data`, `wunen_playwright_cookies`, `wunen_whatsapp_auth`. Si se cambia a
`buscapega` sin más, Docker crea volúmenes nuevos y vacíos: **se pierde la base de datos,
las cookies de sesión de los portales y la vinculación de WhatsApp**. Pendiente de
confirmar con Rodrigo cómo proceder (migrar / empezar limpio / mantener nombres físicos).

## Ramas

### `fix_instalador_ux_21072026` (correcciones) — ✅ COMPLETADA
- [x] `fail()` en rojo (`✗`) para errores no fatales; aplicado a "Teléfono inválido",
      "Correo inválido", "No se pudo eliminar el volumen", "No se pudo crear el venv" y
      "No se pudo capturar sesión". Se deja `warn()` amarillo solo para avisos que **no**
      son fallos (p. ej. "el build puede morir por memoria")
- [x] Puerto ocupado: ahora informa comando, PID y usuario; si lo publica Docker, además
      el nombre del contenedor, y sugiere el `kill` / `docker stop` concreto.
      Probado con stubs en los 3 casos (proceso normal / contenedor / puerto libre)
- [x] Reutilizar `.install-config` aunque no exista `STATE_FILE` + pregunta explícita
      "¿Usar estos datos? (S/n)". Probado el caso exacto del reporte: hay config, no hay
      state-file → antes repreguntaba todo, ahora reutiliza
- [x] `nota()` con barra naranja de la marca para la información del paso siguiente
      (el azul inicial se probó y quedaba invisible sobre fondo negro)

### `feature_instalador_robot_estrella_21072026` (mejora) — ✅ COMPLETADA
- [x] Estrella blanca (`✦`) sobre el cantón azul del pecho del robot.
      Se pinta como **fondo** azul + glifo blanco, no como carácter azul, para que la
      estrella quede recortada dentro del cuadro y no abra un hueco negro.
      No se usó `★`: `unicodedata.east_asian_width` lo clasifica **A** (Ambiguous) y
      muchos terminales lo pintan a doble ancho; `✦` (U+2726) es **N**, ancho 1 seguro.
      Verificada la alineación: las dos filas del pecho miden 15 columnas igual que antes.

### `fix_rebranding_wunen_buscapega_21072026` (corrección) — ✅ COMPLETADA
- [x] `wunen` → `buscapega`: 93 ocurrencias en 22 archivos + los 36 docs de obsidian.
      Incluye `name:` del proyecto compose, los 5 `container_name`, el mount
      `..:/buscapega`, `/buscapega/perfil.md`, `POSTGRES_DB/USER` y el renombre de
      `setup/wunen-daily.sh` → `setup/buscapega-daily.sh`
- [x] **Empezar limpio** (decisión de Rodrigo): el instalador detecta los restos
      `wunen_*` (contenedores y volúmenes), explica qué se pierde y ofrece eliminarlos
- [x] Referencias a Presto eliminadas del producto: instrucciones de WhatsApp en
      Configuración (ahora `./configuraciones/vincular-whatsapp.sh`), el QR de
      `server.js` (`presto.local:3002` → `localhost:${PORT}`, host **y** puerto estaban
      mal) y la opción `vincular-whatsapp.sh presto 3001` de `install.sh`.
      Se conservan las de uso interno del desarrollador (`--presto` de `setup_session.py`
      y `smoke-test.sh --presto`), que no ve quien instala — **confirmar con Rodrigo**
- [x] Validado: `compose config -q`, `py_compile`, `node --check`, `bash -n` de todos los shells

### `feature_web_portales_21072026` (mejora) — ✅ COMPLETADA
- [x] Campo nuevo `requires_auth` en `GET /api/portals`, derivado de `session_key` (que no
      se expone). Sin él la UI no distinguía "sin sesión" de "no necesita sesión"
- [x] Ofertas: los checkboxes de Portal solo listan
      `p.active && (!p.requires_auth || p.session_active)`
- [x] Portales: aviso **rojo** con ícono cuando el portal exige sesión y no la tiene
      ("no buscará ofertas ni podrá postular hasta que la registres"), por delante del
      aviso ámbar de postulación manual
- [x] Portales: recuadro explicativo al abrir "Portales con auto-postulación" — por qué
      registrar la sesión y que queda solo en el equipo del usuario
- [x] Validado con `tsc --noEmit` (exit 0, sin errores) y `py_compile`

### `feature_web_avisos_fijos_21072026` (mejora) — ✅ COMPLETADA
- [x] Componente `components/Aviso.tsx` reutilizable (tipos ok/error/info, `role="status"`,
      botón de cierre con `aria-label`)
- [x] Eliminados los 3 `setTimeout` de Configuración: prueba de WhatsApp (5 s), prueba de
      correo (6 s) y "Guardado" (2 s). Ahora quedan fijos hasta cerrarlos a mano
- [x] Los avisos salieron del contenedor flex del botón: al pasar de texto en línea a
      bloque, dentro del flex quedaban apretados contra el botón
- [x] Validado con `tsc --noEmit` (exit 0)

### `feature_manual_github_pages_21072026` (mejora) — ✅ COMPLETADA
- [x] `obsidian/Creación de página github.md`. Responde la duda del nombre con datos
      verificados vía API el 21/07/2026: el subdominio lo determina el nombre de la
      **cuenta**, no el del repo. El usuario/org `buscapega` está **libre**, así que
      `buscapega.github.io` es posible pero exige crear una organización aparte;
      `rodrigomoya-dev.github.io/buscapega` no requiere nada nuevo (recomendada).
      Incluye ambos caminos paso a paso, `.nojekyll`, dominio propio con las IPs de
      Pages, tabla de problemas frecuentes y el recordatorio de `git push github main`

### `fix_daily_referencia_presto_21072026` (corrección) — ✅ COMPLETADA
Detectada al validar el merge a `main`: el rebranding automático había convertido
`http://wunen.presto` en `http://buscapega.presto`, o sea **seguía apuntando a Presto**
en el mensaje de notificación diaria que le llega al usuario.
- [x] `setup/buscapega-daily.sh` usa `FRONTEND_URL`, por defecto `http://localhost:3000`
      y sobrescribible por variable de entorno. Probadas ambas rutas de expansión

**Referencias a Presto que quedan a propósito** (no las ve quien instala; describen
herramientas internas que existen y funcionan — borrarlas dejaría la doc incorrecta):
`CLAUDE.md`, `.claude/commands/autentica.md` (flag `--presto` de `setup_session.py`),
`smoke-test.sh --presto` y un comentario histórico en `server.js:103`.
**Confirmar con Rodrigo si también deben irse.**

## Cierre de sesión
- [x] Push de las **7 ramas** a `github` — verificado por SHA, no solo por el exit del push
- [ ] Push a `origin` (gitea) — **BLOQUEADO**: Presto no responde. WOL enviado 2 veces
      (magic packet OK) y sondeado el ping sin respuesta. Reintentar todo con:
      `for b in fix_instalador_ux_21072026 feature_instalador_robot_estrella_21072026 \
       fix_rebranding_wunen_buscapega_21072026 feature_web_portales_21072026 \
       feature_web_avisos_fijos_21072026 feature_manual_github_pages_21072026 \
       fix_daily_referencia_presto_21072026 main fix_credenciales_expuestas_21072026; do \
       git push origin $b; done`
- [x] Merge a `main` sin `obsidian/` → `14bd9bf`, verificado: **0 archivos de obsidian**
      en el árbol de `main` y `.gitignore` público restaurado
- [x] `main` subido a github y verificado por SHA
- [x] Validaciones sobre `main`: `bash -n`, `compose config -q`, `node --check`,
      `tsc --noEmit` (exit 0) y `smoke-test --static` (2 OK · 0 fallidas)
- [x] Ejecutar `/prueba` — ver resultado abajo

## Resultado de `/prueba` (21/07/2026)

Clonado `main` fresco desde GitHub a `demo/buscapega` y verificado que es la última
versión (`14bd9bf`, idéntico al `main` recién subido). El clon público **no** contiene
`obsidian/`.

### Validado funcionando
| Qué | Resultado |
|---|---|
| Robot con estrella `✦` | ✅ se dibuja alineado |
| `fail()` rojo vs `warn()` amarillo | ✅ "Teléfono inválido" sale en rojo, claramente distinto |
| Detección de restos `wunen_*` | ✅ listó los 5 contenedores y 3 volúmenes; se respondió «n» y **se conservaron** |
| `nota()` naranja | ✅ destaca sobre el fondo |
| Puerto ocupado | ✅ "Lo ocupa: com.docke (PID 693)" + "Contenedor Docker: wunen_frontend" |
| Trap de salida | ✅ "Instalación NO completada", nunca salida silenciosa |
| **Reutilización de datos** | ✅ **el bug reportado está resuelto**: había `.install-config` sin `.install-state` (el caso exacto) y en la 2ª corrida reutilizó los datos en vez de repreguntar |
| Python + Playwright | ✅ `setup-sessions.sh --lista` creó el venv, instaló Playwright y Chromium; Chromium lanza (149.0.7827.55) |

> Nota sobre la validación de Python del comando: `python3 -c "import playwright"` **falla**
> con el Python del sistema, y es correcto que falle. El proyecto usa `setup/.venv` a
> propósito desde el fix de 26/06/2026. Lo que hay que validar es
> `./configuraciones/setup-sessions.sh`, que sí funciona.

### Problema encontrado y corregido — `fix_puerto_kill_docker_21072026`
Con el puerto ocupado por un contenedor, el instalador sugería `kill 693`. **Ese PID es
`com.docker.backend`, el proxy compartido de Docker Desktop**: se comprobó que el *mismo*
PID sirve los 5 puertos (3000, 8000, 8001, 3001, 5432), así que matarlo **tumbaría Docker
entero**, no el servicio.
- [x] Si se identifica el contenedor → solo `docker stop <cont>`
- [x] Si lo publica Docker pero no se identifica → `docker ps --filter publish=<puerto>`
- [x] Solo en procesos normales se sugiere `kill <pid>`
- [x] Al probarlo apareció un segundo detalle: `lsof` trunca COMMAND a 9 caracteres
      (`com.docke`), así que el patrón `com.docker*` nunca casaba. Corregido a `com.dock*`

### No ejecutado: build completo de Docker
El build no se corrió porque **tu instalación actual está en marcha** (5 contenedores
`wunen_*` con la BD, las cookies y la vinculación de WhatsApp) y **ocupa los 5 puertos**.
Completar la instalación exigía detenerla y arriesgar tus datos. Los Dockerfiles no se
tocaron en esta sesión y el build completo ya quedó validado en la ronda 2 del 20/07.

**Para probar el ciclo completo hay que decidir antes qué hacer con los datos actuales**
(ver el punto del rebranding: se optó por «empezar limpio»).

---

# Arrastre de la sesión anterior (21/07/2026 — seguridad)

Cerrado en `fix_credenciales_expuestas_21072026` (commits `d675b7d`, `4158cbb`),
documentado en [[tecnico/credenciales-git]]. Quedó pendiente:

- [ ] **Push de esa rama a `origin` (gitea)** — Presto no respondió al WOL. Reintentar:
      `git push origin fix_credenciales_expuestas_21072026`
- [ ] **Rotar el token de GitHub** (scope `repo`, quedó visible en salidas de terminal)
- [ ] **Rotar la contraseña de Gitea** del usuario `claude` — está en el historial
      público en el commit `772dd5a`
- [ ] Purga del historial: **decidido no ejecutarla por ahora**. Solo tiene sentido
      después de rotar, y aun así GitHub conserva los commits huérfanos accesibles por
      SHA hasta el garbage collection.
