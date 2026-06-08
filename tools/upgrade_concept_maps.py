#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from kb_paths import resolve_vault_path


TARGETS = {
    "力學核心概念圖": {
        "sections": {
            "主要主題": ["骨架概念"],
            "關鍵概念": ["骨架概念", "關鍵物理量與結構"],
            "關鍵定律": ["核心定律"],
            "典型問題類型": ["典型現象與模型"],
            "建議學習順序": ["建議閱讀順序"],
            "先備知識": [],
            "與其他領域的橋接": ["同域參考"],
            "延伸方向": ["延伸方向"],
        },
        "fills": {
            "先備知識": "閱讀此圖前，最好先掌握向量、位移、速度、加速度、力與能量等最基本的物理語言，否則後面的守恆律、轉動與振動模型只會變成孤立條目而不會形成結構。",
            "與其他領域的橋接": "力學不只是獨立單元。它會向分析力學延伸出更抽象的狀態描述，也會向熱流與波動延伸出連續介質、振動與穩定性等問題，因此這張圖應被視為整個物理知識網路的基礎骨架。",
        },
    },
    "分析力學與非線性動力系統圖": {
        "sections": {
            "主要主題": ["主線一：拉格朗日語言", "主線二：哈密頓語言", "主線三：結構與對稱", "主線四：非線性與混沌"],
            "關鍵概念": ["主線一：拉格朗日語言", "主線二：哈密頓語言", "主線三：結構與對稱", "主線四：非線性與混沌"],
            "關鍵定律": ["主線三：結構與對稱"],
            "典型問題類型": ["主線四：非線性與混沌"],
            "建議學習順序": ["建議閱讀順序"],
            "先備知識": [],
            "與其他領域的橋接": ["和其他地圖的連接", "同域參考"],
            "延伸方向": [],
        },
        "fills": {
            "先備知識": "這張圖預設讀者已經熟悉牛頓力學、能量觀點、基本微分方程與相空間直觀。若沒有這些基礎，拉格朗日與哈密頓語言會只剩形式推導而失去結構意義。",
            "延伸方向": "完成這張圖之後，下一步通常是往連續系統、統計物理、量子力學的作用量與對稱語言延伸，或往非線性系統、混沌與穩定性分析做更深的動力學研究。",
        },
    },
    "振動波動與光學概念圖": {
        "sections": {
            "主要主題": ["骨架概念", "光學接口", "進階連接"],
            "關鍵概念": ["骨架概念", "光學接口"],
            "關鍵定律": [],
            "典型問題類型": ["核心現象"],
            "建議學習順序": ["建議閱讀順序"],
            "先備知識": [],
            "與其他領域的橋接": ["同域參考"],
            "延伸方向": ["延伸方向"],
        },
        "fills": {
            "關鍵定律": "- 波動與光學雖以概念圖呈現，但背後的核心約束仍包括反射與折射關係、干涉與繞射的相位條件，以及由波動方程與邊界條件導出的模式結構。閱讀這張圖時，應把這些定律視為把幾何、相位與能量傳播串起來的骨幹。",
            "先備知識": "這張圖最好建立在簡諧運動、週期、相位、向量與基本幾何光學的基礎上。否則『波』與『光』兩套語言很容易被誤讀成彼此無關的章節。",
        },
    },
    "熱學與流體概念圖": {
        "sections": {
            "主要主題": ["熱學骨架", "過程語言", "流體骨架"],
            "關鍵概念": ["熱學骨架", "流體骨架"],
            "關鍵定律": ["典型方程與應用"],
            "典型問題類型": ["典型方程與應用"],
            "建議學習順序": ["建議閱讀順序"],
            "先備知識": [],
            "與其他領域的橋接": ["同域參考"],
            "延伸方向": ["延伸方向"],
        },
        "fills": {
            "先備知識": "閱讀這張圖前，至少要熟悉能量、功、壓力、密度與基本微積分，因為熱學與流體的核心困難不在名詞，而在如何把狀態量、過程與守恆關係視為同一個結構。",
        },
    },
    "近代物理概念圖": {
        "sections": {
            "主要主題": ["主線一：相對論", "主線二：量子起點", "主線三：量子狀態語言"],
            "關鍵概念": ["主線一：相對論", "主線二：量子起點", "主線三：量子狀態語言"],
            "關鍵定律": [],
            "典型問題類型": ["典型現象"],
            "建議學習順序": ["建議閱讀順序"],
            "先備知識": [],
            "與其他領域的橋接": ["同域參考"],
            "延伸方向": ["延伸方向"],
        },
        "fills": {
            "關鍵定律": "- 近代物理的核心不是單一公式，而是少數支配框架：相對論中的時空關係與質能等價，量子論中的量子化、波函數與測量規則。這一節把它們視為整張圖背後的約束骨架，而不是零散現象的附屬說明。",
            "先備知識": "這張圖不適合完全零基礎讀者。至少要先有經典力學、波動與能量觀念，否則相對論與量子論會被誤解成只是『更怪的現象集』，而看不到它們如何修正古典框架。",
        },
    },
    "電磁學核心概念圖": {
        "sections": {
            "主要主題": ["骨架概念", "常用系統", "延伸現象"],
            "關鍵概念": ["骨架概念", "常用系統"],
            "關鍵定律": ["核心定律"],
            "典型問題類型": ["延伸現象"],
            "建議學習順序": ["建議閱讀順序"],
            "先備知識": [],
            "與其他領域的橋接": ["同域參考"],
            "延伸方向": ["延伸方向"],
        },
        "fills": {
            "先備知識": "閱讀此圖前，至少要先有向量、場的概念與基本電路語言，否則電場、磁場、通量與回路分析只會看成名詞列表，而不會形成統一的場論直觀。",
        },
    },
}

