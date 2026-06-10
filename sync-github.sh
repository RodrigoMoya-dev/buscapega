#!/bin/bash
# Sincroniza main → rama public → GitHub (excluye obsidian/)
set -e

CURRENT=$(git branch --show-current)

echo "Sincronizando GitHub..."

git checkout public
git merge main --no-edit
git rm --cached -r obsidian/ 2>/dev/null || true
git commit --amend --no-edit
git push github public:main

git checkout "$CURRENT"
echo "GitHub sincronizado con exito."
