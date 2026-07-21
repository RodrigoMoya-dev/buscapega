
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

### `fix_rebranding_wunen_buscapega_21072026` (corrección)
- [ ] `wunen` → `buscapega` en los 22 archivos (contenedores, red, mount, rutas)
- [ ] Quitar **todas** las referencias a Presto en la web (texto de "Configurar WhatsApp
      (Baileys)" y donde aparezcan) — el proyecto corre local
- [ ] Migración de volúmenes según lo que se decida arriba

### `feature_web_portales_21072026` (mejora)
- [ ] Ofertas: mostrar solo portales autenticados o que no requieran autenticación
- [ ] Portales: aviso destacado cuando la sesión con Google no está iniciada
- [ ] Portales: explicación bajo "Portales con autopostulación" (por qué registrar la
      sesión: permite buscar y autopostular según los criterios)

### `feature_web_avisos_fijos_21072026` (mejora)
- [ ] Los avisos (ej. el de mensaje de prueba de WhatsApp) quedan fijos y con botón de cierre

### `feature_manual_github_pages_21072026` (mejora)
- [ ] `Creación de página github.md` — manual para publicar `buscapega` en GitHub Pages
      (incluye la diferencia entre `usuario.github.io` y `usuario.github.io/buscapega`)

## Cierre de sesión
- [ ] Push de cada rama a `github` **y** a `origin` (gitea)
- [ ] Merge a `main` sin `obsidian/`
- [ ] Ejecutar `/prueba`

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
