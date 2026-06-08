#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from apply_weak_model_response import apply_response_to_text, load_schema, make_rename_map, parse_frontmatter
from audit_content_quality import DIRECT_NEGATION_RE, load_schema as load_audit_schema, split_sections, strip_markdown
from kb_paths import repo_root, resolve_vault_path


REWRITE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"這不是[^，。；\n]{0,60}，而是因為"), "這是因為"),
    (re.compile(r"這不是[^，。；\n]{0,60}，而是"), "這是"),
    (re.compile(r"它不是[^，。；\n]{0,60}，而是因為"), "它是因為"),
    (re.compile(r"它不是[^，。；\n]{0,60}，而是"), "它是"),
    (re.compile(r"並不是[^，。；\n]{0,60}，而是因為"), "是因為"),
    (re.compile(r"並不是[^，。；\n]{0,60}，而是"), "是"),
    (re.compile(r"不是因為[^，。；\n]{0,80}，而是因為"), "因為"),
    (re.compile(r"不是[^，。；\n]{0,60}，而是因為"), "因為"),
    (re.compile(r"不是[^，。；\n]{0,60}，而是把"), "把"),
    (re.compile(r"不是[^，。；\n]{0,60}，而是由"), "由"),
    (re.compile(r"不是[^，。；\n]{0,60}，而是從"), "從"),
    (re.compile(r"不是[^，。；\n]{0,60}，而是"), "是"),
    (re.compile(r"不是因為[^，。；\n]{0,80}而是因為"), "因為"),
    (re.compile(r"不是[^，。；\n]{0,60}而是因為"), "因為"),
    (re.compile(r"不是[^，。；\n]{0,60}而是把"), "把"),
    (re.compile(r"不是[^，。；\n]{0,60}而是由"), "由"),
    (re.compile(r"不是[^，。；\n]{0,60}而是從"), "從"),
    (re.compile(r"不是[^，。；\n]{0,60}而是"), "是"),
]

TITLE_SPECIFIC_REPLACEMENTS: dict[str, list[tuple[str, str]]] = {
    "穩態": [
        ("穩態不是不動的口語說法，而是把演化方程中的時間導數壓成零後得到的平衡解", "穩態是把演化方程中的時間導數壓成零後得到的平衡解"),
    ],
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_text(text: str) -> str:
    text = text.replace("  ", " ")
    text = text.replace("，，", "，")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def rewrite_banned_patterns(text: str, title: str) -> str:
    updated = text
    for pattern, replacement in REWRITE_PATTERNS:
        updated = pattern.sub(replacement, updated)
    for source, target in TITLE_SPECIFIC_REPLACEMENTS.get(title, []):
        updated = updated.replace(source, target)
    return normalize_text(updated)


def collect_targets(audit_json: Path, vault: Path, schema_dir: Path) -> list[tuple[Path, str]]:
    audit = load_json(audit_json)
    rel_paths = [item["message"].split(":", 1)[0] for item in audit.get("issues", []) if item.get("category") == "banned_pattern"]
    schema = load_audit_schema(schema_dir)
    targets: list[tuple[Path, str]] = []
    for rel in rel_paths:
        note_path = (vault / rel).resolve()
        text = note_path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(text)
        note_type = str(frontmatter.get("type", "")).strip()
        rename_map = make_rename_map(schema["renames"]["rename_rules"].get(note_type, []))
        _ordered, sections = split_sections(body, rename_map)
        for heading, content in sections.items():
            if DIRECT_NEGATION_RE.search(strip_markdown(content)):
                targets.append((note_path, heading))
                break
    return targets


def main() -> None:
    parser = argparse.ArgumentParser(description="Rule-based cleanup for banned '不是A而是B' style phrasing.")
    parser.add_argument("--vault", help="Override vault path")
    parser.add_argument("--audit-json", default="tmp/audit_results_after_banned_pattern_apply.json", help="Audit JSON path")
    parser.add_argument("--schema-dir", help="Schema directory. Defaults to repo_root()/schema")
    parser.add_argument("--write", action="store_true", help="Write changes back to the vault")
    args = parser.parse_args()

    repo = repo_root()
    vault = resolve_vault_path(args.vault)
    schema_dir = Path(args.schema_dir).resolve() if args.schema_dir else repo / "schema"
    audit_json = (repo / args.audit_json).resolve()
    schema = load_schema(schema_dir)

    changed = 0
    unchanged = 0
    unresolved: list[str] = []

    for note_path, target_section in collect_targets(audit_json, vault, schema_dir):
        text = note_path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(text)
        note_type = str(frontmatter.get("type", "")).strip()
        rename_map = make_rename_map(schema["renames"]["rename_rules"].get(note_type, []))
        _ordered, sections = split_sections(body, rename_map)
        current = sections[target_section]
        title = str(frontmatter.get("title", note_path.stem)).strip()
        updated_section = rewrite_banned_patterns(current, title)

        if updated_section == current:
            unchanged += 1
            unresolved.append(str(note_path))
            continue

        updated_text, _matched = apply_response_to_text(
            text,
            note_type=note_type,
            target_section=target_section,
            replacement_body=updated_section,
            rename_map=rename_map,
        )
        changed += 1
        if args.write:
            note_path.write_text(updated_text, encoding="utf-8")

    print("Banned pattern cleanup summary")
    print(f"- audit json: {audit_json}")
    print(f"- vault: {vault}")
    print(f"- changed: {changed}")
    print(f"- unchanged: {unchanged}")
    print(f"- write: {args.write}")
    if unresolved:
        print("- unresolved:")
        for item in unresolved:
            print(f"  - {item}")


if __name__ == "__main__":
    main()
