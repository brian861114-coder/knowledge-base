#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from kb_config import TEMPLATE_ROOT

ENGLISH_SOURCE_REF = "4ee49f9"
SOURCE_FILES = {
    "graph_en.json": "materials-science-engineering-kb/prototype/graph.json",
    "note_details_en.json": "materials-science-engineering-kb/prototype/note_details.json",
}


def read_file_from_git(ref: str, repo_root: Path, git_path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{ref}:{git_path}"],
        cwd=repo_root,
        text=True,
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Export English graph/note snapshots from git history.")
    parser.add_argument("--out-dir", required=True, help="Output directory for graph_en.json and note_details_en.json")
    parser.add_argument("--ref", default=ENGLISH_SOURCE_REF, help="Git ref containing the English snapshot")
    args = parser.parse_args()

    repo_root = TEMPLATE_ROOT.parent
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for output_name, git_path in SOURCE_FILES.items():
        content = read_file_from_git(args.ref, repo_root, git_path)
        destination = out_dir / output_name
        destination.write_text(content, encoding="utf-8")
        print(f"Exported English snapshot {output_name} to {destination}")


if __name__ == "__main__":
    main()
