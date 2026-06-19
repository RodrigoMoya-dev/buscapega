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
- [ ] Subir a gitea + github, mergear a `main` (sin `obsidian/`).
- [ ] `/test`.

---

## Tema 3 — ¿El instalador detecta puertos/Docker corriendo? (PENDIENTE de revisar)
- `install.sh` ya tiene `check_port` (líneas ~295-317) que valida frontend/backend/
  scraper/whatsapp y ofrece detener o cambiar puerto. Falta revisar si conviene además
  detectar una instalación previa de Wunen ya corriendo. **No abordado en esta sesión.**
