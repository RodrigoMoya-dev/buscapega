
# Instalador 

* Terminé de instalar y me indicó que había conflictos con un puerto en docker. Me daba opciones, y luego me preguntó si continuaba o no. Le puse "S" pero no me indicó nada y salió a la línea de comandos. 
  
  ¿Cómo se yo si el proceso fue o no exitoso? 

* ¿Puedes además, al final de la instalación, colocar la ruta de localhost a la que se debe entrar para ver el administrador? 

* Intenté entrar poa localhost:3000 no aparece nada. Al revisar los contenedores, tampoco veo los contenedores de buscapega funcionando. 

## Checklist ronda 3 (20/07/2026 — salida silenciosa del instalador)

> **Causa raíz encontrada (un solo bug explica los 3 síntomas):** la función `check_port`
> termina con el idiom `[[ cond ]] && error`. Al escribir "S" (continuar), el `[[ ]]` es
> falso → la función **retorna 1** → bajo `set -e` el llamador `check_port ...` mata el
> script en silencio, ANTES de `docker compose up -d` y del resumen. Por eso salió sin
> avisar, no se supo si fue exitoso, y no quedaron contenedores ni web en localhost:3000.
> Reproducido en un test mínimo.

### Rama `fix_install_salida_silenciosa_20072026`
- [x] `check_port` debe retornar 0 al continuar (arreglar el `[[ ]] && error` final).
- [x] `trap ... EXIT`: si el instalador se detiene antes de terminar, imprimir un mensaje
      claro de "NO completada" (nunca más salir en silencio). Responde "¿cómo sé si fue
      exitoso?".

### Rama `feature_install_url_admin_20072026`
- [x] Mostrar de forma destacada al final la URL del administrador
      (`http://localhost:<puerto>`) para entrar a la web. Recuadro "👉 Abre el
      administrador en…" tras "Instalación completada", y también en el caso
      "backend caído" (URL cuando responda).

### Cierre ronda 3
- [x] Push de ambas ramas a `origin` (gitea) y `github`
- [x] Merge a `main` sin `obsidian/`
- [x] Re-ejecutar `/prueba` — **VALIDADO**: se clonó `main` fresco desde GitHub, el
      puerto 3001 estaba ocupado (conflicto real), se respondió "S" y el instalador
      **continuó al build** (`! Continuando con el puerto 3001 en uso` → `[2/5]
      Construyendo backend`) en vez de morir en silencio. Se abortó antes del build
      pesado del scraper para no repetir el incidente de memoria. El build completo ya
      quedó validado en la ronda 2 (Dockerfiles sin cambios).

