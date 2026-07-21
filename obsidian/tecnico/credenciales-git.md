# Credenciales de Git (política y auditoría 21/07/2026)

Cómo se autentican los remotos del proyecto y qué **no** debe volver a ocurrir.

## Regla base

**Nunca incrustar credenciales en la URL de un remoto.** Una URL del tipo
`https://<token>@github.com/...` o `http://usuario:clave@gitea.presto/...` queda
en texto plano en `.git/config` y se imprime en cada `git remote -v`, en logs de
CI, en capturas de pantalla y en cualquier transcripción de terminal.

Las credenciales viven en el **keychain de macOS**:

```bash
git config --global credential.helper osxkeychain
```

Para cargar o actualizar una credencial sin que quede en el historial del shell:

```bash
git credential approve <<'EOF'
protocol=https
host=github.com
username=RodrigoMoya-dev
password=<token>
EOF
```

Para Gitea es igual, con `protocol=http` y `host=gitea.presto`.

## Estado actual de los remotos

| Remoto | URL | Auth |
|---|---|---|
| `github` | `https://github.com/RodrigoMoya-dev/buscapega.git` | keychain |
| `origin` | `http://gitea.presto/moya.dev/buscapega.git` | keychain |
| `gitea_old` | `http://gitea.presto/claude/buscapega.git` | keychain (repo antiguo) |

## Auditoría del 21/07/2026

Detectado al validar la sincronía entre la copia local y GitHub.

### Hallazgos

1. **El repositorio de GitHub es público** (`private: false`, 0 forks). Todo lo que
   entre a `main` es visible para cualquiera.
2. **Contraseña de Gitea en el historial público.** La cadena `Temporal2026!` aparece
   en el commit `772dd5a`, archivo `obsidian/tareas pendientes.md:34`, dentro de un
   comando `git push` de ejemplo. Ese commit es ancestro de `github/main`.
   - Hoy `main` excluye `obsidian/` vía `.gitignore`, pero **eso no borra el commit
     histórico**: sigue siendo accesible.
   - *Mitigante:* `gitea.presto` es un host de red local, no alcanzable desde internet.
     El impacto real es bajo, pero la credencial se considera quemada igual.
3. **Token de GitHub en la URL del remoto.** PAT con scope `repo` (control total sobre
   los repositorios de la cuenta) en texto plano en `.git/config`. **No** llegó al
   historial ni a archivos versionados — solo a la config local, que no se sube.

### Corregido en `fix_credenciales_expuestas_21072026`

- Credenciales movidas al keychain; URLs de los tres remotos limpiadas.
- Upstream configurado en las ramas que no lo tenían: antes coincidían con GitHub por
  SHA, pero `git status` no avisaba de una desincronización.

### Lecciones

- **Al documentar un comando, nunca pegar la credencial real.** Escribir
  `git push http://claude:<clave>@gitea.presto/...` con el placeholder.
- Una credencial que llegó a un repositorio público se rota; no se "despublica".
  Reescribir el historial reduce la exposición, pero GitHub conserva los commits
  huérfanos accesibles por SHA directo hasta hacer garbage collection — para un
  borrado real hay que abrir ticket a GitHub Support.
- `main` es pública. Antes de mergear, verificar que no entre nada privado además de
  `obsidian/`.

## Verificar que todo sigue funcionando

```bash
git remote -v                                  # ninguna URL debe llevar credenciales
GIT_TERMINAL_PROMPT=0 git fetch github --dry-run   # debe pasar sin pedir contraseña
GIT_TERMINAL_PROMPT=0 git fetch origin --dry-run
```

Si `origin` falla, puede ser que Presto esté apagado:
`/Users/rodrigo/Proyectos/Moya.dev/sh/wake_presto.sh`

Ver también [[instalador]] y [[validacion]].
