#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from audit_content_quality import (
    DIRECT_NEGATION_RE,
    GROUPED_RELATED_LINK_TYPES,
    MEANING_SECTION_BY_TYPE,
    RELATED_LINKS_SECTION_NAME,
    audit_note,
    load_schema,
    make_rename_map,
    parse_frontmatter,
    related_links_grouped,
    strip_markdown,
    split_sections,
)
from kb_paths import is_ignored_note_path, repo_root, resolve_vault_path


DEFAULT_TARGET_LIMIT = 0
DEFAULT_MAX_CHARS = 220
DEFAULT_BANNED_PATTERN_MAX_CHARS = 180
MEANING_CONTEXT_BY_TYPE = {
    "concept": ["概念摘要", "嚴格定義", "物理意義", "典型應用", "現代理論視角"],
    "law": ["定律摘要", "數學表述", "物理意義", "適用條件", "現代理論視角"],
    "quantity": ["定義", "數學表達", "物理意義", "現代理論視角"],
}
BANNED_PATTERN_CONTEXT_BY_TYPE = {
    "concept": ["概念摘要", "嚴格定義", "物理意義", "歷史背景"],
    "law": ["定律摘要", "數學表述", "物理意義", "歷史背景"],
    "quantity": ["定義", "數學表達", "物理意義", "歷史背景"],
    "experiment": ["實驗摘要", "問題背景", "歷史背景", "現代理論視角"],
    "map": ["地圖摘要", "主要主題", "關鍵概念", "延伸方向"],
    "mathematical_tool": ["工具摘要", "數學定義", "現代理論視角"],
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def relative_note_path(note_path: Path, vault: Path) -> str:
    return note_path.relative_to(vault).as_posix()


def select_context_sections(note_type: str, sections: dict[str, str]) -> dict[str, str]:
    ordered_names = MEANING_CONTEXT_BY_TYPE.get(note_type, [])
    selected: dict[str, str] = {}
    for name in ordered_names:
        if name in sections:
            selected[name] = sections[name]
    if not selected:
        for name, content in sections.items():
            if len(selected) >= 4:
                break
            selected[name] = content
    return selected


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


def build_meaning_task(
    *,
    note_path: Path,
    vault: Path,
    schema: dict,
    routing_rules: dict,
) -> dict | None:
    text = note_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)
    note_type = str(frontmatter.get("type", "")).strip()
    if note_type not in MEANING_SECTION_BY_TYPE:
        return None

    rename_rules = schema["renames"]["rename_rules"].get(note_type, [])
    rename_map = make_rename_map(rename_rules)
    _ordered, sections = split_sections(body, rename_map)

    target_section = MEANING_SECTION_BY_TYPE[note_type]
    if target_section not in sections:
        return None

    route_config = next(
        (item for item in routing_rules.get("weak_model_first", []) if item.get("issue_category") == "meaning_too_short"),
        None,
    )
    requirements = route_config.get("requirements", []) if route_config else []

    must_include = [
        "describe what this note is about in concrete physical terms",
        "explain why it matters",
    ]
    if note_type == "quantity":
        must_include.append("state what physical state, effect, or measurable aspect this quantity tracks")
    elif note_type == "law":
        must_include.append("state what mechanism or regularity this law captures")
    elif note_type == "concept":
        must_include.append("state how this concept helps interpret or organize physical behavior")

    title = str(frontmatter.get("title", note_path.stem))
    summary = str(frontmatter.get("summary", ""))

    return {
        "task_version": 1,
        "note_path": relative_note_path(note_path, vault),
        "note_type": note_type,
        "issue_category": "meaning_too_short",
        "target_section": target_section,
        "target_constraints": {
            "min_chars": int(schema["content_rules"].get("audit_thresholds", {}).get("meaning_min_chars", 100)),
            "max_chars": DEFAULT_MAX_CHARS,
            "must_include": must_include,
            "must_not": [
                "不是A而是B",
                "empty filler",
            ],
            "additional_requirements": requirements,
        },
        "allowed_edits": [
            "replace_target_section_only",
        ],
        "forbidden_edits": [
            "modify_frontmatter",
            "modify_other_sections",
            "invent_new_wikilinks",
            "change_existing_formulae",
            "change_section_order",
        ],
        "source_context": {
            "title": title,
            "summary": summary,
            "sections": select_context_sections(note_type, sections),
            "known_links": sorted(set(frontmatter.get("related_concepts", []))) if isinstance(frontmatter.get("related_concepts"), list) else [],
            "provided_evidence": [],
        },
    }


