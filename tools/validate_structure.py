#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from kb_paths import is_ignored_note_path, repo_root, resolve_vault_path


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
FORMULA_RE = re.compile(r"(?<!\\)(\$\$.*?\$\$|\$[^$\n]+\$)", re.DOTALL)


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


def load_json_yaml(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema(schema_dir: Path) -> dict:
    return {
        "note_types": load_json_yaml(schema_dir / "note_types.yaml"),
        "sections": load_json_yaml(schema_dir / "sections.yaml"),
        "renames": load_json_yaml(schema_dir / "renaming_rules.yaml"),
        "content_rules": load_json_yaml(schema_dir / "content_rules.yaml"),
    }


def extract_sections(body: str) -> list[str]:
    return [match.group(1).strip() for match in SECTION_RE.finditer(body)]


def has_formula(body: str) -> bool:
    return bool(FORMULA_RE.search(body))


def make_rename_map(rename_rules: list[dict]) -> tuple[dict[str, str], set[str]]:
    rename_map: dict[str, str] = {}
    merge_targets: set[str] = set()
    for rule in rename_rules:
        target = str(rule["to"]).strip()
        if rule.get("action") == "merge":
            merge_targets.add(target)
        for source in rule.get("from", []):
            source_name = str(source).strip()
            if not source_name or source_name == target:
                continue
            rename_map[source_name] = target
    return rename_map, merge_targets


def normalize_sections(sections: list[str], rename_map: dict[str, str]) -> tuple[list[str], list[str]]:
    normalized: list[str] = []
    legacy_hits: list[str] = []
    seen: set[str] = set()
    for heading in sections:
        target = rename_map.get(heading, heading)
        if heading in rename_map:
            legacy_hits.append(f"{heading} -> {target}")
        if target in seen:
            continue
        seen.add(target)
        normalized.append(target)
    return normalized, legacy_hits


def check_required_order(headings: list[str], required_order: list[str]) -> list[str]:
    present_required = [heading for heading in headings if heading in required_order]
    expected = [heading for heading in required_order if heading in present_required]
    if present_required != expected:
        return [f"required section order mismatch: got {present_required}, expected {expected}"]
    return []


def check_missing_required(headings: set[str], required_order: list[str]) -> list[str]:
    return [heading for heading in required_order if heading not in headings]


def check_conditional_requirements(headings: set[str], body: str, rules: list[dict]) -> list[str]:
    issues: list[str] = []
    formula_present = has_formula(body)
    for rule in rules:
        triggered = False
        section_name = rule.get("if_section_present")
        if isinstance(section_name, str) and section_name in headings:
            triggered = True
        if rule.get("if_formula_present") is True and formula_present:
            triggered = True
        if not triggered:
            continue
        for required in rule.get("require_sections", []):
            if required not in headings:
                if section_name:
                    issues.append(f"missing conditional section: {required} required when {section_name} is present")
                else:
                    issues.append(f"missing conditional section: {required} required when formula is present")
    return issues


def check_map_optional_positions(headings: list[str], ordering_rules: list[dict]) -> list[str]:
    issues: list[str] = []
    positions = {}
    for rule in ordering_rules:
        positions.update(rule.get("optional_section_positions", {}))
    if not positions:
        return issues

    for heading, config in positions.items():
        if heading not in headings:
            continue
        heading_index = headings.index(heading)
        allowed_after = [item["after"] for item in config.get("allowed", []) if "after" in item]
        if not allowed_after:
            continue
        previous_heading = headings[heading_index - 1] if heading_index > 0 else None
        if previous_heading not in allowed_after:
            issues.append(f"{heading} must appear immediately after one of {allowed_after}, got after {previous_heading}")
        if config.get("fixed_position") is True:
            for anchor in allowed_after:
                if anchor in headings:
                    anchor_index = headings.index(anchor)
                    if heading_index != anchor_index + 1:
                        issues.append(f"{heading} must be immediately after {anchor}")
    return issues


def validate_note(path: Path, vault: Path, schema: dict) -> list[str]:
    text = path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)
    note_type = str(frontmatter.get("type", "")).strip()
    if not note_type:
        return []

    section_schemas = schema["sections"]["section_schemas"]
    if note_type not in section_schemas:
        return []

    rename_rules = schema["renames"]["rename_rules"].get(note_type, [])
    rename_map, _merge_targets = make_rename_map(rename_rules)
    raw_sections = extract_sections(body)
    normalized_sections, legacy_hits = normalize_sections(raw_sections, rename_map)
    headings_set = set(normalized_sections)
    note_schema = section_schemas[note_type]
    required_order = note_schema.get("required_order", [])
    conditional_requirements = note_schema.get("conditional_requirements", [])
    ordering_rules = note_schema.get("ordering_rules", [])

    rel_path = path.relative_to(vault).as_posix()
    issues: list[str] = []
    for legacy in legacy_hits:
        issues.append(f"{rel_path}: legacy heading hit: {legacy}")

    missing_required = check_missing_required(headings_set, required_order)
    for heading in missing_required:
        issues.append(f"{rel_path}: missing required section: {heading}")

    for issue in check_required_order(normalized_sections, required_order):
        issues.append(f"{rel_path}: {issue}")

    for issue in check_conditional_requirements(headings_set, body, conditional_requirements):
        issues.append(f"{rel_path}: {issue}")

    for issue in check_map_optional_positions(normalized_sections, ordering_rules):
        issues.append(f"{rel_path}: {issue}")

    return issues


