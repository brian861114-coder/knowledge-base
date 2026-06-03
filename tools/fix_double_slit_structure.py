#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


INTUITION_BLOCK = """## 物理直覺
雙狹縫實驗最殘酷的地方，是它逼你在『粒子走哪條路』和『波如何疊加』之間選邊站，而實驗結果會反覆打臉粗糙的經典直覺。它的教育性不只在條紋本身，而在於你會被迫承認：觀測安排、相干條件與可得路徑資訊，真的會改變你能說什麼。
"""

HISTORY_BLOCK = """## 歷史背景
雙狹縫實驗先在光學史上鞏固了波動觀，後來又在量子論裡成為最具象徵性的試金石之一。它之所以反覆出現，不是因為教科書偏愛它，而是因為它一次把干涉、相干、路徑資訊與量測問題全推到檯面上。
"""


def parse_frontmatter(text: str) -> tuple[str, str]:
    text = text.lstrip("\ufeff")
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 5 :]


def main() -> None:
    vault = resolve_vault_path()
    path = vault / "04_experiments" / "雙狹縫實驗.md"
    text = path.read_text(encoding="utf-8")
    raw_frontmatter, body = parse_frontmatter(text)

    if "## 物理直覺" in body and "## 歷史背景" in body:
        print("changed=0")
        return

    anchor = body.find("## 問題背景")
    if anchor == -1:
        raise RuntimeError("Expected '## 問題背景' anchor not found in 雙狹縫實驗.md")

    insertion = "\n" + INTUITION_BLOCK.strip() + "\n\n" + HISTORY_BLOCK.strip() + "\n\n"
    new_body = body[:anchor].rstrip() + insertion + body[anchor:]
    final = f"---\n{raw_frontmatter}\n---\n{new_body}" if raw_frontmatter else new_body
    path.write_text(final, encoding="utf-8")
    print("changed=1")


if __name__ == "__main__":
    main()
