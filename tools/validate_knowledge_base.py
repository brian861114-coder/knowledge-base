#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from kb_paths import repo_root, resolve_vault_path


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")
MATH_TOKEN_RE = re.compile(r"(?<!\\)(\$\$|\$)")
RELATION_FIELDS = {
    "prerequisites",
    "related_concepts",
    "related_quantities",
    "related_laws",
    "experiments",
    "math_tools",
    "derived_results",
    "modern_connections",
    "tested_laws",
    "measured_quantities",
    "measurement_methods",
    "used_in",
    "includes",
    "recommended_order",
}
BASE_REQUIRED_FIELDS = ("type", "title", "summary")
DOMAIN_REQUIRED_TYPES = {"law", "concept", "quantity", "experiment"}


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


def normalize_target(value: str) -> str:
    return value.strip().lower().replace(" ", "-")


def extract_links(body: str) -> list[str]:
    return [match.group(1).strip() for match in WIKILINK_RE.finditer(body)]


def math_issues(body: str, note_path: str) -> list[str]:
    issues: list[str] = []
    display_count = body.count("$$")
    if display_count % 2 != 0:
        issues.append(f"{note_path}: unmatched $$ delimiter count ({display_count})")
    inline_count = 0
    for token in MATH_TOKEN_RE.finditer(body):
        if token.group(1) == "$$":
            continue
        inline_count += 1
    if inline_count % 2 != 0:
        issues.append(f"{note_path}: unmatched $ delimiter count ({inline_count})")
    return issues


def collect_vault_diagnostics(vault: Path) -> dict:
    files = sorted(vault.rglob("*.md"))
    note_ids: set[str] = set()
    paths: list[str] = []
    titles: list[str] = []
    missing_fields: list[str] = []
    broken_links: list[str] = []
    broken_relations: list[str] = []
    math_errors: list[str] = []
    parsed_notes = []

    for file_path in files:
        text = file_path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(text)
        rel_path = file_path.relative_to(vault).as_posix()
        note_id = normalize_target(file_path.stem)
        note_ids.add(note_id)
        paths.append(rel_path)
        titles.append(str(frontmatter.get("title", file_path.stem)).strip())
        parsed_notes.append((rel_path, frontmatter, body))

        note_type = str(frontmatter.get("type", "")).strip()
        required_fields = list(BASE_REQUIRED_FIELDS)
        if note_type in DOMAIN_REQUIRED_TYPES:
            required_fields.append("domain")
        absent = [field for field in required_fields if not str(frontmatter.get(field, "")).strip()]
        if absent:
            missing_fields.append(f"{rel_path}: missing {', '.join(absent)}")

        math_errors.extend(math_issues(body, rel_path))

    for rel_path, frontmatter, body in parsed_notes:
        for target in extract_links(body):
            if normalize_target(target) not in note_ids:
                broken_links.append(f"{rel_path}: [[{target}]]")

        for field_name in RELATION_FIELDS:
            raw = frontmatter.get(field_name, [])
            if isinstance(raw, str):
                items = [raw] if raw else []
            elif isinstance(raw, list):
                items = raw
            else:
                items = []
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


def validate_exports(repo: Path, note_ids: set[str], expected_count: int) -> tuple[list[str], dict]:
    errors: list[str] = []
    details_path = repo / "physics_note_details.json"
    graph_path = repo / "physics_graph.json"

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the vault and exported JSON.")
    parser.add_argument("--vault", help="Knowledge-base vault path. Falls back to KB_VAULT_PATH or .knowledge-base.local.json")
    args = parser.parse_args()

    repo = repo_root()
    vault = resolve_vault_path(args.vault)
    if not vault.exists():
        raise SystemExit(f"Vault path does not exist: {vault}")

    diagnostics = collect_vault_diagnostics(vault)
    export_errors, export_stats = validate_exports(repo, diagnostics["note_ids"], diagnostics["note_count"])

    errors = []
    errors.extend(diagnostics["missing_fields"])
    errors.extend(diagnostics["broken_links"])
    errors.extend(diagnostics["broken_relations"])
    errors.extend(diagnostics["math_errors"])
    errors.extend(f"duplicate title: {title}" for title in diagnostics["duplicate_titles"])
    errors.extend(f"duplicate path: {path}" for path in diagnostics["duplicate_paths"])
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
