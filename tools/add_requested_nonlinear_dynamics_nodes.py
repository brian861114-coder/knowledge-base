#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


NOTES: dict[str, str] = {
    "02_concepts/非線性系統.md": """---
type: concept
title: 非線性系統
domain: 動力系統
summary: 非線性系統的演化方程對狀態變數不是線性的，因此疊加原理通常失效，並可能產生分岔、混沌與複雜吸引子。
prerequisites: ["[[相空間]]", "[[矩陣]]"]
related_laws: []
related_quantities: []
related_concepts: ["[[混沌]]", "[[分岔]]", "[[吸引子]]", "[[正常模態]]"]
math_tools: ["[[矩陣]]", "[[向量]]"]
tags: [physics, dynamical-systems, concept]
updated: 2026-06-04
---

# 非線性系統

## 概念摘要
非線性系統是指演化方程對狀態變數不是線性的系統。這句話的殺傷力很大，因為一旦非線性出現，很多在線性世界裡乾淨漂亮的工具會立刻失效或只剩局部有效。

## 為什麼重要
在線性系統裡，疊加原理通常成立；在非線性系統裡，兩個解加起來大多不是解。這意味著行為可能出現多穩態、分岔、極限環、混沌，甚至完全出乎直覺。

## 和線性模態的差別
線性系統常能拆成 [[正常模態]]；非線性系統通常不能這麼乾淨地分解，或只能在小振幅近似下暫時偽裝成線性。

## 物理直覺
非線性不是小修飾，而是規則本身開始讓不同部分彼此糾纏。你若還用線性直覺硬看，通常只會誤判。

## 相關概念
- [[混沌]]
- [[分岔]]
- [[吸引子]]
- [[相空間]]
""",
    "02_concepts/混沌.md": """---
type: concept
title: 混沌
domain: 動力系統
summary: 混沌是由確定性方程產生的高度複雜動力行為，典型特徵包括初始條件敏感性、長期不可預測性與奇異吸引子。
prerequisites: ["[[非線性系統]]", "[[相空間]]"]
related_laws: []
related_quantities: ["[[李雅普諾夫指數]]"]
related_concepts: ["[[初始條件敏感性]]", "[[吸引子]]", "[[龐加萊截面]]", "[[分岔]]"]
math_tools: ["[[向量]]"]
tags: [physics, dynamical-systems, concept]
updated: 2026-06-04
---

# 混沌

## 概念摘要
混沌不是隨機亂數，而是由完全確定的方程產生的極度複雜行為。系統規則沒變，麻煩的是解對初始條件太敏感，久了之後幾乎不可能精確預測。

## 核心特徵
- [[初始條件敏感性]]
- 長期預測困難
- 常伴隨複雜的 [[吸引子]]

## 物理直覺
混沌最容易被誤會成「因為太亂所以沒規律」。錯。它不是沒規律，而是規律太嚴格、太糾纏，導致極小差異被放大到巨觀尺度。

## 相關概念
- [[非線性系統]]
- [[初始條件敏感性]]
- [[吸引子]]
- [[李雅普諾夫指數]]
""",
    "02_concepts/初始條件敏感性.md": """---
type: concept
title: 初始條件敏感性
domain: 動力系統
summary: 初始條件敏感性是指兩個極度接近的初始狀態，隨時間可能迅速分離，這是混沌系統的關鍵特徵之一。
prerequisites: ["[[非線性系統]]"]
related_laws: []
related_quantities: ["[[李雅普諾夫指數]]"]
related_concepts: ["[[混沌]]", "[[相空間]]"]
math_tools: ["[[向量]]"]
tags: [physics, dynamical-systems, concept]
updated: 2026-06-04
---

# 初始條件敏感性

## 概念摘要
初始條件敏感性是指：起點差一點點，後面可能差到完全像兩個世界。這是混沌系統最讓人頭痛、也最核心的特徵之一。

## 為什麼重要
如果小誤差會被快速放大，那麼就算方程完全確定、測量也很努力，長時間預測仍然會失效。

## 和隨機性的差別
這不是噪音亂入，而是確定性規則本身就在放大小偏差。你看到的不可靠，不是因為沒規律，而是因為規律太會放大誤差。

## 相關概念
- [[混沌]]
- [[李雅普諾夫指數]]
- [[相空間]]
""",
    "02_concepts/吸引子.md": """---
type: concept
title: 吸引子
domain: 動力系統
summary: 吸引子是相空間中會吸引鄰近軌道長時間靠近的集合，可以是固定點、極限環或更複雜的奇異吸引子。
prerequisites: ["[[相空間]]", "[[非線性系統]]"]
related_laws: []
related_quantities: []
related_concepts: ["[[混沌]]", "[[相圖]]", "[[龐加萊截面]]"]
math_tools: ["[[向量]]"]
tags: [physics, dynamical-systems, concept]
updated: 2026-06-04
---

# 吸引子

## 概念摘要
吸引子是相空間裡一組長時間會把鄰近軌道拉過去的集合。它不一定是一個點，也可能是一條閉曲線，甚至是一個形狀複雜到近乎病態的集合。

## 常見類型
- 固定點
- 極限環
- 奇異吸引子

## 物理直覺
吸引子代表系統長時間願意待在哪種行為附近。它不是瞬間狀態，而是長期命運的骨架。

## 相關概念
- [[相圖]]
- [[混沌]]
- [[龐加萊截面]]
""",
    "02_concepts/相圖.md": """---
type: concept
title: 相圖
domain: 動力系統
summary: 相圖是把系統在相空間中的軌道視覺化，用來觀察固定點、吸引子、極限環與整體流向結構。
prerequisites: ["[[相空間]]"]
related_laws: []
related_quantities: []
related_concepts: ["[[吸引子]]", "[[龐加萊截面]]", "[[分岔]]"]
math_tools: ["[[向量]]"]
tags: [physics, dynamical-systems, concept]
updated: 2026-06-04
---

# 相圖

## 概念摘要
相圖是把系統在 [[相空間]] 中的軌道畫出來。它的重點不是作圖好看，而是讓你直接看到系統會往哪裡流、繞哪裡轉、卡在哪裡。

## 可以看出什麼
- 固定點
- 極限環
- 吸引子
- 穩定與不穩定區域

## 物理直覺
很多動力系統若只盯著時間序列，你會被細節淹死；一搬到相圖，整體骨架反而突然清楚。

## 相關概念
- [[相空間]]
- [[吸引子]]
- [[龐加萊截面]]
""",
    "02_concepts/龐加萊截面.md": """---
type: concept
title: 龐加萊截面
domain: 動力系統
summary: 龐加萊截面以低維切面觀察高維連續動力系統的返回點結構，是分析週期、準週期與混沌的重要工具。
prerequisites: ["[[相空間]]", "[[相圖]]"]
related_laws: []
related_quantities: []
related_concepts: ["[[混沌]]", "[[吸引子]]", "[[分岔]]"]
math_tools: ["[[向量]]"]
tags: [physics, dynamical-systems, concept]
updated: 2026-06-04
---

# 龐加萊截面

## 概念摘要
龐加萊截面是把高維連續演化切成一張低維切面，然後只記錄軌道每次穿過該切面的點。這能把很難直接讀的流動結構壓成更容易觀察的離散圖樣。

## 為什麼有用
在高維系統裡，直接看完整軌道常常太亂。龐加萊截面能把週期、準週期與混沌的差異壓縮成清楚得多的幾何圖樣。

## 物理直覺
這相當於你不再追每一秒，而是固定在某個門口，只記錄系統每次經過那扇門時的狀態。

## 相關概念
- [[相圖]]
- [[混沌]]
- [[吸引子]]
""",
    "03_quantities/李雅普諾夫指數.md": """---
type: quantity
title: 李雅普諾夫指數
symbol: \\lambda
unit: 1/s
dimension: T^-1
domain: 動力系統
summary: 李雅普諾夫指數量化相鄰軌道分離或收斂的平均指數速率，是判定初始條件敏感性與混沌的重要量。
related_concepts: ["[[混沌]]", "[[初始條件敏感性]]", "[[相空間]]"]
related_laws: []
measurement_methods: []
tags: [physics, dynamical-systems, quantity]
updated: 2026-06-04
---

# 李雅普諾夫指數

## 量綱摘要
李雅普諾夫指數描述相鄰軌道在平均意義下分離或收斂得有多快，常記作
$$
\\lambda.
$$

## 物理意義
若最大的李雅普諾夫指數為正，代表鄰近初始條件的差異會指數放大，這通常是 [[混沌]] 的強烈訊號。

## 和混沌的關係
它不是混沌的全部，但它是最常用來量化 [[初始條件敏感性]] 的工具之一。

## 相關概念
- [[混沌]]
- [[初始條件敏感性]]
- [[相空間]]
""",
    "02_concepts/分岔.md": """---
type: concept
title: 分岔
domain: 動力系統
summary: 分岔是系統控制參數跨過某個臨界值後，長時間行為的質性結構發生改變，例如固定點失穩、週期出現或混沌誕生。
prerequisites: ["[[非線性系統]]", "[[相圖]]"]
related_laws: []
related_quantities: []
related_concepts: ["[[混沌]]", "[[吸引子]]", "[[龐加萊截面]]"]
math_tools: ["[[向量]]"]
tags: [physics, dynamical-systems, concept]
updated: 2026-06-04
---

# 分岔

## 概念摘要
分岔是系統在調整某個控制參數時，整體行為骨架突然改變的現象。不是數值多一點少一點，而是系統長時間命運的類型換了。

## 常見效果
- 固定點由穩變不穩
- 週期解突然出現
- 週期倍化一路推向混沌

## 物理直覺
分岔代表系統不是平滑地「慢慢變」，而是參數過某個門檻後，行為拓樸直接換檔。

## 相關概念
- [[非線性系統]]
- [[混沌]]
- [[吸引子]]
- [[龐加萊截面]]
""",
}


def write_file(vault: Path, relative_path: str, content: str) -> None:
    target = vault / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def main() -> None:
    vault = resolve_vault_path()
    for relative_path, content in NOTES.items():
        write_file(vault, relative_path, content)
    print(f"wrote={len(NOTES)} notes")


if __name__ == "__main__":
    main()
