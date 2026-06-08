#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from kb_paths import resolve_vault_path


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


MAP_INSERTS: dict[str, list[tuple[str, str]]] = {
    "數學工具總覽": [
        (
            "關鍵概念",
            "- [[向量]]：提供方向、大小與線性組合的最基本語言。\n"
            "- [[導數]]：把局部變化率變成可計算對象，是動力學與場論的入口。\n"
            "- [[積分]]：把局部量累積成整體結果，對守恆量與總效應特別重要。\n"
            "- [[矩陣]]：把線性映射、本徵值問題與耦合系統寫成統一形式。\n"
            "- [[梯度]]：把純量場的局部變化轉成向量，直接連到場與勢能的描述。\n"
            "- [[複數]]：把振動、相位與波動問題轉成更緊湊的表示。"
        ),
        (
            "關鍵定律",
            "- 本頁以數學工具為主，不以單一定律為核心；較重要的是這些工具如何支撐 [[牛頓第二定律]]、[[高斯定律]]、[[法拉第感應定律]] 與 [[薛丁格方程]] 等理論表述。\n"
            "- 對這張地圖而言，『關鍵定律』不是新增一批獨立主題，而是標示哪些物理規律會迫使你回頭學會對應的數學語言。"
        ),
    ],
    "物理基礎概念總覽": [
        (
            "主要主題",
            "- 運動描述：先分清位置、時間、速度、加速度與參考系，否則後面所有定律都會失焦。\n"
            "- 交互作用與守恆：力、能量、動量與角動量提供了理解系統演化的主幹語言。\n"
            "- 場與連續描述：當問題從粒子擴展到介質、電磁與波動時，場的觀點開始接手。"
        ),
        (
            "關鍵概念",
            "- [[速度]]、[[加速度]]：描述運動狀態與變化率，是最基礎的運動學骨架。\n"
            "- [[力]]、[[慣性]]：建立交互作用如何改變運動的最小概念組。\n"
            "- [[能量]]、[[動量]]：把系統演化改寫成更穩定的守恆語言。\n"
            "- [[參考系]]：決定哪些量是觀測結果，哪些是理論表示方式。"
        ),
        (
            "關鍵定律",
            "- [[牛頓第一定律]]：界定慣性系與無外力時的運動基準。\n"
            "- [[牛頓第二定律]]：把受力與運動變化率接起來，是經典力學主幹。\n"
            "- [[動量守恆]]：當外力結構合適時，提供比逐點受力更穩的描述。\n"
            "- [[能量守恆]]：把不同形式的作用統一進單一帳本，是後續各領域共通語言。"
        ),
        (
            "典型問題類型",
            "- 已知初始條件，判斷系統隨時間如何演化。\n"
            "- 比較不同概念其實在描述同一現象的哪個面向。\n"
            "- 在多種描述語言之間切換，例如從受力圖切到能量或動量分析。"
        ),
    ],
}


LAW_INSERTS: dict[str, str] = {
    "角動量守恆": "### 相關概念\n- [[角動量]]\n- [[力矩]]\n- [[轉動慣量]]\n\n### 物理量\n- [[角速度]]\n- [[角位移]]\n- [[動量]]\n\n### 數學工具\n- [[向量]]\n- [[外積]]",
    "轉動運動學方程": "### 相關概念\n- [[轉動運動]]\n- [[剛體]]\n- [[角位移]]\n\n### 物理量\n- [[角速度]]\n- [[角加速度]]\n- [[時間]]\n\n### 數學工具\n- [[導數]]\n- [[積分]]",
}


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


def section_present(body: str, heading: str) -> bool:
    return f"## {heading}" in body


def insert_before_heading(body: str, heading: str, new_heading: str, content: str) -> tuple[str, bool]:
    if section_present(body, new_heading):
        return body, False
    matches = list(SECTION_RE.finditer(body))
    for match in matches:
        if match.group(1).strip() == heading:
            block = f"## {new_heading}\n{content}\n\n"
            updated = body[: match.start()].rstrip() + "\n\n" + block + body[match.start() :].lstrip()
            return updated, True
    block = f"\n\n## {new_heading}\n{content}\n"
    return body.rstrip() + block, True


def process_map(path: Path, title: str, body: str) -> tuple[str, bool]:
    changed = False
    updated = body
    for heading, content in MAP_INSERTS.get(title, []):
        if heading == "主要主題":
            anchor = "建議學習順序"
        elif heading in {"關鍵概念", "關鍵定律"}:
            anchor = "典型問題類型"
        else:
            anchor = "建議學習順序"
        updated, did_change = insert_before_heading(updated, anchor, heading, content)
        changed = changed or did_change
    return updated, changed


def process_law(path: Path, title: str, body: str) -> tuple[str, bool]:
    content = LAW_INSERTS.get(title)
    if not content:
        return body, False
    return insert_before_heading(body, "現代理論視角", "相關連結", content)


def process_file(path: Path, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    raw_frontmatter, body = parse_frontmatter(text)
    frontmatter = parse_frontmatter_data(raw_frontmatter)
    note_type = frontmatter.get("type", "").strip()
    title = frontmatter.get("title", "").strip() or path.stem

    if note_type == "map":
        new_body, changed = process_map(path, title, body)
    elif note_type == "law":
        new_body, changed = process_law(path, title, body)
    else:
        return False

    if not changed:
        return False
    if dry_run:
        return True
    final = f"---\n{raw_frontmatter}\n---\n{new_body}" if raw_frontmatter else new_body
    path.write_text(final, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill final remaining structure gaps in map and law notes.")
    parser.add_argument("--vault", help="Override vault path")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    vault = resolve_vault_path(args.vault)
    targets = [
        vault / "00_maps" / "數學工具總覽.md",
        vault / "00_maps" / "物理基礎概念總覽.md",
        vault / "01_laws" / "角動量守恆.md",
        vault / "01_laws" / "轉動運動學方程.md",
    ]

    changed = 0
    matched = 0
    for path in targets:
        if not path.exists():
            continue
        matched += 1
        if process_file(path, args.dry_run):
            changed += 1
    print(f"matched={matched}")
    print(f"changed={changed}")
    print(f"dry_run={args.dry_run}")


if __name__ == "__main__":
    main()
