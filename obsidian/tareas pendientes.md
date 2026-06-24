# Tareas pendientes

> Las tareas resueltas se eliminan o se marcan aquí; el historial completo queda en git.

---

## Tema 1 — Archivos privados fuera del GitHub público ✅ LISTO
- [x] `.claude/commands/journal.md` y `prueba.md` en `.gitignore` y des-trackeados.
- [x] Purga total del historial (`git filter-repo`) — no quedan en versiones anteriores.
- [x] `valida.md` y `autentica.md` siguen versionados (son públicos).

---

## Tema 2 — Instalador 100% local (rama `fix_instalador_local_sin_presto_19062026`)
- [x] **Quitar la sincronización a Presto del instalador.** `setup_session.py` ahora
      copia las cookies al contenedor local `wunen_scraper` (`docker cp`,
      `sincronizar_local`). El `rsync` a Presto quedó como opción interna `--presto`.
- [x] Corregir mensajes: ya no dice "La sesión está lista en Presto".
- [x] Prompt de WhatsApp en `install.sh` ahora aclara que solo guarda el número y que
      la vinculación se hace después con `./whatsapp-qr.sh` (QR).
- [x] Documentación actualizada en `obsidian/tecnico/instalador.md`.
- [x] Subido a gitea + github (rama) y mergeado a `main` (sin `obsidian/`), `main` pusheado a ambos.
- [x] Validación: `./smoke-test.sh --static` → 2 OK, 0 fallidas. La fase dinámica no aplica
      (no hay servicios locales arriba) y mis cambios son a scripts de instalación/setup,
      no a los servicios en runtime. `setup_session.py` compila (`py_compile`).

---

## Tema 3 — Instalador detecta Docker/puertos corriendo ✅ (rama `feature_instalador_detecta_docker_19062026`)
- [x] **Daemon de Docker:** se verifica con `docker info` (antes solo `command -v docker`).
      Si Docker Desktop está apagado, aborta con mensaje claro en vez de fallar en `compose build`.
- [x] **Instalación previa de Wunen:** detecta contenedores `wunen_*` y avisa que es
      reinstalación (datos en volúmenes se conservan).
- [x] **`check_port` sin falsos positivos:** los puertos ocupados por contenedores de Wunen
      corriendo se reportan como "se recreará", no como conflicto. Procesos ajenos siguen alertando.
- [x] Documentación en `obsidian/tecnico/instalador.md`.
- [x] Subido a gitea + github (rama) y mergeado a `main` (sin `obsidian/`), `main` pusheado a ambos.
- [x] Validación: `./smoke-test.sh --static` → 2 OK, 0 fallidas. `install.sh` pasa `bash -n`.

---

## Tema 4 — Backend caído en reinstalación por volumen Postgres huérfano (detectado por `/prueba`)

> **Prompt para resolver.** El comando `/prueba` clonó la última versión de GitHub
> (`ddae72c`) en `demo/` y ejecutó `install.sh`. El instalador terminó con código 0 y
> mostró "Instalación completada" en verde, **pero el backend quedó caído**: el contenedor
> `wunen_backend` figura *Up* mientras hace crash-loop con
> `psycopg2.OperationalError: ... password authentication failed for user "wunen"`.
> Frontend (`:3000`) y scraper (`:8001`) responden 200; el backend `:8000/health` da
> HTTP 000. Es un **falso positivo del instalador**: reporta éxito con el backend muerto.

**Causa raíz y hallazgos:**
- [x] **Volumen Postgres huérfano.** Existe el volumen `wunen_db_data` de una instalación
      anterior (inicializado con OTRA contraseña). En un clon nuevo no hay `docker/.env`, así
      que `install.sh` genera un `POSTGRES_PASSWORD` aleatorio nuevo, pero `compose up`
      reutiliza el volumen viejo → la contraseña no coincide y el backend no autentica.
