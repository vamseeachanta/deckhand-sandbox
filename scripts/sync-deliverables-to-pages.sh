#!/usr/bin/env bash
# Sync the domains/ deliverable tree from main onto the gh-pages branch so the
# canonical GitHub Pages URLs that sandbox_publication advertises actually
# resolve, while preserving the curated landing index.html. (deckhand#463)
#
# Pages serves gh-pages (a curated index.html + review dirs); deliverables are
# committed to main under domains/. Without this overlay the advertised
# pages_url 404s for every deliverable.
#
# Run by .github/workflows/deploy-pages.yml on push to main; APPLY=1 pushes.
# Locally: `APPLY=0 bash scripts/sync-deliverables-to-pages.sh` is a safe dry-run.
set -euo pipefail

REMOTE="${REMOTE:-origin}"
APPLY="${APPLY:-0}"

root="$(git rev-parse --show-toplevel)"
if [ ! -d "$root/domains" ]; then
  echo "no domains/ tree at $root; nothing to deploy"
  exit 0
fi

git fetch "$REMOTE" gh-pages --quiet
work="$(mktemp -d)"
git worktree add -q --detach "$work" "$REMOTE/gh-pages"
trap 'git worktree remove --force "$work" 2>/dev/null || true' EXIT

# Overlay deliverables. --delete is scoped to domains/ so removed deliverables
# propagate, but the curated index.html / review dirs / .nojekyll on gh-pages
# are never touched.
mkdir -p "$work/domains"
rsync -a --delete "$root/domains/" "$work/domains/"
[ -f "$work/.nojekyll" ] || touch "$work/.nojekyll"

cd "$work"
git add -A domains .nojekyll
if git diff --cached --quiet; then
  echo "gh-pages already up to date"
  exit 0
fi

git -c user.name="deckhand-sandbox deploy" \
    -c user.email="deploy@users.noreply.github.com" \
    commit -q -m "deploy: sync domains/ deliverables to gh-pages (deckhand#463)"

if [ "$APPLY" = "1" ]; then
  git push "$REMOTE" HEAD:gh-pages
  echo "pushed deliverables to gh-pages"
else
  echo "dry-run (set APPLY=1 to push). Staged for gh-pages:"
  git show --stat HEAD | tail -n +2
fi