def classify_issue(issue: str) -> str:
    if "legacy heading hit:" in issue:
        return "legacy_heading"
    if "missing required section:" in issue:
        return "missing_required_section"
    if "required section order mismatch:" in issue:
        return "section_order_mismatch"
    if "missing conditional section:" in issue:
        return "missing_conditional_section"
    if "must appear immediately after" in issue or "must be immediately after" in issue:
        return "optional_section_position"
    return "other"


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate note section structure against the local schema.")
    parser.add_argument("--vault", help="Knowledge-base vault path. Falls back to KB_VAULT_PATH or .knowledge-base.local.json")
    parser.add_argument("--schema-dir", help="Schema directory. Defaults to repo_root()/schema")
    args = parser.parse_args()

    repo = repo_root()
    vault = resolve_vault_path(args.vault)
    if not vault.exists():
        raise SystemExit(f"Vault path does not exist: {vault}")

    schema_dir = Path(args.schema_dir).resolve() if args.schema_dir else repo / "schema"
    if not schema_dir.exists():
        raise SystemExit(f"Schema directory does not exist: {schema_dir}")

    schema = load_schema(schema_dir)
    files = sorted(file_path for file_path in vault.rglob("*.md") if not is_ignored_note_path(file_path, vault))

    issues: list[str] = []
    for file_path in files:
        issues.extend(validate_note(file_path, vault, schema))

    issue_counts = Counter(classify_issue(issue) for issue in issues)
    affected_files = Counter(issue.split(":", 1)[0] for issue in issues if ":" in issue)

    print("Structure validation summary")
    print(f"- vault: {vault}")
    print(f"- notes scanned: {len(files)}")
    print(f"- schema dir: {schema_dir}")
    print(f"- issues: {len(issues)}")
    print(f"- files with issues: {len(affected_files)}")

    if issue_counts:
        print("- issue categories:")
        for category, count in issue_counts.most_common():
            print(f"  - {category}: {count}")

    if affected_files:
        print("- top affected files:")
        for rel_path, count in affected_files.most_common(10):
            print(f"  - {rel_path}: {count}")

    if issues:
        print("\nStructure validation failed:")
        for issue in issues[:100]:
            print(f"- {issue}")
        if len(issues) > 100:
            print(f"- ... {len(issues) - 100} more issues")
        raise SystemExit(1)

    print("\nStructure validation passed.")


if __name__ == "__main__":
    main()
