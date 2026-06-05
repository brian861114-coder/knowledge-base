#!/usr/bin/env bash
# Deploy the knowledge base frontend to GitHub Pages.
#
# Prerequisites:
#   1. The repo must have GitHub Pages enabled (Settings → Pages → Deploy from branch)
#   2. Run exports first:
#      python tools/run_exports.py --vault /path/to/vault --out-dir ./docs
#
# Usage:
#   bash scripts/deploy.sh "commit message"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
DOCS_DIR="$REPO_ROOT/docs"

# Default commit message
MSG="${1:-"content: update knowledge base export"}"

echo "=== Deploying Knowledge Base to GitHub Pages ==="

# 1. Make sure docs/ exists with the required files
if [ ! -f "$DOCS_DIR/index.html" ]; then
    echo "ERROR: docs/index.html not found. Run exports first:"
    echo "  python tools/run_exports.py --vault /path/to/vault --out-dir ./docs"
    exit 1
fi

# 2. Add .nojekyll to prevent GitHub Pages from ignoring underscore-prefixed files
touch "$DOCS_DIR/.nojekyll"

# 3. Commit and push
cd "$REPO_ROOT"
git add -A
git commit -m "$MSG"
git push origin main

echo "=== Deploy complete ==="
echo "GitHub Pages will be available at:"
echo "https://$(git remote get-url origin | sed 's/.*github.com.//;s/.git$//' | sed 's|/|.github.io/|').github.io/"
