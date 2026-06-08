#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

from kb_paths import is_ignored_note_path, repo_root, resolve_vault_path


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class SectionBlock:
    heading: str
    body: str
    source_heading: str


def parse_frontmatter(text: str) -> tuple[str, str]:
    text = text.lstrip("\ufeff")
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 5 :]


def parse_frontmatter_data(raw: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data


def load_json_yaml(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema(schema_dir: Path) -> dict:
    return {
        "sections": load_json_yaml(schema_dir / "sections.yaml"),
        "renames": load_json_yaml(schema_dir / "renaming_rules.yaml"),
    }


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


def split_sections(body: str) -> tuple[str, list[SectionBlock]]:
    matches = list(SECTION_RE.finditer(body))
    if not matches:
        return body, []

    intro = body[: matches[0].start()]
    sections: list[SectionBlock] = []
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        content_start = match.end()
        content_end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = body[content_start:content_end]
        sections.append(SectionBlock(heading=heading, body=content, source_heading=heading))
    return intro, sections


def normalize_and_merge_sections(
    sections: list[SectionBlock], rename_map: dict[str, str], merge_targets: set[str]
) -> tuple[list[SectionBlock], list[str]]:
    normalized: list[SectionBlock] = []
    merged_index: dict[str, int] = {}
    changes: list[str] = []

    for section in sections:
        target = rename_map.get(section.heading, section.heading)
        if target != section.heading:
            changes.append(f"rename: {section.heading} -> {target}")

        updated = SectionBlock(heading=target, body=section.body, source_heading=section.source_heading)
        existing_index = merged_index.get(target)
        if existing_index is None:
            merged_index[target] = len(normalized)
            normalized.append(updated)
            continue

        existing = normalized[existing_index]
        left = existing.body.rstrip()
        right = updated.body.lstrip()
        joined = left + ("\n\n" if left and right else "") + right
        normalized[existing_index] = SectionBlock(
            heading=existing.heading,
            body=joined,
            source_heading=existing.source_heading,
        )
        if target in merge_targets:
            changes.append(f"merge: {updated.source_heading} into {target}")
        else:
            changes.append(f"dedupe: {updated.source_heading} into {target}")

    return normalized, changes


def resolve_section_order(section_schema: dict) -> list[str]:
    order = list(section_schema.get("required_order", []))
    appended_optional: list[str] = []
    optional_positions: dict[str, dict] = {}
    for rule in section_schema.get("ordering_rules", []):
        optional_positions.update(rule.get("optional_section_positions", {}))

    for optional_heading in section_schema.get("optional", []):
        config = optional_positions.get(optional_heading)
        if config and config.get("fixed_position") is True:
            inserted = False
            for anchor_rule in config.get("allowed", []):
                anchor = anchor_rule.get("after")
                if anchor in order:
                    order.insert(order.index(anchor) + 1, optional_heading)
                    inserted = True
                    break
            if inserted:
                continue
        appended_optional.append(optional_heading)
    return order + appended_optional


def reorder_sections(sections: list[SectionBlock], section_schema: dict) -> tuple[list[SectionBlock], bool]:
    desired_order = resolve_section_order(section_schema)
    rank = {heading: index for index, heading in enumerate(desired_order)}

    known: list[SectionBlock] = []
    unknown: list[SectionBlock] = []
    for section in sections:
        if section.heading in rank:
            known.append(section)
        else:
            unknown.append(section)

    reordered_known = sorted(known, key=lambda item: (rank[item.heading], sections.index(item)))
    changed = [block.heading for block in reordered_known] != [block.heading for block in known]
    return reordered_known + unknown, changed


def rebuild_body(intro: str, sections: list[SectionBlock]) -> str:
    if not sections:
        return intro
    parts: list[str] = []
    prefix = intro.rstrip()
    if prefix:
        parts.append(prefix)
        parts.append("")
    for section in sections:
        parts.append(f"## {section.heading}")
        parts.append(section.body.strip("\n"))
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def process_file(path: Path, schema: dict, dry_run: bool) -> tuple[bool, list[str]]:
    text = path.read_text(encoding="utf-8")
    raw_frontmatter, body = parse_frontmatter(text)
    frontmatter = parse_frontmatter_data(raw_frontmatter)
    note_type = frontmatter.get("type", "").strip()
    section_schema = schema["sections"]["section_schemas"].get(note_type)
    if not section_schema:
        return False, []

    rename_rules = schema["renames"]["rename_rules"].get(note_type, [])
    rename_map, merge_targets = make_rename_map(rename_rules)
    intro, raw_sections = split_sections(body)
    if not raw_sections:
        return False, []

    normalized_sections, changes = normalize_and_merge_sections(raw_sections, rename_map, merge_targets)
    reordered_sections, reordered = reorder_sections(normalized_sections, section_schema)
    if reordered:
        changes.append("reorder sections")
    if not changes:
        return False, []

    new_body = rebuild_body(intro, reordered_sections)
    final = f"---\n{raw_frontmatter}\n---\n{new_body}" if raw_frontmatter else new_body
    if not dry_run:
        path.write_text(final, encoding="utf-8")
    return True, changes


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize note section headings and order against the local schema.")
    parser.add_argument("--vault", help="Knowledge-base vault path. Falls back to KB_VAULT_PATH or .knowledge-base.local.json")
    parser.add_argument("--schema-dir", help="Schema directory. Defaults to repo_root()/schema")
    parser.add_argument("--write", action="store_true", help="Write changes back to the vault. Default is dry-run.")
    parser.add_argument("--relative-path", help="Normalize only one note relative to the vault root.")
    args = parser.parse_args()

    vault = resolve_vault_path(args.vault)
    schema_dir = Path(args.schema_dir).resolve() if args.schema_dir else repo_root() / "schema"
    schema = load_schema(schema_dir)

    if args.relative_path:
        files = [vault / args.relative_path]
    else:
        files = sorted(file_path for file_path in vault.rglob("*.md") if not is_ignored_note_path(file_path, vault))

    changed = 0
    scanned = 0
    for file_path in files:
        if not file_path.exists():
            print(f"skip missing: {file_path}")
            continue
        scanned += 1
        touched, changes = process_file(file_path, schema, dry_run=not args.write)
        if touched:
            changed += 1
            rel_path = file_path.relative_to(vault).as_posix()
            print(f"{rel_path}: {'; '.join(changes)}")

    print(f"scanned={scanned}")
    print(f"changed={changed}")
    print(f"write={args.write}")


if __name__ == "__main__":
    main()
