#!/usr/bin/env python3
"""Export note detailed content (sections, previews) from an Obsidian vault.

Produces a JSON file mapping node IDs → {id, path, title, summary,
body_preview, body_full, sections} for the frontend reader mode.

Usage:
  python tools/export_note_details.py --vault /path/to/vault --out note_details.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_config import (
    parse_frontmatter,
    parse_frontmatter_data,
    note_id_from_path,
    clean_text,
    extract_sections,
)


def build_details(vault: Path) -> dict:
    """掃描 vault 中的所有 .md 檔案，生成節點詳情 JSON。"""
    payload = {}
    for file_path in sorted(vault.rglob("*.md")):
        text = file_path.read_text(encoding="utf-8")
        raw_fm, body = parse_frontmatter(text)
        frontmatter = parse_frontmatter_data(raw_fm)
        node_id = note_id_from_path(file_path)
        cleaned_body = clean_text(body)

        payload[node_id] = {
            "id": node_id,
            "path": file_path.relative_to(vault).as_posix(),
            "title": frontmatter.get("title", file_path.stem),
            "summary": frontmatter.get("summary", ""),
            "body_preview": cleaned_body[:900],
            "body_full": cleaned_body,
            "sections": extract_sections(body),
        }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Export note detail previews from an Obsidian vault.")
    parser.add_argument("--vault", required=True, help="Vault root path")
    parser.add_argument("--out", required=True, help="Output JSON path")
    args = parser.parse_args()

    vault = Path(args.vault).resolve()
    out = Path(args.out).resolve()
    payload = build_details(vault)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported {len(payload)} note details to {out}")


if __name__ == "__main__":
    main()
