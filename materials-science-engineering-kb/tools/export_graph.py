#!/usr/bin/env python3
"""Export an Obsidian vault into graph JSON.

Produces a graph JSON file compatible with the frontend graph visualizer.

Usage:
  python tools/export_graph.py --vault /path/to/vault --out graph.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from kb_config import (
    TEMPLATE_ROOT,
    WIKILINK_RE,
    HEADING_RE,
    extract_links,
    note_id_from_path,
    normalize_target,
    parse_frontmatter,
    parse_frontmatter_data,
)

# Map from frontmatter relation field names → edge type labels
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


def extract_title(frontmatter: dict, body: str, path: Path) -> str:
    """從 frontmatter 或 body 的 # 標題提取節點標題。"""
    if frontmatter.get("title"):
        return str(frontmatter["title"])
    match = HEADING_RE.search(body)
    if match:
        return match.group(1).strip()
    return path.stem


def build_note_index(md_files: list[Path]) -> tuple[list[dict], dict[str, str]]:
    """建立筆記索引與別名對照表。"""
    notes = []
    alias_to_id: dict[str, str] = {}

    for file_path in md_files:
        text = file_path.read_text(encoding="utf-8")
        raw_fm, body = parse_frontmatter(text)
        frontmatter = parse_frontmatter_data(raw_fm)
        note_id = note_id_from_path(file_path)
        title = extract_title(frontmatter, body, file_path)
        tags = frontmatter.get("tags", [])
        if not isinstance(tags, list):
            tags = []

        notes.append({
            "file_path": file_path,
            "frontmatter": frontmatter,
            "body": body,
            "id": note_id,
            "title": title,
            "tags": tags,
        })

        for alias in {file_path.stem, title, note_id}:
            normalized = normalize_target(str(alias))
            alias_to_id.setdefault(normalized, note_id)

    return notes, alias_to_id


def resolve_target_id(target: str, alias_to_id: dict[str, str]) -> str:
    """將 wikilink 目標解析為正式 node ID。"""
    normalized = normalize_target(target)
    return alias_to_id.get(normalized, normalized)


def extract_frontmatter_edges(node_id: str, frontmatter: dict, alias_to_id: dict[str, str]) -> list[dict]:
    """從 frontmatter 的關聯欄位提取邊。"""
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
            edges.append({
                "source": node_id,
                "target": resolve_target_id(target, alias_to_id),
                "type": edge_type,
            })
    return edges


def export_graph(vault: Path) -> dict:
    """主匯出函數：掃描 vault 中的所有 .md 檔案，生成圖譜 JSON。"""
    nodes = []
    edges = []
    md_files = sorted(vault.rglob("*.md"))
    notes, alias_to_id = build_note_index(md_files)

    for note in notes:
        file_path = note["file_path"]
        frontmatter = note["frontmatter"]
        body = note["body"]
        node_id = note["id"]
        title = note["title"]
        tags = note["tags"]

        nodes.append({
            "id": node_id,
            "title": title,
            "type": frontmatter.get("type", "note"),
            "summary": frontmatter.get("summary", ""),
            "path": file_path.relative_to(vault).as_posix(),
            "domain": frontmatter.get("domain", ""),
            "taxonomy_domain": frontmatter.get("taxonomy_domain", ""),
            "tags": tags,
        })

        edges.extend(extract_frontmatter_edges(node_id, frontmatter, alias_to_id))

        for target in extract_links(body):
            edges.append({
                "source": node_id,
                "target": resolve_target_id(target, alias_to_id),
                "type": "wikilink",
            })

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
