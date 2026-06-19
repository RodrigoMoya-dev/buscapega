# Tareas pendientes

> Las tareas resueltas se eliminan de este archivo. El historial completo queda en los
> commits de git. Aquí solo vive lo que está **pendiente** o las notas vigentes.

---

## Sesión 18/06/2026 (b) — sacar comandos privados del GitHub público

Los archivos `.claude/commands/journal.md` y `.claude/commands/prueba.md` NO deben
aparecer en el GitHub público. `journal.md` además **contiene la contraseña de gitea
en texto plano** (riesgo de seguridad ya flagueado antes). `valida.md` y `autentica.md`
SÍ se quedan (son comandos públicos, los referencia el instalador).

- [ ] 1. Gitignorar `.claude/commands/journal.md` y `prueba.md` (privados, como `obsidian/`)
- [ ] 2. `git rm --cached` de ambos en la rama de trabajo (quedan locales, sin trackear)
- [ ] 3. Commit + push de la rama a gitea (`origin`) y github
- [ ] 4. Mergear a `main` (la eliminación + gitignore) y push a ambos remotos
- [ ] 5. Verificar que un `git ls-tree main` ya NO los liste
- [ ] 6. DECISIÓN del usuario: ¿purgar también del **historial** + force-push? (destructivo)
       y **rotar la contraseña de gitea** (quedó expuesta en commits previos).
- [ ] 7. `/test` final
