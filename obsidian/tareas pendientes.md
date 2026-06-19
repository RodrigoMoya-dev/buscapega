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
- [ ] Subir a gitea + github, mergear a `main` (sin `obsidian/`), `/test`.
