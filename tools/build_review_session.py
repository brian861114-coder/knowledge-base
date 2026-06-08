#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from kb_paths import repo_root, resolve_vault_path
from validate_knowledge_base import parse_frontmatter

SUMMARY_REVISIONS = {
    "自然對數": "自然對數 $\\ln(x)$ 是以 $e$ 為底的對數函數，定義在 $x > 0$，並且是指數函數 $e^x$ 的反函數。它在物理上的價值是把乘法、倍數與指數衰減關係轉成可加且可線性擬合的形式，因此常出現在熵、Arrhenius 分析、RC 電路與放射性衰變。",
    "指數函數": "指數函數 $e^x$ 是滿足 $\\frac{d}{dx}e^x = e^x$ 的函數，也是微分方程 $\\frac{dy}{dt}=ky$ 的標準解型。只要系統的變化率與當前量成正比，解就會呈現指數成長、衰減或複指數振盪，因此它貫穿 RC 電路、阻尼、放射性衰變與波動問題。",
    "泰勒展開": "泰勒展開是在展開點 $a$ 附近，用函數各階導數構造多項式來近似函數的方法。物理上它的作用是把非線性問題局部線性化或低階化，讓小角度近似、平衡點振動、誤差估計與微擾計算變成可控的近似問題。",
}

TOOLS_SUMMARY_REVISIONS = {
    "自然對數": r"""$\ln(x)$ 是以 $e$ 為底的對數函數，定義域 $x > 0$，同時也是 [[指數函數]] 的反函數。它在物理中最核心的功能是把乘法與倍數關係轉成加法與差值，讓指數成長、衰減與跨數量級的資料變得可以線性分析。

實際應用中，$\ln$ 常常不是拿來「算一個數」，而是拿來把模型變直。像是 $N(t)=N_0 e^{-t/\tau}$ 這類衰減律，取對數後變成線性關係，斜率直接對應時間常數或活化能。[[熵]] 的定義、Arrhenius 圖、RC 充放電分析都依賴這個轉換。

---""",
    "指數函數": r"""$e^x$ 的定義性質是它等於自己的導數：$\frac{d}{dx}e^x = e^x$。對時間演化問題而言，滿足 $\frac{dy}{dt}=ky$ 的系統，解一律寫成 $y(t)=y_0 e^{kt}$——$k<0$ 是衰減，$k>0$ 是成長，$k=i\omega$ 則連到振盪與波動的複指數表示。

這個結構在物理中反覆出現：[[RC電路]] 的充放電、放射性衰變、[[阻尼振動]] 的振幅包絡、[[機械波]] 的複數表示，底層都是同一個函數。

---""",
    "泰勒展開": r"""泰勒展開的核心不在「展開成無限級數」，而在**截斷後得到的低階模型**。在展開點 $a$ 附近，保留到一階就是局部線性化，保留到二階就能描述平衡點附近的曲率與穩定性。

物理上大量問題的第一步就是這個截斷：小角度近似 $\sin\theta \approx \theta$ 是一階，位能井附近的 [[簡諧運動]] 是二階，誤差傳播的一階敏感度分析也是。沒有這個工具，很多非線性問題根本沒有乾淨的起手式。

---""",
}

TOOL_SUMMARY_SECTION_RE = re.compile(r"(?ms)(^##\s+工具摘要\s*\n)(.*?)(?=^##\s+|\Z)")


def format_scalar(value: str) -> str:
    if value == "":
        return '""'
    needs_quotes = any(char in value for char in [":", "[", "]", "{", "}", "#", '"', "'", "\n"])
    if value.startswith((" ", "-", "?", "@", "!", "&", "*")):
        needs_quotes = True
    if not needs_quotes:
        return value
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'


def dump_frontmatter(frontmatter: dict) -> str:
    lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {format_scalar(str(item))}")
        elif value is None:
            lines.append(f"{key}:")
        else:
            lines.append(f"{key}: {format_scalar(str(value))}")
    lines.append("---")
    return "\n".join(lines)


def compose_markdown(frontmatter: dict, body: str) -> str:
    return f"{dump_frontmatter(frontmatter)}\n{body.lstrip()}"


