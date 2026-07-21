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
- [ ] Push a `github` y merge a `main`
- [ ] Push a `origin` (gitea) — **omitido**: Rodrigo no está en la red de Presto.
      Prompt listo más abajo
