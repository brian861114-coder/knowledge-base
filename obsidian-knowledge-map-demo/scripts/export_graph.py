#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")
HEADING_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
RELATION_FIELDS = {
    "prerequisites": "requires",
    "related_concepts": "related_to",
    "related_quantities": "related_to",
    "related_laws": "related_to",
    "experiments": "verified_by",
    "math_tools": "formalized_by",
    "derived_results": "derives_to",
    "modern_connections": "explains",
    "tested_laws": "verified_by",
    "measured_quantities": "measures",
    "measurement_methods": "measures",
    "used_in": "uses",
    "includes": "organized_by",
    "recommended_order": "requires",
}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    text = text.lstrip("\ufeff")
    if not text.startswith("---\n"):
        return {}, text

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text

    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, object] = {}

    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            items = [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
            data[key] = items
        else:
            data[key] = value.strip("'\"")

    return data, body


def note_id_from_path(path: Path) -> str:
    return path.stem.strip().lower().replace(" ", "-")


def extract_title(frontmatter: dict, body: str, path: Path) -> str:
    if frontmatter.get("title"):
        return str(frontmatter["title"])
    match = HEADING_RE.search(body)
    if match:
        return match.group(1).strip()
    return path.stem


def extract_links(body: str) -> list[str]:
    return [match.group(1).strip() for match in WIKILINK_RE.finditer(body)]


def normalize_target(value: str) -> str:
    return value.strip().lower().replace(" ", "-")


def extract_frontmatter_edges(node_id: str, frontmatter: dict) -> list[dict]:
    edges = []
    for field_name, edge_type in RELATION_FIELDS.items():
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
                    "target": normalize_target(target),
                    "type": edge_type,
                }
            )
    return edges


def export_graph(vault: Path) -> dict:
    nodes = []
    edges = []
    md_files = sorted(vault.rglob("*.md"))

    for file_path in md_files:
        text = file_path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(text)
        node_id = note_id_from_path(file_path)
        title = extract_title(frontmatter, body, file_path)
        tags = frontmatter.get("tags", [])
        if not isinstance(tags, list):
            tags = []

        nodes.append(
            {
                "id": node_id,
                "title": title,
                "type": frontmatter.get("type", "note"),
                "summary": frontmatter.get("summary", ""),
                "path": file_path.relative_to(vault).as_posix(),
                "domain": frontmatter.get("domain", ""),
                "tags": tags,
            }
        )

        edges.extend(extract_frontmatter_edges(node_id, frontmatter))

        for target in extract_links(body):
            edges.append(
                {
                    "source": node_id,
                    "target": normalize_target(target),
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
