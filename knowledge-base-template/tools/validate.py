#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from kb_config import (
    base_required_fields,
    parse_frontmatter,
    parse_frontmatter_data,
    extract_links,
    normalize_target,
    relation_fields,
    require_domain_for,
)
from kb_paths import is_ignored_note_path, resolve_vault_path


def collect_vault_diagnostics(vault: Path) -> dict:
    files = sorted(file_path for file_path in vault.rglob("*.md") if not is_ignored_note_path(file_path, vault))
    note_ids: set[str] = set()
    missing_fields: list[str] = []
    broken_links: list[str] = []
    broken_relations: list[str] = []
    math_errors: list[str] = []
    parsed_notes = []
    paths: list[str] = []
    titles: list[str] = []

    required_base = tuple(base_required_fields() or ("type", "title", "summary"))
    domain_required_types = require_domain_for()
    relation_field_names = relation_fields()

    for file_path in files:
        text = file_path.read_text(encoding="utf-8")
        raw_fm, body = parse_frontmatter(text)
        frontmatter = parse_frontmatter_data(raw_fm)
        rel_path = file_path.relative_to(vault).as_posix()
        note_id = normalize_target(file_path.stem)
        note_ids.add(note_id)
        paths.append(rel_path)
        titles.append(str(frontmatter.get("title", file_path.stem)).strip())
        parsed_notes.append((rel_path, frontmatter, body))

        note_type = str(frontmatter.get("type", "")).strip()
        required_fields = list(required_base)
        if note_type in domain_required_types:
            required_fields.append("domain")
        absent = [field for field in required_fields if not str(frontmatter.get(field, "")).strip()]
        if absent:
            missing_fields.append(f"{rel_path}: missing {', '.join(absent)}")

        math_errors.extend(math_issues(body, rel_path))

    for rel_path, frontmatter, body in parsed_notes:
        for target in extract_links(body):
            if normalize_target(target) not in note_ids:
                broken_links.append(f"{rel_path}: [[{target}]]")

        for field_name in relation_field_names:
            raw = frontmatter.get(field_name, [])
            items = normalize_list(raw)
            for item in items:
                target = str(item).strip()
                if not target:
                    continue
                if target.startswith("[[") and target.endswith("]]"):
                    target = target[2:-2]
                target = target.split("|", 1)[0].strip()
                if normalize_target(target) not in note_ids:
                    broken_relations.append(f"{rel_path}: {field_name} -> {target}")

    path_counts = Counter(paths)
    title_counts = Counter(titles)

    return {
        "note_count": len(files),
        "note_ids": note_ids,
        "missing_fields": missing_fields,
        "broken_links": broken_links,
        "broken_relations": broken_relations,
        "math_errors": math_errors,
        "duplicate_paths": [path for path, count in path_counts.items() if count > 1],
        "duplicate_titles": [title for title, count in title_counts.items() if count > 1],
    }


def validate_exports(details_path: Path, graph_path: Path, note_ids: set[str], expected_count: int) -> tuple[list[str], dict]:
    errors: list[str] = []

    if not details_path.exists():
        errors.append(f"missing export file: {details_path}")
        details_payload = {}
    else:
        details_payload = json.loads(details_path.read_text(encoding="utf-8"))

    if not graph_path.exists():
        errors.append(f"missing export file: {graph_path}")
        graph_payload = {"nodes": [], "edges": []}
    else:
        graph_payload = json.loads(graph_path.read_text(encoding="utf-8"))

    detail_ids = set(details_payload.keys())
    normalized_detail_ids = {normalize_target(note_id) for note_id in detail_ids}
    graph_nodes = graph_payload.get("nodes", [])
    graph_edges = graph_payload.get("edges", [])
    graph_ids = {str(node.get("id", "")) for node in graph_nodes if node.get("id")}
    normalized_graph_ids = {normalize_target(node_id) for node_id in graph_ids}

    if len(detail_ids) != expected_count:
        errors.append(f"note details count mismatch: expected {expected_count}, got {len(detail_ids)}")
    if len(graph_nodes) != expected_count:
        errors.append(f"graph node count mismatch: expected {expected_count}, got {len(graph_nodes)}")

    missing_detail_ids = sorted(note_ids - normalized_detail_ids)
    if missing_detail_ids:
        errors.append(f"note details missing ids: {', '.join(missing_detail_ids[:10])}")

    missing_graph_ids = sorted(note_ids - normalized_graph_ids)
    if missing_graph_ids:
        errors.append(f"graph export missing ids: {', '.join(missing_graph_ids[:10])}")

    unknown_edge_targets = sorted(
        {
            str(edge.get("target", ""))
            for edge in graph_edges
            if str(edge.get("target", "")) and normalize_target(str(edge.get("target", ""))) not in normalized_graph_ids
        }
    )
    if unknown_edge_targets:
        errors.append(f"graph edges point to missing nodes: {', '.join(unknown_edge_targets[:10])}")

    return errors, {
        "details_count": len(detail_ids),
        "graph_nodes": len(graph_nodes),
        "graph_edges": len(graph_edges),
    }


