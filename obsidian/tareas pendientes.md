Las siguientes tareas tienen que ver con la interfaz de la página de github: En el proyecto está en la carpeta /docs. 


1. ¿Puedes cambiarle los estilos de color y usar la paleta entregada? 
2. Lo mismo ocurre con el bot que aparece ¿Puedes usar el bot entregado? 
	1. Ambos (Estilo e imagen del bot) están en /Users/rodrigo/Proyectos/Moya.dev/Proyectos internos/buscapega/grafica. 
	2. ¿Puedes darle un efecto de movimineto al bot, así como si flotara en el aire? 
3. El texto de "Buscar la oferta, leerla.." utiliza todo el ancho de la página. Adjunto evidencia. 
4. ![[Pasted image 20260721221246.png]]


	En los pasos, también usar el ancho de la página para el título. Además, los textos debieran ser los siguientes (Adjunto evidencia): 
	![[Pasted image 20260721221405.png]]


A continuación van los textos de las páginas. 

 * PASO 01
####  Recolecta

Recorre los portales activos de forma autónoma y trae las ofertas nuevas.

* PASO 02
#### Filtra 

Evalua cada oferta con tu perfil y revisa sólo las que se adaptan. 

* PASO 03 
#### Autopostula

Si el portal reportado lo permite, genera automáticamente la postulación, enviando correo con los datos. 

* PASO 04
#### Postula manualmente 

* Si no es posible autopostular, igual te llegará el aviso a whatsapp indicando porqué no se pudo postular. 


* Una vez terminado, revisa todos los temas pendientes aquí abajo, y todo lo que está listo anda tachandolo. 

---- 
### Instalador 

* Al momento de anotar el correo, lo quise evitar pero no me deja. Entonces ¿Es obligatorio u opcional? 
  
  ![[Pasted image 20260721162238.png]]
* Los contenedores siguen apareciendo con el prefijo wunen_ pero debieran aparecer con el prefijo buscapega_ 

![[Pasted image 20260721162311.png]]

* ¿Se hicieron los cambios en el github? Porque sigo viendo la misma interfaz en la web. 


---

# PLAN DE TRABAJO — sesión 21/07/2026 (ronda 2)

## Diagnóstico de las 3 consultas

### 1. El correo: es OPCIONAL, pero la UX lo vuelve inescapable — **es un bug**
En el código el correo **nunca fue obligatorio**, pero dejarlo vacío abre una segunda
pregunta `¿Continuar sin correo? (s/N)` cuya **única** salida es escribir `s`. En la
evidencia se ve el bucle: Enter → repregunta; `n` → repregunta; `N` → repregunta; y al
escribir `n` como si fuera el correo → "Correo inválido".

El problema es la doble negación: "¿Continuar **sin** correo?" se lee como "¿te lo
saltas?", y quien quiere omitirlo responde `n` o Enter, que es justo lo que lo devuelve
al principio. Además contradice el estilo del resto de campos opcionales del instalador
(API key, contraseña de Gmail), que dicen `[OPCIONAL — Enter para omitir]`.

### 2. Los contenedores `wunen_`: no es un bug, es una copia vieja
Los contenedores en marcha se crearon a las **20:20 de hoy** desde
`/Users/rodrigo/Desktop/buscapega-main` — una **descarga ZIP del 20/07**, anterior a
todos los cambios de hoy. Verificado con las etiquetas de compose del contenedor:

```
com.docker.compose.project          = wunen
com.docker.compose.project.config_files = /Users/rodrigo/Desktop/buscapega-main/docker/docker-compose.yml
```

Esa carpeta **no** tiene `fail()`, ni la estrella del robot, ni `requires_auth`, ni
`Aviso.tsx`, y su compose declara `name: wunen`. El repositorio y la carpeta de trabajo
sí tienen el rebranding (`name: buscapega`).

### 3. "Sigo viendo la misma interfaz": misma causa
Los cambios **sí están en GitHub** (`main` = `fd2ed36`, verificado por SHA contra el
remoto). Lo que se está viendo es el frontend construido desde la descarga del 20/07.

