#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from kb_paths import is_ignored_note_path, repo_root, resolve_vault_path


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
SUBSECTION_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
FORMULA_RE = re.compile(r"(?<!\\)(\$\$.*?\$\$|\$[^$\n]+\$)", re.DOTALL)
YEAR_RE = re.compile(r"\b(1[5-9]\d{2}|20\d{2}|2100)\b")
LATIN_NAME_RE = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\b")


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
        "renames": load_json_yaml(schema_dir / "renaming_rules.yaml"),
        "content_rules": load_json_yaml(schema_dir / "content_rules.yaml"),
    }


def make_rename_map(rename_rules: list[dict]) -> dict[str, str]:
    rename_map: dict[str, str] = {}
    for rule in rename_rules:
        target = str(rule["to"]).strip()
        for source in rule.get("from", []):
            source_name = str(source).strip()
            if not source_name or source_name == target:
                continue
            rename_map[source_name] = target
    return rename_map


def split_sections(body: str, rename_map: dict[str, str]) -> tuple[list[str], dict[str, str]]:
    matches = list(SECTION_RE.finditer(body))
    ordered_headings: list[str] = []
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        raw_heading = match.group(1).strip()
        heading = rename_map.get(raw_heading, raw_heading)
        content_start = match.end()
        content_end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = body[content_start:content_end].strip()
        if heading not in sections:
            ordered_headings.append(heading)
            sections[heading] = content
        else:
            sections[heading] = sections[heading].rstrip() + ("\n\n" if sections[heading] and content else "") + content
    return ordered_headings, sections


def strip_markdown(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), text)
    text = re.sub(r"[*_>#-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def visible_length(text: str) -> int:
    return len(strip_markdown(text))


def has_formula(text: str) -> bool:
    return bool(FORMULA_RE.search(text))


def has_history_anchor(text: str) -> bool:
    return bool(YEAR_RE.search(text) or LATIN_NAME_RE.search(text))


def related_links_grouped(text: str) -> bool:
    return bool(SUBSECTION_RE.search(text))


def section_aliases(schema: dict, note_type: str) -> dict:
    return schema["content_rules"].get("content_rules", {}).get("types", {}).get(note_type, {})


def banned_patterns(schema: dict) -> list[str]:
    return list(schema["content_rules"].get("content_rules", {}).get("global", {}).get("banned_patterns", []))


def audit_note(path: Path, vault: Path, schema: dict) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)
    note_type = str(frontmatter.get("type", "")).strip()
    if not note_type:
        return []

    rename_rules = schema["renames"]["rename_rules"].get(note_type, [])
    rename_map = make_rename_map(rename_rules)
    _ordered_headings, sections = split_sections(body, rename_map)
    thresholds = schema["content_rules"].get("audit_thresholds", {})
    aliases = section_aliases(schema, note_type)

    rel_path = path.relative_to(vault).as_posix()
    issues: list[tuple[str, str]] = []
    plain_body = strip_markdown(body).lower()

    for pattern in banned_patterns(schema):
        if pattern.lower() in plain_body:
            issues.append(("banned_pattern", f"{rel_path}: contains banned phrase '{pattern}'"))

    meaning_section = aliases.get("meaning_section")
    if isinstance(meaning_section, str) and meaning_section in sections:
        min_chars = int(thresholds.get("meaning_min_chars", 120))
        if visible_length(sections[meaning_section]) < min_chars:
            issues.append(("meaning_too_short", f"{rel_path}: {meaning_section} shorter than {min_chars} chars"))

    derivation_section_name = aliases.get("derivation_section")
    derivation_section = sections.get(derivation_section_name, "") if isinstance(derivation_section_name, str) else ""
    if derivation_section_name and derivation_section:
        min_chars = int(thresholds.get("derivation_min_chars", 100))
        if visible_length(derivation_section) < min_chars:
            issues.append(("derivation_too_short", f"{rel_path}: {derivation_section_name} shorter than {min_chars} chars"))
        if bool(thresholds.get("require_latex_in_derivation", False)) and not has_formula(derivation_section):
            issues.append(("derivation_missing_formula", f"{rel_path}: {derivation_section_name} has no LaTeX formula"))

    history_section_name = aliases.get("history_section")
    if isinstance(history_section_name, str) and history_section_name in sections:
        if bool(thresholds.get("require_people_or_year_in_history", True)) and not has_history_anchor(sections[history_section_name]):
            issues.append(("history_not_concrete", f"{rel_path}: {history_section_name} lacks a detectable person name or year"))

    symbol_section_name = aliases.get("symbol_section")
    if isinstance(symbol_section_name, str) and bool(thresholds.get("require_symbol_section_if_formula_present", True)) and has_formula(body):
        if symbol_section_name not in sections:
            issues.append(("missing_symbol_section", f"{rel_path}: formula present but missing {symbol_section_name}"))

    related_links_section_name = aliases.get("related_links_section")
    if isinstance(related_links_section_name, str) and bool(thresholds.get("require_grouped_related_links", True)):
        related_text = sections.get(related_links_section_name, "")
        if related_text and "[[" in related_text and not related_links_grouped(related_text):
            issues.append(("ungrouped_related_links", f"{rel_path}: {related_links_section_name} has links but no grouped subsections"))

    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit note content quality against lightweight semantic rules.")
    parser.add_argument("--vault", help="Knowledge-base vault path. Falls back to KB_VAULT_PATH or .knowledge-base.local.json")
    parser.add_argument("--schema-dir", help="Schema directory. Defaults to repo_root()/schema")
    parser.add_argument("--json-out", help="Optional path to write full issue data as JSON")
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

    issues: list[tuple[str, str]] = []
    note_issue_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    by_file: dict[str, list[str]] = defaultdict(list)

    for file_path in files:
        note_issues = audit_note(file_path, vault, schema)
        if not note_issues:
            continue
        rel_path = file_path.relative_to(vault).as_posix()
        note_issue_counts[rel_path] = len(note_issues)
        for category, message in note_issues:
            issues.append((category, message))
            category_counts[category] += 1
            by_file[rel_path].append(message)

    if args.json_out:
        payload = {
            "vault": str(vault),
            "notes_scanned": len(files),
            "issues": [{"category": category, "message": message} for category, message in issues],
            "category_counts": dict(category_counts),
            "file_issue_counts": dict(note_issue_counts),
        }
        Path(args.json_out).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Content quality audit summary")
    print(f"- vault: {vault}")
    print(f"- notes scanned: {len(files)}")
    print(f"- schema dir: {schema_dir}")
    print(f"- issues: {len(issues)}")
    print(f"- files with issues: {len(note_issue_counts)}")

    if category_counts:
        print("- issue categories:")
        for category, count in category_counts.most_common():
            print(f"  - {category}: {count}")

    if note_issue_counts:
        print("- top affected files:")
        for rel_path, count in note_issue_counts.most_common(10):
            print(f"  - {rel_path}: {count}")

    if issues:
        score_buckets: Counter[int] = Counter(note_issue_counts.values())
        print("- issue-count buckets:")
        for bucket, count in sorted(score_buckets.items()):
            print(f"  - {bucket} issues: {count} files")

        print("\nContent quality audit failed:")
        for _category, message in issues[:100]:
            print(f"- {message}")
        if len(issues) > 100:
            print(f"- ... {len(issues) - 100} more issues")
        raise SystemExit(1)

    print("\nContent quality audit passed.")


if __name__ == "__main__":
    main()