def math_issues(body: str, note_path: str) -> list[str]:
    issues: list[str] = []
    display_count = body.count("$$")
    if display_count % 2 != 0:
        issues.append(f"{note_path}: unmatched $$ delimiter count ({display_count})")
    inline_count = body.count("$") - display_count * 2
    if inline_count % 2 != 0:
        issues.append(f"{note_path}: unmatched $ delimiter count ({inline_count})")
    return issues


def normalize_list(raw) -> list:
    if isinstance(raw, str):
        return [raw] if raw else []
    if isinstance(raw, list):
        return raw
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the vault and exported JSON.")
    parser.add_argument("--vault", help="Knowledge-base vault path")
    parser.add_argument("--graph", help="Path to graph JSON (optional)")
    parser.add_argument("--details", help="Path to note details JSON (optional)")
    args = parser.parse_args()

    vault = resolve_vault_path(args.vault)
    if not vault.exists():
        raise SystemExit(f"Vault path does not exist: {vault}")

    diagnostics = collect_vault_diagnostics(vault)
    errors = []
    errors.extend(diagnostics["missing_fields"])
    errors.extend(diagnostics["broken_links"])
    errors.extend(diagnostics["broken_relations"])
    errors.extend(diagnostics["math_errors"])
    errors.extend(f"duplicate title: {title}" for title in diagnostics["duplicate_titles"])
    errors.extend(f"duplicate path: {path}" for path in diagnostics["duplicate_paths"])

    export_stats = {"details_count": 0, "graph_nodes": 0, "graph_edges": 0}
    if args.graph and args.details:
        export_errors, export_stats = validate_exports(
            Path(args.details),
            Path(args.graph),
            diagnostics["note_ids"],
            diagnostics["note_count"],
        )
        errors.extend(export_errors)

    print("Validation summary")
    print(f"- vault: {vault}")
    print(f"- notes: {diagnostics['note_count']}")
    print(f"- note details: {export_stats['details_count']}")
    print(f"- graph nodes: {export_stats['graph_nodes']}")
    print(f"- graph edges: {export_stats['graph_edges']}")
    print(f"- missing required fields: {len(diagnostics['missing_fields'])}")
    print(f"- broken wikilinks: {len(diagnostics['broken_links'])}")
    print(f"- broken frontmatter relations: {len(diagnostics['broken_relations'])}")
    print(f"- math issues: {len(diagnostics['math_errors'])}")
    print(f"- duplicate titles: {len(diagnostics['duplicate_titles'])}")
    print(f"- duplicate paths: {len(diagnostics['duplicate_paths'])}")

    if errors:
        print("\nValidation failed:")
        for issue in errors[:50]:
            print(f"- {issue}")
        if len(errors) > 50:
            print(f"- ... {len(errors) - 50} more issues")
        raise SystemExit(1)

    print("\nValidation passed.")


if __name__ == "__main__":
    main()
