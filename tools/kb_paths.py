#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from pathlib import Path


UNICODE_ESCAPE_RE = re.compile(r"\\u([0-9a-fA-F]{4})")


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def is_ignored_note_path(path: Path, vault_root: Path) -> bool:
    try:
        parts = path.relative_to(vault_root).parts
    except ValueError:
        parts = path.parts
    return any(part.startswith("_bak") for part in parts)


def decode_path_value(value: str) -> str:
    return UNICODE_ESCAPE_RE.sub(lambda match: chr(int(match.group(1), 16)), value)


def load_local_config(config_path: Path | None = None) -> dict:
    path = config_path or repo_root() / ".knowledge-base.local.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("pythonPath", "vaultPath"):
        value = data.get(key)
        if isinstance(value, str):
            data[key] = decode_path_value(value)
    return data


def resolve_vault_path(cli_value: str | None = None, config_path: Path | None = None) -> Path:
    if cli_value:
        return Path(cli_value).expanduser().resolve()
    env_value = os.environ.get("KB_VAULT_PATH")
    if env_value:
        return Path(decode_path_value(env_value)).expanduser().resolve()
    config = load_local_config(config_path)
    config_value = config.get("vaultPath")
    if isinstance(config_value, str) and config_value.strip():
        return Path(config_value).expanduser().resolve()
    raise FileNotFoundError(
        "Vault path not configured. Pass --vault, set KB_VAULT_PATH, or define vaultPath in .knowledge-base.local.json."
    )
