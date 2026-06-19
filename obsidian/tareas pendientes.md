# Tareas pendientes

> Las tareas resueltas se eliminan de este archivo. El historial completo queda en los
> commits de git. Aquí solo vive lo que está **pendiente** o las notas vigentes.

---

## Sesión 18/06/2026 (b) — sacar comandos privados del GitHub público ✅

Los archivos `.claude/commands/journal.md` y `.claude/commands/prueba.md` no debían
aparecer en el GitHub público (`journal.md` filtra la contraseña de gitea). `valida.md`
y `autentica.md` se mantienen (comandos públicos referenciados por el instalador).

- [x] 1-5. Gitignorar + `git rm --cached` ambos, commit en rama `fix_ocultar_comandos_privados_18062026`, push a gitea+github, merge a `main`.
- [x] 6. **Purga total del historial** (decisión del usuario): `git filter-repo --invert-paths`
      eliminó ambos archivos de los 61 commits. Force-push de `main` limpio a github y de
      todas las ramas reescritas a gitea. **github quedó solo con `main`** (sin obsidian ni
      comandos privados); las 5 ramas feature/fix se borraron de github. Verificado:
      `git log --all -- journal.md prueba.md` vacío.
- [x] Contraseña de gitea: el usuario indicó que **no es necesario** rotarla.
- [x] 7. `/test` final.

### ⚠️ Aprendizaje importante sobre `git filter-repo`
`filter-repo` **resetea el working tree al HEAD reescrito y borra del disco** los archivos
purgados Y los archivos no trackeados en la rama actual (estábamos en `main`, que ignora
`obsidian/`). Se perdieron del disco: `journal.md`, `prueba.md` y casi todo `obsidian/`.

**Recuperación aplicada:**
- `journal.md` / `prueba.md` → copiados desde el clon `demo/` (estaba en `d3d72cd`, antes del borrado).
- `obsidian/` → `git archive fix_ocultar_comandos_privados_18062026 obsidian/ | tar -x` (las ramas feature sí trackean obsidian).

**Para la próxima:** antes de correr `filter-repo`, hacer backup del working tree o
correrlo sobre un clon espejo aparte, no sobre el repo de trabajo principal.

---

## Resultado del `/prueba` (18/06/2026) — bug encontrado y corregido

Se clonó `github/main` y se corrió `install.sh`. El `smoke-test.sh` detectó que el backend
no levantaba: `password authentication failed`. Causa: `install.sh` regeneraba el
`POSTGRES_PASSWORD` en cada corrida pero el volumen conserva la contraseña original.
Fix (rama `fix_install_db_password_18062026`): reutiliza la contraseña del `.env` existente
y, si falla la auth, imprime la remediación (`down -v && up -d`). Validado: smoke-test 6/6.

---

## Cómo validar que nada se rompió después de un cambio

Script **`smoke-test.sh`** en la raíz. Dos fases:

| Fase | Qué valida | ¿Servicios levantados? |
|------|-----------|------------------------|
| **Estática** | `bash -n`, `shellcheck` (si está), `docker-compose.yml`, JSON de settings | No |
| **Dinámica** | `backend /health`, `scraper /health`, `frontend /`, `user_name` en `/api/settings` | Sí |

```bash
./smoke-test.sh            # local (3000/8000/8001)
./smoke-test.sh --presto   # presto (3020/8020/8021)
./smoke-test.sh --static   # solo fase estática
```

Devuelve exit 0/1. Ver `obsidian/tecnico/validacion.md` para detalle y tecnologías
recomendadas (bash+curl, shellcheck, y a futuro pytest/Playwright).
