#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from kb_paths import is_ignored_note_path, load_local_config
from validate_knowledge_base import RELATION_FIELDS, normalize_target, parse_frontmatter


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(#[^\]|]+)?(?:\|([^\]]+))?\]\]")


def collect_note_ids(vault: Path) -> set[str]:
    note_ids: set[str] = set()
    for file_path in vault.rglob("*.md"):
        if is_ignored_note_path(file_path, vault):
            continue
        note_ids.add(normalize_target(file_path.stem))
    return note_ids


def rewrite_relation_line(line: str, note_ids: set[str]) -> tuple[str, int]:
    if ":" not in line:
        return line, 0
    key, value = line.split(":", 1)
    field = key.strip()
    if field not in RELATION_FIELDS:
        return line, 0

    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        target = value.strip().strip("'\"")
        raw_target = target[2:-2] if target.startswith("[[") and target.endswith("]]") else target
        raw_target = raw_target.split("|", 1)[0].strip()
        if target and normalize_target(raw_target) not in note_ids:
            return f"{key}: []", 1
        return line, 0

    items = [item.strip() for item in value[1:-1].split(",") if item.strip()]
    kept: list[str] = []
    removed = 0
    for item in items:
        target = item.strip().strip("'\"")
        raw_target = target[2:-2] if target.startswith("[[") and target.endswith("]]") else target
        raw_target = raw_target.split("|", 1)[0].strip()
        if target and normalize_target(raw_target) not in note_ids:
            removed += 1
            continue
        kept.append(item)
    return f"{key}: [{', '.join(kept)}]", removed


def sanitize_body(body: str, note_ids: set[str]) -> tuple[str, int]:
    replacements = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal replacements
        target = match.group(1).strip()
        alias = match.group(3)
        if normalize_target(target) in note_ids:
            return match.group(0)
        replacements += 1
        return alias or target

    return WIKILINK_RE.sub(replace, body), replacements


def sanitize_note(text: str, note_ids: set[str]) -> tuple[str, int, int]:
    frontmatter, body = parse_frontmatter(text)
    if not text.lstrip("\ufeff").startswith("---\n"):
        new_body, body_count = sanitize_body(text, note_ids)
        return new_body, 0, body_count

    frontmatter_end = text.find("\n---\n", 4)
    raw_frontmatter = text[4:frontmatter_end]
    lines = raw_frontmatter.splitlines()
    relation_removals = 0
    new_lines: list[str] = []
    for line in lines:
        new_line, removed = rewrite_relation_line(line, note_ids)
        new_lines.append(new_line)
        relation_removals += removed
    new_body, body_replacements = sanitize_body(body, note_ids)
    rebuilt = "---\n" + "\n".join(new_lines) + "\n---\n" + new_body
    return rebuilt, relation_removals, body_replacements


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove broken frontmatter relations and de-wikilink missing note targets.")
    parser.add_argument("--vault", help="Vault path. Defaults to .knowledge-base.local.json")
    parser.add_argument("--apply", action="store_true", help="Write changes back to the vault")
    args = parser.parse_args()

    vault_arg = args.vault or load_local_config().get("vaultPath")
    if not vault_arg:
        raise SystemExit("Vault path not configured.")
    vault = Path(vault_arg).resolve()
    note_ids = collect_note_ids(vault)

    changed_files = 0
    removed_relations = 0
    replaced_links = 0

    for file_path in sorted(vault.rglob("*.md")):
        if is_ignored_note_path(file_path, vault):
            continue
        original = file_path.read_text(encoding="utf-8")
        updated, rel_removed, links_replaced = sanitize_note(original, note_ids)
        if updated == original:
            continue
        changed_files += 1
        removed_relations += rel_removed
        replaced_links += links_replaced
        if args.apply:
            file_path.write_text(updated, encoding="utf-8")

    mode = "Applied" if args.apply else "Planned"
    print(f"{mode} changes in {changed_files} files")
    print(f"Frontmatter relations removed: {removed_relations}")
    print(f"Broken wikilinks converted to plain text: {replaced_links}")


if __name__ == "__main__":
    main()