REQUIRED_ORDER = [
    "地圖摘要",
    "主要主題",
    "關鍵概念",
    "關鍵定律",
    "典型問題類型",
    "建議學習順序",
    "先備知識",
    "與其他領域的橋接",
    "延伸方向",
]


def parse_frontmatter(text: str) -> tuple[str, str]:
    text = text.lstrip("\ufeff")
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 5 :]


def parse_frontmatter_data(raw: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data


def split_sections(body: str) -> tuple[str, dict[str, str]]:
    lines = body.splitlines()
    title_lines: list[str] = []
    sections: dict[str, list[str]] = {}
    current_heading: str | None = None

    for line in lines:
        if line.startswith("## "):
            current_heading = line[3:].strip()
            sections.setdefault(current_heading, [])
            continue
        if current_heading is None:
            title_lines.append(line)
        else:
            sections[current_heading].append(line)

    rendered = {heading: "\n".join(content).strip() for heading, content in sections.items()}
    intro = "\n".join(title_lines).strip()
    return intro, rendered


def join_bodies(sections: dict[str, str], source_names: list[str]) -> str:
    chunks = [sections[name].strip() for name in source_names if sections.get(name, "").strip()]
    return "\n\n".join(chunks).strip()


def render_sections(title: str, source_sections: dict[str, str], spec: dict) -> str:
    fills = spec.get("fills", {})
    mapped = spec["sections"]
    blocks: list[str] = [f"# {title}", ""]
    for heading in REQUIRED_ORDER:
        content = ""
        if heading == "地圖摘要":
            content = source_sections.get("地圖摘要", "").strip()
        else:
            content = join_bodies(source_sections, mapped.get(heading, []))
            if fills.get(heading):
                fill = fills[heading].strip()
                content = f"{content}\n\n{fill}".strip() if content else fill
        if not content:
            content = "待補。"
        blocks.append(f"## {heading}")
        blocks.append(content)
        blocks.append("")
    return "\n".join(blocks).rstrip() + "\n"


def process_file(path: Path, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    raw_frontmatter, body = parse_frontmatter(text)
    frontmatter = parse_frontmatter_data(raw_frontmatter)
    title = frontmatter.get("title", path.stem).strip() or path.stem
    spec = TARGETS.get(title)
    if not spec:
        return False

    _, sections = split_sections(body)
    new_body = render_sections(title, sections, spec)
    final = f"---\n{raw_frontmatter}\n---\n{new_body}" if raw_frontmatter else new_body
    if not dry_run:
        path.write_text(final, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Upgrade concept-map style map notes into the full map schema.")
    parser.add_argument("--vault", help="Override vault path")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    vault = resolve_vault_path(args.vault)
    maps_dir = vault / "00_maps"
    changed = 0
    for file_path in sorted(maps_dir.glob("*.md")):
        if process_file(file_path, dry_run=args.dry_run):
            changed += 1
            print(file_path.name)
    print(f"changed={changed}")
    print(f"dry_run={args.dry_run}")


if __name__ == "__main__":
    main()
