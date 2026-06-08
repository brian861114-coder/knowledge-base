#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from apply_weak_model_response import (
    apply_response_to_text,
    load_json,
    load_schema,
    make_rename_map,
    parse_frontmatter,
    resolve_note_path,
    validate_task_response,
)
from kb_paths import repo_root, resolve_vault_path


def gather_task_files(task_dir: Path) -> list[Path]:
    return sorted(path for path in task_dir.glob("*.json") if path.name != "manifest.json")


def map_response_files(response_dir: Path) -> dict[str, Path]:
    return {path.name: path for path in sorted(response_dir.glob("*.json"))}


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply a batch of weak-model JSON responses to note sections.")
    parser.add_argument("--task-dir", required=True, help="Directory of task JSON files")
    parser.add_argument("--response-dir", required=True, help="Directory of response JSON files, one per task filename")
    parser.add_argument("--vault", help="Knowledge-base vault path. Falls back to KB_VAULT_PATH or .knowledge-base.local.json")
    parser.add_argument("--schema-dir", help="Schema directory. Defaults to repo_root()/schema")
    parser.add_argument("--write", action="store_true", help="Write changes back. Default is dry-run.")
    parser.add_argument("--report-out", help="Optional JSON report output path")
    args = parser.parse_args()

    repo = repo_root()
    vault = resolve_vault_path(args.vault)
    schema_dir = Path(args.schema_dir).resolve() if args.schema_dir else repo / "schema"
    schema = load_schema(schema_dir)

    task_dir = Path(args.task_dir).resolve()
    response_dir = Path(args.response_dir).resolve()
    if not task_dir.exists():
        raise SystemExit(f"Task directory does not exist: {task_dir}")
    if not response_dir.exists():
        raise SystemExit(f"Response directory does not exist: {response_dir}")

    task_files = gather_task_files(task_dir)
    response_map = map_response_files(response_dir)

    applied: list[dict] = []
    skipped: list[dict] = []
    failed: list[dict] = []

    for task_file in task_files:
        response_file = response_map.get(task_file.name)
        if response_file is None:
            skipped.append({"task": task_file.name, "reason": "missing_response_file"})
            continue

        try:
            task = load_json(task_file)
            response = load_json(response_file)
            if response.get("status") == "blocked":
                skipped.append(
                    {
                        "task": task_file.name,
                        "response": response_file.name,
                        "reason": "blocked",
                    }
                )
                continue

            validate_task_response(task, response)

            note_path = resolve_note_path(task, vault, None)
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

            applied.append(
                {
                    "task": task_file.name,
                    "response": response_file.name,
                    "note_path": str(task["note_path"]),
                    "note_type": note_type,
                    "matched_heading": matched_heading,
                    "write": args.write,
                }
            )
        except BaseException as exc:
            failed.append(
                {
                    "task": task_file.name,
                    "response": response_file.name,
                    "error": str(exc),
                }
            )

    report = {
        "task_dir": str(task_dir),
        "response_dir": str(response_dir),
        "vault": str(vault),
        "write": args.write,
        "task_count": len(task_files),
        "applied_count": len(applied),
        "skipped_count": len(skipped),
        "failed_count": len(failed),
        "applied": applied,
        "skipped": skipped,
        "failed": failed,
    }

    if args.report_out:
        Path(args.report_out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Weak-model batch apply summary")
    print(f"- task dir: {task_dir}")
    print(f"- response dir: {response_dir}")
    print(f"- vault: {vault}")
    print(f"- write: {args.write}")
    print(f"- tasks: {len(task_files)}")
    print(f"- applied: {len(applied)}")
    print(f"- skipped: {len(skipped)}")
    print(f"- failed: {len(failed)}")

    if skipped:
        print("- skipped tasks:")
        for item in skipped[:20]:
            print(f"  - {item['task']}: {item['reason']}")

    if failed:
        print("- failed tasks:")
        for item in failed[:20]:
            print(f"  - {item['task']}: {item['error']}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
