#!/usr/bin/env bash
# deploy.sh — Export, validate, sync docs/, commit, and push
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[1/5] Exporting + validating..."
python tools/run_exports.py

echo "[2/5] Syncing docs/..."
cp physics_graph.json docs/
cp physics_note_details.json docs/
cp prototype/app.js docs/
cp prototype/index.html docs/
cp prototype/styles.css docs/
mkdir -p docs/materials-science-engineering
cp materials-science-engineering-kb/prototype/app.js docs/materials-science-engineering/
cp materials-science-engineering-kb/prototype/index.html docs/materials-science-engineering/
cp materials-science-engineering-kb/prototype/styles.css docs/materials-science-engineering/
cp materials-science-engineering-kb/prototype/graph.json docs/materials-science-engineering/
cp materials-science-engineering-kb/prototype/note_details.json docs/materials-science-engineering/
echo "  docs/ synced"

echo "[3/5] Staging changes..."
git add physics_graph.json physics_note_details.json docs/ README.md AI_HANDOFF.md

echo "[4/5] Committing..."
CHANGES=$(git diff --cached --stat)
if [ -z "$CHANGES" ]; then
  echo "  No changes to commit."
else
  git commit -m "deploy: export + sync docs

$(echo "$CHANGES" | head -5)"
fi

echo "[5/5] Pushing..."
git push

echo ""
echo "Done. GitHub Pages will update shortly."
