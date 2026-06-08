#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


TEMPLATE_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = TEMPLATE_ROOT / "schema"

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")
HEADING_RE = re.compile(r"^(#{2,3})\s+(.+)$", re.MULTILINE)
UNICODE_ESCAPE_RE = re.compile(r"\\u([0-9a-fA-F]{4})")


def decode_path_value(value: str) -> str:
    return UNICODE_ESCAPE_RE.sub(lambda match: chr(int(match.group(1), 16)), value)


def load_json_or_yaml(path: Path) -> Any:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                f"{path} is not valid JSON, and PyYAML is not installed for YAML parsing."
            ) from exc
        return yaml.safe_load(text)


def load_local_config(config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or TEMPLATE_ROOT / ".knowledge-base.local.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("vaultPath", "vault_path", "pythonPath", "python_path", "outDir", "out_dir"):
        value = data.get(key)
        if isinstance(value, str):
            data[key] = decode_path_value(value)
    return data


def resolve_vault_path(override: str | None = None) -> Path:
    if override:
        return Path(override).expanduser().resolve()

    env_path = os.environ.get("KB_VAULT_PATH")
    if env_path:
        return Path(decode_path_value(env_path)).expanduser().resolve()

    config = load_local_config()
    for key in ("vaultPath", "vault_path"):
        value = config.get(key)
        if isinstance(value, str) and value.strip():
            return Path(value).expanduser().resolve()

    raise SystemExit(
        "Vault path not configured. Pass --vault, set KB_VAULT_PATH, or define it in .knowledge-base.local.json."
    )


def load_note_types_config() -> dict[str, Any]:
    return load_json_or_yaml(SCHEMA_DIR / "note_types.yaml")


def load_note_types() -> list[dict[str, Any]]:
    data = load_note_types_config()
    return list(data.get("types", []))


def load_domains_config() -> dict[str, Any]:
    return load_json_or_yaml(SCHEMA_DIR / "domains.yaml")


def load_taxonomy_domains() -> list[dict[str, Any]]:
    data = load_domains_config()
    return list(data.get("taxonomy_domains", []))


def load_domains() -> list[dict[str, Any]]:
    data = load_domains_config()
    return list(data.get("domains", []))


def load_sections_config() -> dict[str, Any]:
    return load_json_or_yaml(SCHEMA_DIR / "sections.yaml")


def load_section_schemas() -> dict[str, dict[str, Any]]:
    data = load_sections_config()
    return dict(data.get("section_schemas", {}))


def load_renaming_rules() -> dict[str, Any]:
    return load_json_or_yaml(SCHEMA_DIR / "renaming_rules.yaml")


def load_content_rules() -> dict[str, Any]:
    return load_json_or_yaml(SCHEMA_DIR / "content_rules.yaml")


def relation_fields() -> list[str]:
    data = load_note_types_config()
    return list(data.get("relation_fields", []))


def base_required_fields() -> list[str]:
    data = load_note_types_config()
    required = data.get("required_frontmatter", {})
    return list(required.get("base", []))


def require_domain_for() -> set[str]:
    data = load_note_types_config()
    required = data.get("required_frontmatter", {})
    return set(required.get("require_domain_for", []))


def get_type_label(type_id: str) -> str:
    for entry in load_note_types():
        if str(entry.get("id", "")).strip() == type_id:
            return str(entry.get("label", type_id))
    return type_id


def get_type_folder(type_id: str) -> str:
    for entry in load_note_types():
        if str(entry.get("id", "")).strip() == type_id:
            return str(entry.get("folder", type_id))
    return type_id


def parse_frontmatter(text: str) -> tuple[str, str]:
    text = text.lstrip("\ufeff")
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 5 :]


def parse_frontmatter_data(raw: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
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
    return data


def note_id_from_path(path: Path) -> str:
    return path.stem.strip().replace(" ", "-")


def clean_text(value: str) -> str:
    value = re.sub(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), value)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = re.sub(r"\*([^*]+)\*", r"\1", value)
    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"^\s*[-*]\s+", "", value, flags=re.MULTILINE)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def extract_links(body: str) -> list[str]:
    return [match.group(1).strip() for match in WIKILINK_RE.finditer(body)]


def extract_sections(body: str) -> list[dict[str, Any]]:
    matches = list(HEADING_RE.finditer(body))
    sections: list[dict[str, Any]] = []
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
                "content": content,
            }
        )
    return sections


def normalize_target(value: str) -> str:
    return value.strip().lower().replace(" ", "-")
