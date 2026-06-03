#!/usr/bin/env python3
"""共用配置載入器。
從 schema/ 目錄讀取 YAML 配置，提供給所有工具腳本使用。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = TEMPLATE_ROOT / "schema"


def resolve_vault_path(override: str | None = None) -> Path:
    """決定 vault 路徑：CLI 參數 > 環境變數 > local config > 預設錯誤。"""
    if override:
        return Path(override)

    import os
    env_path = os.environ.get("KB_VAULT_PATH")
    if env_path:
        return Path(env_path)

    local_config = TEMPLATE_ROOT / ".knowledge-base.local.json"
    if local_config.exists():
        data = json.loads(local_config.read_text(encoding="utf-8"))
        vault = data.get("vault_path")
        if vault:
            return Path(vault)

    raise SystemExit(
        "Error: vault path not set.\n"
        "  Use --vault <path>, set KB_VAULT_PATH, or configure .knowledge-base.local.json"
    )


# ---------------------------------------------------------------------------
# YAML parsing (no dependency: manual parser for simple flat/nested YAML)
# ---------------------------------------------------------------------------

def _parse_yaml_simple(text: str) -> dict:
    """Minimal YAML parser for our schema files. Handles nested dicts and lists of dicts."""
    import yaml  # lazy import; falls back to manual if unavailable
    return yaml.safe_load(text)


def _load_yaml(path: Path) -> dict:
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except ImportError:
        # Fallback: use a very basic manual parser for our specific schema format
        return _parse_yaml_manual(path.read_text(encoding="utf-8"))


def _parse_yaml_manual(text: str) -> dict:
    """Extremely minimal YAML-ish parser. Works only for our specific schema files."""
    result: dict = {}
    current_key = None
    current_list: list | None = None
    current_dict: dict | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Top-level key with list
        if indent == 0 and stripped.endswith(":"):
            current_key = stripped[:-1].strip()
            current_list = []
            current_dict = None
            result[current_key] = current_list
            continue

        # List item
        if stripped.startswith("- ") and current_list is not None:
            item_text = stripped[2:].strip()
            if ":" in item_text:
                key, val = item_text.split(":", 1)
                current_dict = {key.strip(): val.strip().strip('"').strip("'")}
                current_list.append(current_dict)
            else:
                current_list.append(item_text)
                current_dict = None
            continue

        # Dict property under list item
        if current_dict is not None and ":" in stripped:
            key, val = stripped.split(":", 1)
            val = val.strip().strip('"').strip("'")
            if val == "true":
                val = True
            elif val == "false":
                val = False
            current_dict[key.strip()] = val

    return result


# ---------------------------------------------------------------------------
# Schema loaders
# ---------------------------------------------------------------------------

def load_note_types() -> list[dict]:
    """載入筆記類型定義。"""
    data = _load_yaml(SCHEMA_DIR / "note_types.yaml")
    return data.get("types", [])


def load_domains() -> list[dict]:
    """載入領域定義。"""
    data = _load_yaml(SCHEMA_DIR / "domains.yaml")
    return data.get("domains", [])


def load_section_schemas() -> dict[str, dict]:
    """載入 section 結構定義。"""
    data = _load_yaml(SCHEMA_DIR / "sections.yaml")
    return data.get("section_schemas", {})


def load_bridge_schemas() -> dict[str, dict]:
    """載入 bridge/method 頁面的 section 定義。"""
    data = _load_yaml(SCHEMA_DIR / "sections.yaml")
    return data.get("bridge_schemas", {})


def get_type_label(type_id: str) -> str:
    """取得 type 的顯示標籤。"""
    for t in load_note_types():
        if t.get("id") == type_id:
            return t.get("label", type_id)
    return type_id


def get_type_folder(type_id: str) -> str:
    """取得 type 對應的 Vault 子資料夾名稱。"""
    for t in load_note_types():
        if t.get("id") == type_id:
            return t.get("folder", type_id)
    return type_id


def get_type_color(type_id: str) -> str:
    """取得 type 的色彩。"""
    for t in load_note_types():
        if t.get("id") == type_id:
            return t.get("color", "#666666")
    return "#666666"


def get_domain_label(domain_id: str) -> str:
    """取得 domain 的顯示標籤。"""
    for d in load_domains():
        if d.get("id") == domain_id:
            return d.get("label", domain_id)
    return domain_id


def get_domain_description(domain_id: str) -> str:
    """取得 domain 的描述。"""
    for d in load_domains():
        if d.get("id") == domain_id:
            return d.get("description", "")
    return ""


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[str, str]:
    """分離 YAML frontmatter 與 body。回傳 (raw_frontmatter, body)。"""
    text = text.lstrip("\ufeff")
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 5:]


def parse_frontmatter_data(raw: str) -> dict[str, str]:
    """解析 frontmatter 為 dict。"""
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data


SECTION_RE = re.compile(r"^(##)\\s+(.+)$", re.MULTILINE)


def find_sections(body: str) -> list[tuple[int, str]]:
    """找到 body 中所有 ## 標題的位置與文字。"""
    return [(m.start(), m.group(2).strip()) for m in SECTION_RE.finditer(body)]


def has_section(body: str, heading: str) -> bool:
    """檢查 body 中是否已有指定的 section。"""
    return f"## {heading}" in body
