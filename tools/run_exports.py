#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys

from kb_paths import repo_root, resolve_vault_path


def run_step(command: list[str], label: str) -> None:
    print(f"[run] {label}", flush=True)
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run both exports and validation in one command.")
    parser.add_argument("--vault", help="Knowledge-base vault path. Falls back to KB_VAULT_PATH or .knowledge-base.local.json")
    parser.add_argument("--skip-validate", action="store_true", help="Run exports only")
    args = parser.parse_args()

    repo = repo_root()
    vault = resolve_vault_path(args.vault)
    python_exe = sys.executable

    run_step(
        [
            python_exe,
            str(repo / "tools" / "export_note_details.py"),
            "--vault",
            str(vault),
            "--out",
            str(repo / "physics_note_details.json"),
        ],
        "export note details",
    )
    run_step(
        [
            python_exe,
            str(repo / "obsidian-knowledge-map-demo" / "scripts" / "export_graph.py"),
            "--vault",
            str(vault),
            "--out",
            str(repo / "physics_graph.json"),
        ],
        "export graph",
    )

    if not args.skip_validate:
        run_step(
            [
                python_exe,
                str(repo / "tools" / "validate_knowledge_base.py"),
                "--vault",
                str(vault),
            ],
            "validate exports",
        )

    print("\nDone.")


if __name__ == "__main__":
    main()
