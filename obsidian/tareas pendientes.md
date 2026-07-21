
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

---

# Seguridad — credenciales expuestas (21/07/2026)

Detectado al validar la sincronía local ↔ GitHub.

**Hallazgos confirmados:**

1. El repo `RodrigoMoya-dev/buscapega` es **público** (`private: false`, 0 forks).
2. La contraseña de Gitea `Temporal2026!` está en el **historial público**: commit
   `772dd5a`, archivo `obsidian/tareas pendientes.md:34`, ancestro de `github/main`.
   Hoy `main` excluye `obsidian/`, pero el commit histórico sigue siendo accesible.
   Mitigante: `gitea.presto` es un host de red local, no alcanzable desde internet.
3. El **token de GitHub** `ghp_…` (scope `repo`, control total) estaba en texto plano
   en la URL del remoto en `.git/config`. **No** está en el historial ni en archivos
   versionados — solo en config local, que no se sube.
4. Las URLs de los 3 remotos (`github`, `origin`, `gitea_old`) llevaban credenciales
   incrustadas, visibles en cada `git remote -v`, en logs y en capturas de pantalla.

## Rama `fix_credenciales_expuestas_21072026`
- [x] Guardar credenciales en el keychain de macOS (`credential.helper=osxkeychain`)
- [x] Limpiar las credenciales de las URLs de los 3 remotos
- [x] Verificar que `fetch`/`push` siguen funcionando sin credenciales en la URL —
      `git fetch --dry-run` OK contra `github` y `origin` sin pedir contraseña
- [x] Configurar upstream en las 6 ramas que no lo tenían (antes coincidían por SHA
      pero `git status` no avisaba de desincronización)
- [x] Documentar el hallazgo y la política en `obsidian/tecnico/credenciales-git.md`

## Cierre de la rama
- [x] Commit `d675b7d` + push a **github**
- [ ] Push a **origin** (gitea) — **BLOQUEADO**: Presto no responde. Se envió WOL con
      `wake_presto.sh` (magic packet enviado) y se sondeó el ping durante ~2 min sin
      respuesta. Puede estar apagado a nivel físico o con WoL deshabilitado en BIOS.
      Reintentar con: `git push origin fix_credenciales_expuestas_21072026`
- [~] Merge a `main` — **no aplica**. El fix real fue sobre `.git/config`, que **no se
      versiona**; los únicos archivos del commit son documentación en `obsidian/`, que
      `main` excluye por diseño. Mergear produciría un commit vacío. Nada que llevar a `main`.

## Acciones que solo puede hacer Rodrigo (no automatizables)
- [ ] **Rotar el token de GitHub** en https://github.com/settings/tokens (quedó visible
      en salidas de terminal; se considera quemado)
- [ ] **Rotar la contraseña de Gitea** del usuario `claude` (está en el historial público)

## Purga del historial — pendiente de decisión
- [ ] Reescribir `main` con `git-filter-repo` y force-push a ambos remotos.
      **Salvedad:** GitHub conserva los commits huérfanos accesibles por SHA directo
      hasta hacer garbage collection; para borrado real hay que abrir ticket a GitHub
      Support. Riesgo bajo de romper terceros (0 forks).