def build_related_links_task(
    *,
    note_path: Path,
    vault: Path,
    schema: dict,
    routing_rules: dict,
) -> dict | None:
    text = note_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)
    note_type = str(frontmatter.get("type", "")).strip()
    if note_type not in GROUPED_RELATED_LINK_TYPES:
        return None

    rename_rules = schema["renames"]["rename_rules"].get(note_type, [])
    rename_map = make_rename_map(rename_rules)
    _ordered, sections = split_sections(body, rename_map)
    related_text = sections.get(RELATED_LINKS_SECTION_NAME, "")
    if not related_text or related_links_grouped(related_text):
        return None

    route_config = next(
        (item for item in routing_rules.get("weak_model_first", []) if item.get("issue_category") == "ungrouped_related_links"),
        None,
    )
    requirements = route_config.get("requirements", []) if route_config else []
    title = str(frontmatter.get("title", note_path.stem))
    summary = str(frontmatter.get("summary", ""))
    links = re.findall(r"\[\[[^\]]+\]\]", related_text)

    return {
        "task_version": 1,
        "note_path": relative_note_path(note_path, vault),
        "note_type": note_type,
        "issue_category": "ungrouped_related_links",
        "target_section": RELATED_LINKS_SECTION_NAME,
        "target_constraints": {
            "must_include": [
                "group the existing links under level-3 subsections",
                "add one short explanatory sentence per group",
            ],
            "must_not": [
                "invent new links",
                "drop existing links without reason",
            ],
            "additional_requirements": requirements,
        },
        "allowed_edits": [
            "replace_target_section_only",
        ],
        "forbidden_edits": [
            "modify_frontmatter",
            "modify_other_sections",
            "invent_new_wikilinks",
            "change_section_order",
        ],
        "source_context": {
            "title": title,
            "summary": summary,
            "sections": {
                RELATED_LINKS_SECTION_NAME: related_text,
            },
            "known_links": links,
            "provided_evidence": [],
        },
    }


def build_banned_pattern_task(
    *,
    note_path: Path,
    vault: Path,
    schema: dict,
    routing_rules: dict,
) -> dict | None:
    text = note_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)
    note_type = str(frontmatter.get("type", "")).strip()
    rename_rules = schema["renames"]["rename_rules"].get(note_type, [])
    rename_map = make_rename_map(rename_rules)
    _ordered, sections = split_sections(body, rename_map)

    target_section = None
    target_content = None
    for heading, content in sections.items():
        if DIRECT_NEGATION_RE.search(strip_markdown(content)):
            target_section = heading
            target_content = content
            break
    if not target_section or not target_content:
        return None

    route_config = next(
        (item for item in routing_rules.get("weak_model_first", []) if item.get("issue_category") == "banned_pattern"),
        None,
    )
    requirements = route_config.get("requirements", []) if route_config else []
    title = str(frontmatter.get("title", note_path.stem))
    summary = str(frontmatter.get("summary", ""))
    selected_sections = select_context_sections(note_type, sections)
    selected_sections[target_section] = target_content

    return {
        "task_version": 1,
        "note_path": relative_note_path(note_path, vault),
        "note_type": note_type,
        "issue_category": "banned_pattern",
        "target_section": target_section,
        "target_constraints": {
            "max_chars": DEFAULT_BANNED_PATTERN_MAX_CHARS,
            "must_include": [
                "keep the original meaning",
                "rewrite only the local phrasing that feels templated",
            ],
            "must_not": [
                "不是A而是B",
                "direct contrast filler",
            ],
            "additional_requirements": requirements,
        },
        "allowed_edits": [
            "replace_target_section_only",
        ],
        "forbidden_edits": [
            "modify_frontmatter",
            "modify_other_sections",
            "invent_new_wikilinks",
            "change_existing_formulae",
            "change_section_order",
        ],
        "source_context": {
            "title": title,
            "summary": summary,
            "sections": selected_sections,
            "known_links": [],
            "provided_evidence": [],
        },
    }


