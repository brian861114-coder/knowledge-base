#!/usr/bin/env python3
"""一鍵執行所有匯出與驗證。

Usage:
  python tools/run_exports.py --vault /path/to/vault     # 完整流程
  python tools/run_exports.py --vault /path/to/vault --skip-validate  # 僅匯出
  python tools/run_exports.py --vault /path/to/vault --out-dir ./docs  # 輸出到特定目錄
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from kb_config import TEMPLATE_ROOT, resolve_vault_path


def run_step(command: list[str], label: str) -> None:
    print(f"[run] {label}", flush=True)
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run both exports and validation in one command.")
    parser.add_argument("--vault", help="Knowledge-base vault path.")
    parser.add_argument("--out-dir", default=None, help="Output directory (default: repo root)")
    parser.add_argument("--skip-validate", action="store_true", help="Run exports only")
    args = parser.parse_args()

    repo = TEMPLATE_ROOT
    vault = resolve_vault_path(args.vault)
    out_dir = Path(args.out_dir) if args.out_dir else repo
    out_dir.mkdir(parents=True, exist_ok=True)
    python_exe = sys.executable

    run_step(
        [python_exe, str(repo / "tools" / "export_note_details.py"),
         "--vault", str(vault), "--out", str(out_dir / "note_details.json")],
        "export note details",
    )
    run_step(
        [python_exe, str(repo / "tools" / "export_graph.py"),
         "--vault", str(vault), "--out", str(out_dir / "graph.json")],
        "export graph",
    )

    if not args.skip_validate:
        run_step(
            [python_exe, str(repo / "tools" / "validate.py"),
             "--vault", str(vault),
             "--graph", str(out_dir / "graph.json"),
             "--details", str(out_dir / "note_details.json")],
            "validate exports",
        )

    print("\nDone.")


if __name__ == "__main__":
    main()
