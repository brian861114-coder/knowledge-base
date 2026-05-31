#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


HEADING_RE = re.compile(r"^(#{2,3})\s+(.+)$", re.MULTILINE)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data = {}
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


def slugify_path(path: Path) -> str:
    return path.stem.strip().lower().replace(" ", "-")


def clean_text(value: str) -> str:
    value = re.sub(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), value)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = re.sub(r"\*([^*]+)\*", r"\1", value)
    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"^\s*[-*]\s+", "", value, flags=re.MULTILINE)
    value = re.sub(r"\n{2,}", "\n\n", value)
    return value.strip()


def extract_sections(body: str) -> list[dict]:
    matches = list(HEADING_RE.finditer(body))
    sections = []
    for index, match in enumerate(matches):
      level = len(match.group(1))
      title = match.group(2).strip()
      start = match.end()
      end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
      content = clean_text(body[start:end])
      if not content:
          continue
      sections.append(
          {
              "title": title,
              "level": level,
              "preview": content[:380],
          }
      )
    return sections


def build_details(vault: Path) -> dict:
    payload = {}
    for file_path in sorted(vault.rglob("*.md")):
        text = file_path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(text)
        node_id = slugify_path(file_path)
        cleaned_body = clean_text(body)
        payload[node_id] = {
            "path": file_path.relative_to(vault).as_posix(),
            "title": frontmatter.get("title", file_path.stem),
            "summary": frontmatter.get("summary", ""),
            "body_preview": cleaned_body[:900],
            "sections": extract_sections(body),
        }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Export note detail previews from an Obsidian vault.")
    parser.add_argument("--vault", required=True, help="Vault root path")
    parser.add_argument("--out", required=True, help="Output JSON path")
    args = parser.parse_args()

    vault = Path(args.vault).resolve()
    out = Path(args.out).resolve()
    payload = build_details(vault)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported {len(payload)} note details to {out}")


if __name__ == "__main__":
    main()
