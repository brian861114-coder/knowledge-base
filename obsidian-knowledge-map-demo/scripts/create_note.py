#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def slugify(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a page from a bundled template.")
    parser.add_argument("--type", required=True, help="Page type name, such as law or concept")
    parser.add_argument("--title", required=True, help="Human-readable page title")
    parser.add_argument("--out", required=True, help="Output markdown path")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    template_path = skill_root / "assets" / "templates" / f"{args.type}.md"
    if not template_path.exists():
        raise SystemExit(f"Unknown template type: {args.type}")

    output_path = Path(args.out).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    text = template_path.read_text(encoding="utf-8")
    text = text.replace("{{title}}", args.title)
    if "title:" in text:
        text = text.replace("title:\n", f"title: {args.title}\n", 1)
    if "updated:" in text:
        text = text.replace("updated:\n", "updated: YYYY-MM-DD\n", 1)

    output_path.write_text(text, encoding="utf-8")
    print(f"Created {args.type} page at {output_path}")


if __name__ == "__main__":
    main()
