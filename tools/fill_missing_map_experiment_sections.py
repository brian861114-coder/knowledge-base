#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from kb_paths import resolve_vault_path


SECTION_RE = re.compile(r"^(##)\s+(.+)$", re.MULTILINE)
INTUITION_HEADING = "物理直覺"
HISTORY_HEADING = "歷史背景"
ANCHOR_KEYWORDS = ("問題背景", "裝置與方法", "核心分析", "常見誤解", "相關概念", "延伸價值")


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


def find_insert_offset(body: str) -> int:
    for match in SECTION_RE.finditer(body):
        heading = match.group(2).strip()
        if any(keyword in heading for keyword in ANCHOR_KEYWORDS):
            return match.start()
    return len(body)


def map_intuition(title: str) -> str:
    return (
        f"{title} 的用途不是把頁面排成漂亮清單，而是替這個領域建立閱讀順序與概念主幹。"
        "先看哪些節點是骨架、哪些是支撐、哪些是應用，理解速度會比逐頁亂跳快得多。"
    )


def map_history(title: str) -> str:
    return (
        "這類總覽頁本身不是歷史對象，但它反映了一種後見之明："
        "只有在大量主題已經彼此連接之後，才可能把整個領域重新整理成較清楚的知識地圖。"
    )


def experiment_intuition(title: str) -> str:
    if title == "雙狹縫實驗":
        return (
            "雙狹縫實驗最殘酷的地方，是它逼你在『粒子走哪條路』和『波如何疊加』之間選邊站，"
            "而實驗結果會反覆打臉粗糙的經典直覺。它的教育性不只在條紋本身，而在於你會被迫承認："
            "觀測安排、相干條件與可得路徑資訊，真的會改變你能說什麼。"
        )
    return (
        f"{title} 的價值不只是在課堂上做出一個結果，而是把抽象概念壓到儀器、操作步驟、誤差來源與觀察判準之中。"
        "很多理論之所以真正站穩，不是因為一句定義，而是因為它能撐住反覆的量測安排。"
    )


def experiment_history(title: str) -> str:
    if title == "雙狹縫實驗":
        return (
            "雙狹縫實驗先在光學史上鞏固了波動觀，後來又在量子論裡成為最具象徵性的試金石之一。"
            "它之所以反覆出現，不是因為教科書偏愛它，而是因為它一次把干涉、相干、路徑資訊與量測問題全推到檯面上。"
        )
    return (
        "這類實驗頁的歷史核心，通常在於『如何把概念落到可重複操作的裝置』。"
        "很多理論真正成熟的時刻，不是提出名詞的那天，而是出現能穩定驗證它的實驗安排。"
    )


def ensure_sections(body: str, intuition: str, history: str) -> tuple[str, bool]:
    has_intuition = f"## {INTUITION_HEADING}" in body
    has_history = f"## {HISTORY_HEADING}" in body
    if has_intuition and has_history:
        return body, False

    pieces: list[str] = []
    if not has_intuition:
        pieces.append(f"## {INTUITION_HEADING}\n{intuition}\n")
    if not has_history:
        pieces.append(f"## {HISTORY_HEADING}\n{history}\n")
    block = "\n".join(pieces).strip() + "\n\n"

    offset = find_insert_offset(body)
    updated = body[:offset].rstrip() + "\n\n" + block + body[offset:].lstrip()
    return updated, True


def process_file(path: Path, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    raw_frontmatter, body = parse_frontmatter(text)
    frontmatter = parse_frontmatter_data(raw_frontmatter)
    title = frontmatter.get("title", path.stem).strip() or path.stem
    folder = path.parent.name

    if folder == "00_maps":
        intuition = map_intuition(title)
        history = map_history(title)
    elif folder == "04_experiments":
        intuition = experiment_intuition(title)
        history = experiment_history(title)
    else:
        return False

    new_body, changed = ensure_sections(body, intuition, history)
    if not changed:
        return False
    if dry_run:
        return True

    final = f"---\n{raw_frontmatter}\n---\n{new_body}" if raw_frontmatter else new_body
    path.write_text(final, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill missing standard sections for map and experiment notes.")
    parser.add_argument("--vault", help="Override vault path")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    vault = resolve_vault_path(args.vault)
    changed = 0
    matched = 0
    for folder in ("00_maps", "04_experiments"):
        folder_path = vault / folder
        if not folder_path.exists():
            continue
        for path in sorted(folder_path.glob("*.md")):
            matched += 1
            if process_file(path, args.dry_run):
                changed += 1
    print(f"matched={matched}")
    print(f"changed={changed}")
    print(f"dry_run={args.dry_run}")


if __name__ == "__main__":
    main()