## Ramas

### `fix_correo_opcional_21072026` (corrección) — ✅ COMPLETADA
- [x] El correo se omite con **Enter**, como la API key y la contraseña de Gmail. Se
      elimina la pregunta `¿Continuar sin correo? (s/N)` de doble negación
- [x] La etiqueta dice `[OPCIONAL — Enter para omitir]` y el mensaje de error añade
      "o pulsa Enter para omitirlo", para que la salida sea evidente
- [x] Probados los 3 caminos: Enter (el que dejaba atrapado) → omite; correo válido →
      lo toma; inválido y luego Enter → avisa y omite

### Sin cambio de código — instrucciones para Rodrigo
La descarga de `~/Desktop/buscapega-main` corresponde exactamente al commit **`c2f2606`
(20/07 23:04)**, el `main` de anoche — verificado comparando su `install.sh` contra cada
commit. Le faltan **11 commits**, incluido todo el rebranding. Por eso ve `wunen_` y la
interfaz anterior: el ZIP se bajó de GitHub **antes** de que se subieran los cambios de hoy.

- [ ] Volver a descargar y reconstruir:

```bash
# 1. Detener y borrar la instalación vieja (libera los puertos)
cd ~/Desktop/buscapega-main/docker && docker compose down

# 2. Descargar la versión actual (o simplemente bajar el ZIP otra vez desde GitHub)
cd ~/Desktop && rm -rf buscapega-main
git clone https://github.com/RodrigoMoya-dev/buscapega.git buscapega-main

# 3. Instalar — ofrecerá eliminar los restos «wunen_»
cd buscapega-main && bash install.sh
```

> Al reconstruir, el frontend se compila de nuevo y ahí aparecen los cambios de la web
> (avisos fijos, portales filtrados, aviso de sesión de Google).

## Cierre
- [x] Push a `github` y merge a `main` → `95e2a46` (0 archivos de obsidian en `main`)
- [x] `/prueba`: clonado `main` fresco desde GitHub y verificado que un solo **Enter**
      omite el correo y avanza a los puertos. El bucle desapareció
- [ ] Push a `origin` (gitea) — **omitido a propósito**: Rodrigo no está en la red de
      Presto, el servidor es inalcanzable. Ver el prompt listo abajo

---

# 📌 PENDIENTE: subir todo a Gitea cuando Presto esté en línea

Nada de esto está en Gitea todavía; **todo está en GitHub**. Al volver a la red de Presto,
ejecutar desde la raíz del proyecto:

```bash
# 1. Comprobar que Presto responde (si no, despertarlo)
nc -z -w3 192.168.100.6 80 || /Users/rodrigo/Proyectos/Moya.dev/sh/wake_presto.sh

# 2. Subir las 12 ramas de la sesión del 21/07/2026 + main
for b in \
  fix_credenciales_expuestas_21072026 \
  fix_instalador_ux_21072026 \
  feature_instalador_robot_estrella_21072026 \
  fix_rebranding_wunen_buscapega_21072026 \
  feature_web_portales_21072026 \
  feature_web_avisos_fijos_21072026 \
  feature_manual_github_pages_21072026 \
  fix_daily_referencia_presto_21072026 \
  fix_puerto_kill_docker_21072026 \
  fix_correo_opcional_21072026 \
  main
do
  echo "→ $b"; git push origin "$b" || echo "  ✗ fallo en $b"
done

# 3. Verificar que quedaron iguales
git fetch origin
for b in main fix_correo_opcional_21072026; do
  [ "$(git rev-parse $b)" = "$(git rev-parse origin/$b)" ] && echo "✓ $b" || echo "✗ $b"
done
```

> La credencial de Gitea ya está en el keychain de macOS, así que el push **no** debería
> pedir contraseña. Si la pide, es que aún no se ha rotado/actualizado — ver
> [[tecnico/credenciales-git]].

---

# Página de GitHub Pages — `feature_pagina_github_pages_21072026`

Pedido: armar la página en `/docs` usando como base el estilo de
`project-copacetic.github.io/copacetic/website/`.