def find_target_notes(vault: Path, schema: dict, category: str) -> list[Path]:
    candidates: list[Path] = []
    files = sorted(file_path for file_path in vault.rglob("*.md") if not is_ignored_note_path(file_path, vault))
    for file_path in files:
        issues = audit_note(file_path, vault, schema)
        if any(issue_category == category for issue_category, _message in issues):
            candidates.append(file_path)
    return candidates


def build_task_for_category(*, category: str, note_path: Path, vault: Path, schema: dict, routing_rules: dict) -> dict | None:
    if category == "meaning_too_short":
        return build_meaning_task(note_path=note_path, vault=vault, schema=schema, routing_rules=routing_rules)
    if category == "ungrouped_related_links":
        return build_related_links_task(note_path=note_path, vault=vault, schema=schema, routing_rules=routing_rules)
    if category == "banned_pattern":
        return build_banned_pattern_task(note_path=note_path, vault=vault, schema=schema, routing_rules=routing_rules)
    raise SystemExit(f"Unsupported category for weak-model task generation: {category}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build weak-model section repair tasks from audit categories.")
    parser.add_argument("--vault", help="Knowledge-base vault path. Falls back to KB_VAULT_PATH or .knowledge-base.local.json")
    parser.add_argument("--schema-dir", help="Schema directory. Defaults to repo_root()/schema")
    parser.add_argument("--routing", help="Routing config path. Defaults to llm_configs/issue_routing_rules.json")
    parser.add_argument("--category", default="meaning_too_short", help="Audit issue category to turn into tasks")
    parser.add_argument("--limit", type=int, default=DEFAULT_TARGET_LIMIT, help="Maximum number of new tasks to emit. Use 0 for all missing tasks.")
    parser.add_argument("--out-dir", help="Output directory. Defaults to batch_tasks/deepseek_v4pro/<category>")
    args = parser.parse_args()

    repo = repo_root()
    vault = resolve_vault_path(args.vault)
    schema_dir = Path(args.schema_dir).resolve() if args.schema_dir else repo / "schema"
    routing_path = Path(args.routing).resolve() if args.routing else repo / "llm_configs" / "issue_routing_rules.json"
    out_dir = Path(args.out_dir).resolve() if args.out_dir else repo / "batch_tasks" / "deepseek_v4pro" / args.category

    schema = load_schema(schema_dir)
    routing_rules = load_json(routing_path)
    ensure_dir(out_dir)
    existing_keys, max_existing_index = find_existing_task_keys(out_dir)

    target_notes = find_target_notes(vault, schema, args.category)
    tasks_written: list[str] = []
    next_index = max_existing_index + 1

    for note_path in target_notes:
        task = build_task_for_category(
            category=args.category,
            note_path=note_path,
            vault=vault,
            schema=schema,
            routing_rules=routing_rules,
        )
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
        "category": args.category,
        "new_count": len(tasks_written),
        "total_count": len([path for path in out_dir.glob('*.json') if path.name != 'manifest.json']),
        "vault": str(vault),
        "schema_dir": str(schema_dir),
        "routing": str(routing_path),
        "new_tasks": tasks_written,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {len(tasks_written)} new tasks to {out_dir}")


if __name__ == "__main__":
    main()
