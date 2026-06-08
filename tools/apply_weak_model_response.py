#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

from kb_paths import repo_root, resolve_vault_path


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class SectionSpan:
    heading: str
    canonical_heading: str
    start: int
    heading_end: int
    content_start: int
    content_end: int


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def load_schema(schema_dir: Path) -> dict:
    return {
        "renames": load_json(schema_dir / "renaming_rules.yaml"),
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


def split_section_spans(body: str, rename_map: dict[str, str]) -> list[SectionSpan]:
    matches = list(SECTION_RE.finditer(body))
    spans: list[SectionSpan] = []
    for index, match in enumerate(matches):
        raw_heading = match.group(1).strip()
        canonical_heading = rename_map.get(raw_heading, raw_heading)
        content_start = match.end()
        content_end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        spans.append(
            SectionSpan(
                heading=raw_heading,
                canonical_heading=canonical_heading,
                start=match.start(),
                heading_end=match.end(),
                content_start=content_start,
                content_end=content_end,
            )
        )
    return spans


def normalize_section_body(text: str) -> str:
    cleaned = text.replace("\r\n", "\n").strip("\n")
    return "\n" + cleaned + "\n\n"


def validate_task_response(task: dict, response: dict) -> None:
    if response.get("status") != "ok":
        raise SystemExit(f"Response status is not ok: {response.get('status')!r}")

    for key in ("note_path", "target_section", "issue_category"):
        task_value = task.get(key)
        response_value = response.get(key)
        if task_value != response_value:
            raise SystemExit(f"Task/response mismatch for {key}: {task_value!r} != {response_value!r}")

    content = response.get("content")
    if not isinstance(content, str) or not content.strip():
        raise SystemExit("Response content is empty.")

    if re.search(r"^##\s+", content, re.MULTILINE):
        raise SystemExit("Response content must not contain level-2 headings.")


def apply_response_to_text(text: str, note_type: str, target_section: str, replacement_body: str, rename_map: dict[str, str]) -> tuple[str, str]:
    _frontmatter, body = parse_frontmatter(text)
    spans = split_section_spans(body, rename_map)
    target_canonical = rename_map.get(target_section, target_section)

    selected: SectionSpan | None = None
    for span in spans:
        if span.canonical_heading == target_canonical:
            selected = span
            break

    if selected is None:
        raise SystemExit(f"Target section not found in note: {target_section}")

    replacement = normalize_section_body(replacement_body)
    new_body = body[: selected.content_start] + replacement + body[selected.content_end :]

    if text.lstrip("\ufeff").startswith("---\n"):
        raw_end = text.find("\n---\n", 4)
        prefix = text[: raw_end + 5]
        return prefix + new_body, selected.heading
    return new_body, selected.heading


def resolve_note_path(task: dict, vault: Path, note_path_override: str | None) -> Path:
    relative = note_path_override or str(task["note_path"])
    return (vault / relative).resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply a weak-model JSON response to one note section.")
    parser.add_argument("--task", required=True, help="Task JSON path")
    parser.add_argument("--response", required=True, help="Weak-model response JSON path")
    parser.add_argument("--vault", help="Knowledge-base vault path. Falls back to KB_VAULT_PATH or .knowledge-base.local.json")
    parser.add_argument("--schema-dir", help="Schema directory. Defaults to repo_root()/schema")
    parser.add_argument("--note-path", help="Override note path relative to vault, useful for workspace testing")
    parser.add_argument("--write", action="store_true", help="Write changes back. Default is dry-run.")
    args = parser.parse_args()

    repo = repo_root()
    vault = resolve_vault_path(args.vault)
    schema_dir = Path(args.schema_dir).resolve() if args.schema_dir else repo / "schema"
    schema = load_schema(schema_dir)

    task = load_json(Path(args.task).resolve())
    response = load_json(Path(args.response).resolve())
    validate_task_response(task, response)

    note_path = resolve_note_path(task, vault, args.note_path)
    if not note_path.exists():
        raise SystemExit(f"Note path does not exist: {note_path}")

    text = note_path.read_text(encoding="utf-8")
    frontmatter, _body = parse_frontmatter(text)
    note_type = str(frontmatter.get("type", "")).strip()
    if note_type != str(task.get("note_type", "")).strip():
        raise SystemExit(f"Task note_type does not match note frontmatter: {task.get('note_type')!r} != {note_type!r}")

    rename_rules = schema["renames"]["rename_rules"].get(note_type, [])
    rename_map = make_rename_map(rename_rules)
    updated_text, matched_heading = apply_response_to_text(
        text,
        note_type=note_type,
        target_section=str(task["target_section"]),
        replacement_body=str(response["content"]),
        rename_map=rename_map,
    )

    if args.write:
        note_path.write_text(updated_text, encoding="utf-8")

    print("Weak-model response apply summary")
    print(f"- task: {Path(args.task).resolve()}")
    print(f"- response: {Path(args.response).resolve()}")
    print(f"- note: {note_path}")
    print(f"- note type: {note_type}")
    print(f"- target section: {task['target_section']}")
    print(f"- matched heading: {matched_heading}")
    print(f"- write: {args.write}")


if __name__ == "__main__":
    main()
