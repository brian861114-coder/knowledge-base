#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_content_quality import (
    DERIVATION_SECTION_NAME,
    audit_note,
    load_schema,
    make_rename_map,
    parse_frontmatter,
    split_sections,
)
from kb_paths import is_ignored_note_path, repo_root, resolve_vault_path


DEFAULT_LIMIT = 0
DEFAULT_MAX_CHARS = 320
DERIVATION_CONTEXT_BY_TYPE = {
    "concept": ["嚴格定義", "核心公式", "符號與單位", "物理意義", "推導", "典型應用"],
    "law": ["定律摘要", "數學表述", "符號與單位", "物理意義", "推導", "適用條件"],
    "mathematical_tool": ["工具摘要", "數學定義", "推導", "幾何意義", "典型操作"],
}
DERIVATION_TARGET_TYPES = {"concept", "law", "mathematical_tool"}
DERIVATION_ISSUE_CATEGORIES = {"derivation_too_short", "derivation_missing_formula"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def relative_note_path(note_path: Path, vault: Path) -> str:
    return note_path.relative_to(vault).as_posix()


def find_existing_task_keys(out_dir: Path) -> tuple[set[tuple[str, str, str]], int]:
    keys: set[tuple[str, str, str]] = set()
    max_index = 0
    if not out_dir.exists():
        return keys, max_index
    for path in out_dir.glob("*.json"):
        if path.name == "manifest.json":
            continue
        try:
            payload = load_json(path)
            keys.add(
                (
                    str(payload.get("note_path", "")),
                    str(payload.get("issue_category", "")),
                    str(payload.get("target_section", "")),
                )
            )
        except Exception:
            pass
        try:
            prefix = path.stem.split("-", 1)[0]
            max_index = max(max_index, int(prefix))
        except Exception:
            continue
    return keys, max_index


def select_context_sections(note_type: str, sections: dict[str, str]) -> dict[str, str]:
    ordered_names = DERIVATION_CONTEXT_BY_TYPE.get(note_type, [])
    selected: dict[str, str] = {}
    for name in ordered_names:
        if name in sections:
            selected[name] = sections[name]
    if not selected:
        for name, content in sections.items():
            if len(selected) >= 5:
                break
            selected[name] = content
    return selected


def build_derivation_task(*, note_path: Path, vault: Path, schema: dict) -> dict | None:
    text = note_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)
    note_type = str(frontmatter.get("type", "")).strip()
    if note_type not in DERIVATION_TARGET_TYPES:
        return None

    rename_rules = schema["renames"]["rename_rules"].get(note_type, [])
    rename_map = make_rename_map(rename_rules)
    _ordered, sections = split_sections(body, rename_map)
    derivation_text = sections.get(DERIVATION_SECTION_NAME)
    if derivation_text is None:
        return None

    issues = audit_note(note_path, vault, schema)
    derivation_issue_categories = sorted({category for category, _message in issues if category in DERIVATION_ISSUE_CATEGORIES})
    if not derivation_issue_categories:
        return None

    title = str(frontmatter.get("title", note_path.stem))
    summary = str(frontmatter.get("summary", ""))

    must_include = [
        "show a mathematically coherent derivation path",
        "use at least one explicit LaTeX equation",
        "keep the derivation consistent with the existing equations and symbols",
    ]
    if note_type == "law":
        must_include.append("state the assumptions or conditions used in the derivation")
    elif note_type == "concept":
        must_include.append("connect the derivation to the concept definition instead of listing equations only")
    elif note_type == "mathematical_tool":
        must_include.append("explain what transformation, rule, or construction is being derived")

    return {
        "task_version": 1,
        "note_path": relative_note_path(note_path, vault),
        "note_type": note_type,
        "issue_category": "derivation_repair",
        "target_section": DERIVATION_SECTION_NAME,
        "target_constraints": {
            "min_chars": int(schema["content_rules"].get("audit_thresholds", {}).get("derivation_min_chars", 80)),
            "max_chars": DEFAULT_MAX_CHARS,
            "must_include": must_include,
            "must_not": [
                "empty filler",
                "equation list without explanatory steps",
                "invented notation not grounded in surrounding sections",
            ],
            "source_issue_categories": derivation_issue_categories,
        },
        "allowed_edits": [
            "replace_target_section_only",
        ],
        "forbidden_edits": [
            "modify_frontmatter",
            "modify_other_sections",
            "invent_new_wikilinks",
            "change_section_order",
            "change_existing_formulae_outside_target_section",
        ],
        "source_context": {
            "title": title,
            "summary": summary,
            "sections": select_context_sections(note_type, sections),
            "known_links": [],
            "provided_evidence": [],
        },
    }


def find_target_notes(vault: Path, schema: dict) -> list[Path]:
    candidates: list[Path] = []
    files = sorted(file_path for file_path in vault.rglob("*.md") if not is_ignored_note_path(file_path, vault))
    for file_path in files:
        issues = audit_note(file_path, vault, schema)
        if any(category in DERIVATION_ISSUE_CATEGORIES for category, _message in issues):
            candidates.append(file_path)
    return candidates


def main() -> None:
    parser = argparse.ArgumentParser(description="Build stronger-model derivation repair tasks from audit results.")
    parser.add_argument("--vault", help="Knowledge-base vault path. Falls back to KB_VAULT_PATH or .knowledge-base.local.json")
    parser.add_argument("--schema-dir", help="Schema directory. Defaults to repo_root()/schema")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Maximum number of new tasks to emit. Use 0 for all missing tasks.")
    parser.add_argument("--out-dir", help="Output directory. Defaults to batch_tasks/stronger_model/derivation_repair")
    args = parser.parse_args()

    repo = repo_root()
    vault = resolve_vault_path(args.vault)
    schema_dir = Path(args.schema_dir).resolve() if args.schema_dir else repo / "schema"
    out_dir = Path(args.out_dir).resolve() if args.out_dir else repo / "batch_tasks" / "stronger_model" / "derivation_repair"

    schema = load_schema(schema_dir)
    ensure_dir(out_dir)
    existing_keys, max_existing_index = find_existing_task_keys(out_dir)

    target_notes = find_target_notes(vault, schema)
    tasks_written: list[str] = []
    next_index = max_existing_index + 1

    for note_path in target_notes:
        task = build_derivation_task(note_path=note_path, vault=vault, schema=schema)
        if task is None:
            continue
        task_key = (str(task["note_path"]), str(task["issue_category"]), str(task["target_section"]))
        if task_key in existing_keys:
            continue
        if args.limit and len(tasks_written) >= args.limit:
            break
        task_path = out_dir / f"{next_index:03d}-{note_path.stem}.json"
        task_path.write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding="utf-8")
        tasks_written.append(task_path.name)
        existing_keys.add(task_key)
        next_index += 1

    manifest = {
        "category": "derivation_repair",
        "new_count": len(tasks_written),
        "total_count": len([path for path in out_dir.glob("*.json") if path.name != "manifest.json"]),
        "vault": str(vault),
        "schema_dir": str(schema_dir),
        "new_tasks": tasks_written,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {len(tasks_written)} new tasks to {out_dir}")


if __name__ == "__main__":
    main()
