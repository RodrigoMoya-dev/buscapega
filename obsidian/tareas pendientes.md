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

# 2. Subir las 11 ramas de la sesión del 21/07/2026 + main
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
