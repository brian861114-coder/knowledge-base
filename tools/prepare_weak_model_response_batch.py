#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_paths import repo_root


def gather_task_files(task_dir: Path) -> list[Path]:
    return sorted(path for path in task_dir.glob("*.json") if path.name != "manifest.json")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare an empty batch_responses directory and a todo checklist for weak-model output files.")
    parser.add_argument("--task-dir", required=True, help="Directory containing task JSON files")
    parser.add_argument("--response-dir", help="Response directory to create. Defaults to batch_responses/<relative task path under batch_tasks>")
    args = parser.parse_args()

    repo = repo_root()
    task_dir = Path(args.task_dir).resolve()
    if not task_dir.exists():
        raise SystemExit(f"Task directory does not exist: {task_dir}")

    batch_tasks_root = (repo / "batch_tasks").resolve()
    batch_responses_root = (repo / "batch_responses").resolve()

    if args.response_dir:
        response_dir = Path(args.response_dir).resolve()
    else:
        try:
            relative = task_dir.relative_to(batch_tasks_root)
        except ValueError:
            relative = Path(task_dir.name)
        response_dir = batch_responses_root / relative

    ensure_dir(response_dir)

    task_files = gather_task_files(task_dir)
    task_manifest_path = task_dir / "manifest.json"
    task_manifest = load_json(task_manifest_path) if task_manifest_path.exists() else {}

    todo_items: list[dict] = []
    for task_file in task_files:
        response_path = response_dir / task_file.name
        todo_items.append(
            {
                "task_file": task_file.name,
                "response_file": response_path.name,
                "status": "pending",
            }
        )

    todo_manifest = {
        "task_dir": str(task_dir),
        "response_dir": str(response_dir),
        "task_count": len(task_files),
        "task_manifest": task_manifest,
        "items": todo_items,
        "instructions": {
            "one_response_per_task": True,
            "matching_filenames_required": True,
            "blocked_tasks_must_still_emit_json": True,
        },
    }

    (response_dir / "todo_manifest.json").write_text(
        json.dumps(todo_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    checklist_lines = [
        "# DeepSeek Batch Response TODO",
        "",
        f"- task dir: `{task_dir}`",
        f"- response dir: `{response_dir}`",
        f"- task count: `{len(task_files)}`",
        "",
        "## Required rules",
        "",
        "- One response JSON per task JSON.",
        "- Response filename must exactly match task filename.",
        "- If blocked, still write a JSON file with `status: \"blocked\"`.",
        "- Do not mix response files into the task directory.",
        "",
        "## Pending files",
        "",
    ]
    for item in todo_items:
        checklist_lines.append(f"- [ ] {item['task_file']}")
    checklist_lines.append("")

    (response_dir / "TODO.md").write_text("\n".join(checklist_lines), encoding="utf-8")

    print("Prepared weak-model response batch")
    print(f"- task dir: {task_dir}")
    print(f"- response dir: {response_dir}")
    print(f"- task count: {len(task_files)}")
    print(f"- todo manifest: {response_dir / 'todo_manifest.json'}")
    print(f"- checklist: {response_dir / 'TODO.md'}")


if __name__ == "__main__":
    main()