- [x] **La detección de instalación previa (Tema 3) sólo mira contenedores, no volúmenes.**
      Si se borró el clon o se hizo `docker compose down` (sin `-v`), los contenedores
      `wunen_*` desaparecen pero el volumen `wunen_db_data` sobrevive. Una "reinstalación
      limpia" entonces rompe el backend sin aviso.
- [x] **La remediación de password del propio instalador no se dispara.** El `elif` de
      `install.sh` (~líneas 406-412) que detecta "password authentication failed" en los logs
      y sugiere `down -v && up -d` no se ejecutó: la espera de 60 s expiró con el warning
      genérico "El backend tardó más de lo esperado" (el `grep` corrió antes de que el error
      apareciera en los logs / el backend seguía reintentando).
- [x] **Menor — generación de contraseña concatena aleatorio + fallback.** En la línea ~253,
      `tr -dc ... < /dev/urandom | head -c 24 ... || echo "wunen_$(date +%s)"` produce
      `...vQu2w1anwwunen_1782316762`: `head` cierra el pipe a los 24 bytes, `tr` recibe SIGPIPE
      (exit 141) y dispara el `||`, concatenando ambas cadenas. No rompe la auth (es
      consistente), pero el fallback se añade siempre por error.

**Qué se debe solucionar:**
- [x] Detectar el volumen `wunen_db_data` huérfano cuando NO existe `docker/.env` (instalación
      "nueva" sobre datos viejos): avisar al usuario y ofrecer resetear (`compose down -v`) o
      conservar datos. Sin el `.env` la contraseña del volumen es desconocida → o se resetea o
      se pide al usuario. → Bloque `DB_VOLUME_HUERFANO` en sección 5 (usa `ENV_PREEXISTING`).
- [x] Hacer robusta la verificación de readiness del backend: tras el timeout, revisar
      activamente los logs por el error de password y mostrar la remediación documentada
      (`down -v && up -d`) en vez del warning genérico. → Sección 7 con `BACKEND_OK` + `elif/else`.
- [x] **No mostrar el banner "Instalación completada" en verde si el backend nunca respondió
      `/health`.** Mostrar un estado claro de "backend no disponible" para evitar el falso
      positivo. → Banner condicionado a `${BACKEND_OK}` (verde vs. amarillo "incompleta").
- [x] Corregir la generación de `POSTGRES_PASSWORD` (línea ~253) para que el fallback sólo
      actúe ante un fallo real (capturar en variable y `[[ -z ]] && fallback`), evitando la
      concatenación por SIGPIPE. → `... | head -c 24 || true` + `[[ -z ]] && fallback`.

**Validación (clon `demo/` con volumen huérfano reproducido):**
- [x] `bash -n install.sh` OK.
- [x] Reinstalación detecta `wunen_db_data` huérfano, ofrece reset, lo elimina y recrea limpio.
- [x] Backend `/health` → HTTP 200 `{"status":"ok"}`; frontend 200; scraper 200; db healthy.
- [x] Banner final muestra "Instalación completada" (verde) al estar el backend sano.
- [x] `./smoke-test.sh` (servicios en vivo) → 6 OK, 0 fallidas.

**Entrega:**
- [x] Rama `fix_installer_volumen_postgres_24062026` subida a gitea (`origin`) y github.
- [x] Mergeada a `main` (merge real de 2 padres, **sin `obsidian/`**) y `main` pusheado a ambos remotos (`f6d6fec`).

**Evidencia (entorno de la prueba):**
- Clon validado: `ddae72c` (= HEAD remoto de GitHub).
- `docker volume ls`: `wunen_db_data`, `wunen_playwright_cookies`, `wunen_whatsapp_auth` (preexistentes).
- `.env` generado: `POSTGRES_PASSWORD=MrmbUV1iA2Neme_vQu2w1anwwunen_1782316762`.
- `curl :8000/health` → HTTP 000; `:3000` → 200; `:8001/docs` → 200.
- Log del backend: `password authentication failed for user "wunen"` (db 172.19.0.3:5432).
