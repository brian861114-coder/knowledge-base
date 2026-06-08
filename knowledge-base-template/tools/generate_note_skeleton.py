#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_paths import repo_root, resolve_vault_path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema(schema_dir: Path) -> tuple[dict, dict]:
    return load_json(schema_dir / "note_types.yaml"), load_json(schema_dir / "sections.yaml")


def find_type_entry(note_types: dict, note_type: str) -> dict:
    for entry in note_types.get("types", []):
        if str(entry.get("id", "")).strip() == note_type:
            return entry
    raise SystemExit(f"Unknown note type: {note_type}")


def domain_required_types(note_types: dict) -> set[str]:
    required = note_types.get("required_frontmatter", {})
    return set(required.get("require_domain_for", []))


def build_frontmatter(*, title: str, note_type: str, summary: str, domain: str | None, note_types: dict) -> str:
    lines = [
        "---",
        f'title: "{title}"',
        f"type: {note_type}",
        f'summary: "{summary}"',
    ]
    if note_type in domain_required_types(note_types):
        lines.append(f'domain: "{domain or ""}"')
    lines.append("---")
    return "\n".join(lines)


def render_section(heading: str) -> str:
    return f"## {heading}\n\nWrite this section.\n"


def build_body(section_schema: dict, include_optional: bool) -> str:
    sections: list[str] = []
    for heading in section_schema.get("required_order", []):
        sections.append(render_section(str(heading)))
    if include_optional:
        for heading in section_schema.get("optional", []):
            sections.append(render_section(str(heading)))
    return "\n".join(sections).rstrip() + "\n"


def resolve_output_path(*, note_type: str, title: str, note_types: dict, vault: Path | None, out_dir: Path | None) -> Path:
    type_entry = find_type_entry(note_types, note_type)
    folder = str(type_entry.get("folder", "")).strip()
    filename = f"{title}.md"
    if out_dir is not None:
        return (out_dir / filename).resolve()
    if vault is not None:
        return (vault / folder / filename).resolve()
    return (repo_root() / "tmp" / "generated_note_skeletons" / folder / filename).resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a schema-first note skeleton.")
    parser.add_argument("--type", required=True, help="Note type id")
    parser.add_argument("--title", required=True, help="Note title")
    parser.add_argument("--summary", required=True, help="One-line note summary")
    parser.add_argument("--domain", help="Required for note types that demand a domain")
    parser.add_argument("--schema-dir", help="Schema directory. Defaults to repo_root()/schema")
    parser.add_argument("--vault", help="Optional vault path; if omitted, no external-vault write path is assumed")
    parser.add_argument("--out-dir", help="Optional output directory override")
    parser.add_argument("--include-optional", action="store_true", help="Also render optional sections")
    parser.add_argument("--write", action="store_true", help="Write the skeleton to disk")
    args = parser.parse_args()

    repo = repo_root()
    schema_dir = Path(args.schema_dir).resolve() if args.schema_dir else repo / "schema"
    note_types, sections = load_schema(schema_dir)
    note_type = str(args.type).strip()

    if note_type in domain_required_types(note_types) and not args.domain:
        raise SystemExit(f"--domain is required for note type: {note_type}")

    section_schema = sections.get("section_schemas", {}).get(note_type)
    if not isinstance(section_schema, dict):
        raise SystemExit(f"No section schema found for note type: {note_type}")

    vault = resolve_vault_path(args.vault) if args.vault else None
    out_dir = Path(args.out_dir).resolve() if args.out_dir else None
    output_path = resolve_output_path(
        note_type=note_type,
        title=str(args.title).strip(),
        note_types=note_types,
        vault=vault,
        out_dir=out_dir,
    )

    content = (
        build_frontmatter(
            title=str(args.title).strip(),
            note_type=note_type,
            summary=str(args.summary).strip(),
            domain=args.domain.strip() if isinstance(args.domain, str) else None,
            note_types=note_types,
        )
        + "\n\n"
        + build_body(section_schema, include_optional=args.include_optional)
    )

    if args.write:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

    print("Note skeleton summary")
    print(f"- type: {note_type}")
    print(f"- title: {args.title}")
    print(f"- output: {output_path}")
    print(f"- include optional: {args.include_optional}")
    print(f"- write: {args.write}")
    if not args.write:
        print("\n--- preview ---\n")
        print(content)


if __name__ == "__main__":
    main()