## Qué se tomó de la referencia
Se extrajo el CSS real de la página (es Docusaurus) en vez de imitarla de memoria:
hero centrado en columna con `gap: 1.5rem`, **título en `font-weight: 300`** (el rasgo
más característico), grid de tarjetas `repeat(auto-fit, minmax(…, 1fr))` y tarjetas con
gradiente sutil, borde de 1px y radio de 12px.

## Qué es propio de Buscapega
- **El robot ASCII del instalador es el protagonista del hero**, donde Copacetic pone su
  logo. Es lo único que nadie más puede tener, y quien ya vio la terminal reconoce la
  página al instante. Lleva la bandera chilena real (cantón azul con estrella, blanco, rojo)
- Paleta de `grafica/palette.scss` + el rojo y azul de la bandera
- La monoespaciada como voz de marca (marca, eyebrows, código): no es adorno, el producto
  se instala y se usa desde la consola
- Contenido real: los 12 portales con su marca de auto-postulación, el flujo de 4 pasos y
  los 3 comandos de instalación

## Decisiones tomadas al revisarla en el navegador
| Problema visto | Corrección |
|---|---|
| 5 tarjetas en 4 columnas dejaban una huérfana | 6ª capacidad real (agregar portales validando el sitio) + `minmax(300px)` → 3+3 |
| Los `h2` heredaban `line-height: 1.6` y quedaban muy separados | `line-height: 1.2` |
| **En modo claro la franja blanca de la bandera y los ojos desaparecían** | El robot va sobre una placa de fondo oscuro **fija en ambos temas**; se lee igual siempre y refuerza la identidad de terminal |

Numerar los pasos del flujo (PASO 01…04) se mantuvo porque **es una secuencia real** del
proceso, no un adorno.

## Comprobado
- [x] Escritorio 1200px, móvil 390px, modo oscuro y modo claro (con una copia de prueba
      con la paleta clara forzada, luego eliminada)
- [x] Etiquetas balanceadas, 20.8 KB, **0 recursos externos** — carga sin depender de nadie
- [x] `prefers-reduced-motion` respetado, `:focus-visible` visible, `aria-label` en el robot

## Falta activar Pages (solo Rodrigo puede)
1. https://github.com/RodrigoMoya-dev/buscapega/settings/pages
2. Source: `Deploy from a branch` · Branch: `main` · carpeta `/docs` · Save
3. En 1-3 minutos queda en `https://rodrigomoya-dev.github.io/buscapega/`

Ver [[Creación de página github]].

---

# PLAN DE TRABAJO — sesión 21/07/2026 (ronda 3): gráfica de la página

Rama: `feature_pagina_github_pages_21072026` (se continúa la misma, es la misma página).

## Tareas
- [ ] **1. Paleta entregada** — aplicar `grafica/palette.scss` de verdad (hoy el fondo es
      un gris-verdoso neutro que no sale de ahí). Bordeaux como base oscura, blush como
      texto, naranja y pino como acentos, celadon en los iconos. Modo claro con el blush
      aclarado y el bordeaux como tinta
- [ ] **2. El bot entregado** — reemplazar el robot ASCII del hero por
      `grafica/logobuscapega.jpg`. El archivo trae el damero de "transparencia" pintado
      encima (es JPG), hay que recortarlo a PNG con alfa real
- [ ] **3. Flotación del bot** — animarlo como si flotara, con sombra que acompaña.
      Respetando `prefers-reduced-motion`
- [ ] **4. Ancho completo en los encabezados** — hoy `.section-head` está limitado a
      `60ch` y el título/bajada quedan en media página mientras las tarjetas van a todo
      el ancho. Se quita el tope
- [ ] **5. Textos nuevos del flujo** — PASO 01 Recolecta / 02 Filtra / 03 Autopostula /
      04 Postula manualmente, con los textos entregados
- [ ] **6. Revisar en el navegador** (escritorio y móvil, oscuro y claro)
- [ ] **7. Documentar en obsidian y subir a GitHub + merge a main**
- [ ] **8. Gitea** — solo si Presto responde
