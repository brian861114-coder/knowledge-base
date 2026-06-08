#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_config import (
    extract_links,
    note_id_from_path,
    normalize_target,
    parse_frontmatter,
    parse_frontmatter_data,
    relation_fields,
)
from kb_paths import is_ignored_note_path


DEFAULT_EDGE_MAP = {
    "prerequisites": "requires",
    "related_notes": "related_to",
    "related_concepts": "related_to",
    "related_entities": "related_to",
    "related_principles": "related_to",
    "procedures": "uses",
    "case_studies": "illustrated_by",
    "examples": "illustrated_by",
    "used_in": "used_in",
    "includes": "organized_by",
    "recommended_order": "requires",
    "modern_connections": "extends_to",
}


def build_note_index(md_files: list[Path]) -> tuple[list[dict], dict[str, str]]:
    notes = []
    alias_to_id: dict[str, str] = {}

    for file_path in md_files:
        text = file_path.read_text(encoding="utf-8")
        raw_fm, body = parse_frontmatter(text)
        frontmatter = parse_frontmatter_data(raw_fm)
        note_id = note_id_from_path(file_path)
        title = str(frontmatter.get("title", file_path.stem))
        tags = frontmatter.get("tags", [])
        if not isinstance(tags, list):
            tags = []

        notes.append(
            {
                "file_path": file_path,
                "frontmatter": frontmatter,
                "body": body,
                "id": note_id,
                "title": title,
                "tags": tags,
            }
        )

        for alias in {file_path.stem, title, note_id}:
            normalized = normalize_target(str(alias))
            alias_to_id.setdefault(normalized, note_id)

    return notes, alias_to_id


def resolve_target_id(target: str, alias_to_id: dict[str, str]) -> str:
    normalized = normalize_target(target)
    return alias_to_id.get(normalized, normalized)


def extract_frontmatter_edges(node_id: str, frontmatter: dict, alias_to_id: dict[str, str]) -> list[dict]:
    edges = []
    for field_name in relation_fields():
        edge_type = DEFAULT_EDGE_MAP.get(field_name, "related_to")
        raw = frontmatter.get(field_name, [])
        if isinstance(raw, str):
            items = [raw] if raw else []
        elif isinstance(raw, list):
            items = raw
        else:
            items = []

        for item in items:
            if not item:
                continue
            target = str(item).strip()
            if target.startswith("[[") and target.endswith("]]"):
                target = target[2:-2]
            target = target.split("|", 1)[0].strip()
            edges.append(
                {
                    "source": node_id,
                    "target": resolve_target_id(target, alias_to_id),
                    "type": edge_type,
                }
            )
    return edges


def export_graph(vault: Path) -> dict:
    nodes = []
    edges = []
    md_files = sorted(file_path for file_path in vault.rglob("*.md") if not is_ignored_note_path(file_path, vault))
    notes, alias_to_id = build_note_index(md_files)

    for note in notes:
        file_path = note["file_path"]
        frontmatter = note["frontmatter"]
        body = note["body"]
        node_id = note["id"]
        title = note["title"]
        tags = note["tags"]

        nodes.append(
            {
                "id": node_id,
                "title": title,
                "type": frontmatter.get("type", "note"),
                "summary": frontmatter.get("summary", ""),
                "path": file_path.relative_to(vault).as_posix(),
                "domain": frontmatter.get("domain", ""),
                "taxonomy_domain": frontmatter.get("taxonomy_domain", ""),
                "tags": tags,
            }
        )

        edges.extend(extract_frontmatter_edges(node_id, frontmatter, alias_to_id))
        for target in extract_links(body):
            edges.append(
                {
                    "source": node_id,
                    "target": resolve_target_id(target, alias_to_id),
                    "type": "wikilink",
                }
            )

    return {"nodes": nodes, "edges": edges}


def main() -> None:
    parser = argparse.ArgumentParser(description="Export an Obsidian vault into graph JSON.")
    parser.add_argument("--vault", required=True, help="Path to vault root")
    parser.add_argument("--out", required=True, help="Output JSON file")
    args = parser.parse_args()

    vault = Path(args.vault).resolve()
    out = Path(args.out).resolve()
    payload = export_graph(vault)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported {len(payload['nodes'])} nodes and {len(payload['edges'])} edges to {out}")


if __name__ == "__main__":
    main()
