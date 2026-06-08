#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_paths import resolve_vault_path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply approved review-session revisions back to the vault.")
    parser.add_argument("--session-dir", required=True, help="Path to tmp/review_sessions/<session-id>.")
    parser.add_argument("--dry-run", action="store_true", help="Only print what would be applied.")
    args = parser.parse_args()

    session_dir = Path(args.session_dir).resolve()
    manifest = read_json(session_dir / "manifest.json")
    decisions = read_json(session_dir / "decisions.json")
    vault = resolve_vault_path()

    applied = 0
    for item_meta in manifest.get("items", []):
        item_id = item_meta["item_id"]
        decision = decisions.get(item_id, {}).get("decision")
        if decision != "approved":
            continue
        item = read_json(session_dir / item_meta["item_path"])
        target_path = vault / item["note_path"]
        if args.dry_run:
            print(f"Would apply: {target_path}")
        else:
            target_path.write_text(item["proposed_markdown"], encoding="utf-8")
            print(f"Applied: {target_path}")
        applied += 1

    print(f"Approved items processed: {applied}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