def replace_tool_summary(body: str, replacement: str) -> str:
    match = TOOL_SUMMARY_SECTION_RE.search(body)
    if not match:
        raise ValueError("Could not locate 工具摘要 section")
    replacement_block = f"{match.group(1)}{replacement.strip()}\n\n"
    return TOOL_SUMMARY_SECTION_RE.sub(lambda _: replacement_block, body, count=1)


def build_item(note_path: Path, vault: Path, report_dir: Path) -> dict:
    raw_markdown = note_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(raw_markdown)
    title = str(frontmatter.get("title", note_path.stem)).strip()

    if title not in SUMMARY_REVISIONS or title not in TOOLS_SUMMARY_REVISIONS:
        raise KeyError(f"No pilot candidate revision configured for {title}")

    report_path = report_dir / f"{title}.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    proposed_frontmatter = dict(frontmatter)
    proposed_frontmatter["summary"] = SUMMARY_REVISIONS[title]
    proposed_body = replace_tool_summary(body, TOOLS_SUMMARY_REVISIONS[title])

    selected_page = report.get("wikipedia_evidence", {})
    return {
        "item_id": note_path.stem,
        "note_title": title,
        "note_path": note_path.relative_to(vault).as_posix(),
        "original_frontmatter": frontmatter,
        "original_body": body,
        "original_markdown": raw_markdown,
        "proposed_frontmatter": proposed_frontmatter,
        "proposed_body": proposed_body,
        "proposed_markdown": compose_markdown(proposed_frontmatter, proposed_body),
        "change_summary": [
            "Sharpened frontmatter summary into a definition-first description.",
            "Rewrote the 工具摘要 section to state the mathematical identity and physical role more concretely.",
            "Wrapped mathematical expressions in valid TeX delimiters for review rendering.",
            "Left the rest of the note unchanged for a low-risk pilot review.",
        ],
        "source_metadata": {
            "wikipedia_title": selected_page.get("title"),
            "wikipedia_lang": selected_page.get("lang"),
            "wikipedia_revision_id": selected_page.get("revision_id"),
            "wikipedia_url": selected_page.get("full_url") or selected_page.get("canonical_url"),
            "report_path": report_path.relative_to(repo_root()).as_posix(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a manual-review session for pilot note revisions.")
    parser.add_argument(
        "--titles",
        nargs="+",
        default=["自然對數", "指數函數", "泰勒展開"],
        help="Note titles to include in the session.",
    )
    parser.add_argument(
        "--report-dir",
        default=str(repo_root() / "tmp" / "wikipedia_enrichment"),
        help="Directory containing enrichment reports.",
    )
    args = parser.parse_args()

    vault = resolve_vault_path()
    report_dir = Path(args.report_dir)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    session_id = f"wiki-pilot-{timestamp}"
    session_dir = repo_root() / "tmp" / "review_sessions" / session_id
    items_dir = session_dir / "items"
    items_dir.mkdir(parents=True, exist_ok=True)

    title_set = set(args.titles)
    matched_paths: list[Path] = []
    matched_titles: set[str] = set()
    for note_path in sorted(vault.rglob("*.md")):
        raw_markdown = note_path.read_text(encoding="utf-8")
        frontmatter, _ = parse_frontmatter(raw_markdown)
        title = str(frontmatter.get("title", note_path.stem)).strip()
        if title in title_set:
            matched_paths.append(note_path)
            matched_titles.add(title)

    missing = sorted(title_set - matched_titles)
    if missing:
        raise SystemExit(f"Missing notes for titles: {', '.join(missing)}")

    manifest_items = []
    decisions = {}
    for note_path in matched_paths:
        item = build_item(note_path, vault, report_dir)
        item_path = items_dir / f"{item['item_id']}.json"
        item_path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest_items.append(
            {
                "item_id": item["item_id"],
                "note_title": item["note_title"],
                "note_path": item["note_path"],
                "item_path": item_path.relative_to(session_dir).as_posix(),
            }
        )
        decisions[item["item_id"]] = {
            "decision": "pending",
            "updated_at": None,
        }

    manifest = {
        "session_id": session_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "session_type": "wikipedia_pilot_review",
        "candidate_scope": "low_risk_summary_and_tool_summary_only",
        "vault_path": str(vault),
        "items": manifest_items,
    }

    (session_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (session_dir / "decisions.json").write_text(
        json.dumps(decisions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(str(session_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
