#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


TITLE_FIXES = {
    "02_concepts/RC電路.md": ("RC電路", "rc電路"),
    "02_concepts/RL電路.md": ("RL電路", "rl電路"),
    "02_concepts/RLC電路.md": ("RLC電路", "rlc電路"),
}


def normalize_note_title(path: Path, canonical_title: str, fallback_title: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    title_done = False
    heading_done = False
    for index, line in enumerate(lines):
        if not title_done and line.startswith("title: "):
            current_title = line[len("title: ") :].strip()
            if current_title == fallback_title:
                lines[index] = f"title: {canonical_title}"
            title_done = True
            continue
        if not heading_done and line.startswith("# "):
            current_heading = line[2:].strip()
            if current_heading == fallback_title:
                lines[index] = f"# {canonical_title}"
            heading_done = True
        if title_done and heading_done:
            break
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    vault = resolve_vault_path()
    for relative_path, (canonical_title, fallback_title) in TITLE_FIXES.items():
        normalize_note_title(vault / relative_path, canonical_title, fallback_title)
    print(f"normalized={len(TITLE_FIXES)} note titles")


if __name__ == "__main__":
    main()
