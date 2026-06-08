#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a human-readable checklist for blocked weak-model tasks.")
    parser.add_argument("--apply-report", required=True, help="Path to an apply_weak_model_batch report JSON")
    parser.add_argument("--task-dir", required=True, help="Directory containing the task JSON files")
    parser.add_argument("--response-dir", required=True, help="Directory containing the response JSON files")
    parser.add_argument("--out", required=True, help="Markdown output path")
    args = parser.parse_args()

    report = load_json(Path(args.apply_report).resolve())
    task_dir = Path(args.task_dir).resolve()
    response_dir = Path(args.response_dir).resolve()
    skipped = report.get("skipped", [])

    lines = [
        "# Blocked Manual Review Checklist",
        "",
        f"- apply report: `{Path(args.apply_report).resolve()}`",
        f"- task dir: `{task_dir}`",
        f"- response dir: `{response_dir}`",
        f"- blocked count: `{len(skipped)}`",
        "",
        "These notes were not applied because the weak-model response returned `status: \"blocked\"`.",
        "They need manual review or a stronger model with better context.",
        "",
        "## Items",
        "",
    ]

    for item in skipped:
        task_name = str(item["task"])
        task_path = task_dir / task_name
        response_path = response_dir / str(item["response"])
        task = load_json(task_path)
        response = load_json(response_path)
        lines.append(f"### {task_name}")
        lines.append(f"- note path: `{task.get('note_path', '')}`")
        lines.append(f"- note type: `{task.get('note_type', '')}`")
        lines.append(f"- target section: `{task.get('target_section', '')}`")
        lines.append(f"- issue category: `{task.get('issue_category', '')}`")
        lines.append(f"- reason: `{item.get('reason', '')}`")
        rationale = response.get("rationale", [])
        if rationale:
            lines.append("- model rationale:")
            for entry in rationale:
                lines.append(f"  - {entry}")
        known_links = task.get("source_context", {}).get("known_links", [])
        if known_links:
            lines.append("- known links:")
            for link in known_links:
                lines.append(f"  - `{link}`")
        section_text = task.get("source_context", {}).get("sections", {}).get(task.get("target_section", ""), "")
        if section_text:
            lines.append("- current section excerpt:")
            lines.append("")
            lines.append("```md")
            lines.append(section_text[:1200])
            lines.append("```")
        lines.append("")

    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote blocked review checklist to {Path(args.out).resolve()}")


if __name__ == "__main__":
    main()
