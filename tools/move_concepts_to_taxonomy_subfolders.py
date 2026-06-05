#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from kb_paths import resolve_vault_path


TARGET_DOMAINS = {"analytical_dynamics", "modern_physics", "thermo_fluids"}


def parse_frontmatter(text: str) -> dict[str, str]:
    text = text.lstrip("\ufeff")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    raw = text[4:end]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Move concept notes into taxonomy-based subfolders.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned moves without writing")
    args = parser.parse_args()

    vault = resolve_vault_path()
    concept_dir = vault / "02_concepts"
    moves: list[tuple[Path, Path, str]] = []

    for source in sorted(concept_dir.glob("*.md")):
        text = source.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        domain = frontmatter.get("taxonomy_domain", "")
        if domain not in TARGET_DOMAINS:
            continue
        target = concept_dir / domain / source.name
        moves.append((source, target, domain))

    for source, target, domain in moves:
        print(f"{domain}\t{source.name}\t->\t{target.relative_to(vault).as_posix()}")
        if args.dry_run:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        source.replace(target)

    print(f"moves={len(moves)} dry_run={args.dry_run}")


if __name__ == "__main__":
    main()
