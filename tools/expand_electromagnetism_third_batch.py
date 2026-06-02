#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


NOTES: dict[str, str] = {
    "01_laws/焦耳定律.md": """---
type: law
title: 焦耳定律
domain: 電磁學
summary: 焦耳定律描述電流通過電阻時產生熱的速率，是電能轉換為熱能的基本定律。
applicability: 適用於電阻性發熱分析，常見於直流電路與等效電阻模型。
prerequisites: ["[[電流]]", "[[電阻]]", "[[電位差]]"]
related_concepts: ["[[直流電路]]"]
related_quantities: ["[[電功率]]", "[[電流]]", "[[電阻]]"]
related_laws: ["[[歐姆定律]]"]
experiments: []
math_tools: []
derived_results: []
modern_connections: []
tags: [physics, electromagnetism, law]
updated: 2026-06-02
---

# 焦耳定律

## 敘述
當電流通過電阻性元件時，電能會以熱的形式釋放。焦耳定律量化了這個能量轉換速率。

## 數學表達
$$
P = I^2R
$$

若結合 [[歐姆定律]]，也可寫成
$$
P = IV = \\frac{V^2}{R}
$$

## 物理解讀
焦耳定律不是額外的神祕規則，而是電場對載流子作功、再經散射轉成內能的結果。它直接決定電路中的發熱與功耗。

## 相關連結
- [[電功率]]
- [[電流]]
- [[電阻]]
- [[電位差]]
- [[歐姆定律]]
- [[直流電路]]
""",
    "03_quantities/電功率.md": """---
type: quantity
title: 電功率
symbol: P
unit: W
dimension: M L^2 T^-3
domain: 電磁學
summary: 電功率表示電路中每單位時間進行的電能轉換速率，是分析耗能與輸出的核心量。
related_concepts: ["[[直流電路]]", "[[交流電]]"]
related_laws: ["[[焦耳定律]]", "[[歐姆定律]]"]
measurement_methods: []
tags: [physics, electromagnetism, quantity]
updated: 2026-06-02
---

# 電功率

## 定義
電功率描述單位時間內電能被轉換或傳遞的速率。它可以表現為熱、光、機械輸出或其他形式。

## 數學表達
最基本的形式是
$$
P = IV
$$

對純電阻元件，依 [[焦耳定律]] 可寫成
$$
P = I^2R = \\frac{V^2}{R}
$$

## 符號與單位
- 符號：$P$
- SI 單位：W

## 物理解讀
電功率不是「電流大就一定功率大」。它同時取決於電流與電位差，也取決於電路中能量如何被分配與耗散。

## 相關連結
- [[直流電路]]
- [[交流電]]
- [[焦耳定律]]
- [[歐姆定律]]
""",
    "02_concepts/內電阻.md": """---
type: concept
title: 內電阻
domain: 電磁學
summary: 內電阻描述實際電源自身對電流的阻礙，解釋了端電壓為何會隨負載而改變。
prerequisites: ["[[電動勢]]", "[[電流]]", "[[電阻]]"]
related_laws: ["[[歐姆定律]]"]
related_quantities: ["[[電動勢]]", "[[電位差]]", "[[電流]]"]
related_concepts: ["[[直流電路]]", "[[串聯電路]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 內電阻

## 核心想法
理想電源只有 [[電動勢]]，沒有任何內部損耗；實際電源則存在內電阻，所以輸出端電壓會因負載電流而下降。

## 數學關係
若電源電動勢為 $\\mathcal{E}$、內電阻為 $r$、輸出電流為 $I$，端電壓可寫成
$$
V = \\mathcal{E} - Ir
$$

## 物理解讀
內電阻把部分能量耗散在電源內部，因此負載越重、電流越大，端電壓通常越低。

## 相關連結
- [[電動勢]]
- [[電位差]]
- [[電流]]
- [[電阻]]
- [[直流電路]]
- [[串聯電路]]
""",
    "02_concepts/串聯電路.md": """---
type: concept
title: 串聯電路
domain: 電磁學
summary: 串聯電路中元件首尾相接，流過每個元件的電流相同，而總電位差會分配到各元件上。
prerequisites: ["[[直流電路]]", "[[電流]]", "[[電位差]]"]
related_laws: ["[[歐姆定律]]", "[[基爾霍夫電壓定律]]"]
related_quantities: ["[[電流]]", "[[電位差]]", "[[電阻]]"]
related_concepts: ["[[並聯電路]]", "[[迴路分析]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 串聯電路

## 核心想法
串聯結構只有一條主要通路，因此各元件流過的 [[電流]] 相同，但每個元件上的 [[電位差]] 可以不同。

## 等效規則
對純電阻串聯，有
$$
R_{\\text{eq}} = R_1 + R_2 + \\cdots
$$

## 物理解讀
串聯的本質不是「排成一列」這麼膚淺，而是所有元件共用同一支路電流，因此任何一個元件的改變都會影響整個回路。

## 相關連結
- [[直流電路]]
- [[電流]]
- [[電位差]]
- [[電阻]]
- [[基爾霍夫電壓定律]]
- [[迴路分析]]
""",
    "02_concepts/並聯電路.md": """---
type: concept
title: 並聯電路
domain: 電磁學
summary: 並聯電路中各支路共享相同端電壓，但總電流會在支路間分配。
prerequisites: ["[[直流電路]]", "[[電流]]", "[[電位差]]"]
related_laws: ["[[歐姆定律]]", "[[基爾霍夫電流定律]]"]
related_quantities: ["[[電流]]", "[[電位差]]", "[[電阻]]"]
related_concepts: ["[[串聯電路]]", "[[節點分析]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 並聯電路

## 核心想法
並聯結構讓各支路接在同一對節點上，因此每條支路承受相同的 [[電位差]]，但支路電流可以不同。

## 等效規則
對純電阻並聯，有
$$
\\frac{1}{R_{\\text{eq}}} = \\frac{1}{R_1} + \\frac{1}{R_2} + \\cdots
$$

## 物理解讀
並聯的關鍵在於節點條件，而不是畫圖時是否平行。支路越多，系統提供電流的方式越彈性，但分析時更依賴 [[基爾霍夫電流定律]]。

## 相關連結
- [[直流電路]]
- [[電流]]
- [[電位差]]
- [[電阻]]
- [[基爾霍夫電流定律]]
- [[節點分析]]
""",
    "02_concepts/電介質.md": """---
type: concept
title: 電介質
domain: 電磁學
summary: 電介質是在外電場下會極化但不形成自由導電電流的材料，能顯著影響電容器行為。
prerequisites: ["[[電場]]", "[[電容器]]"]
related_laws: []
related_quantities: []
related_concepts: ["[[平行板電容器]]", "[[介電常數]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 電介質

## 核心想法
電介質中的束縛電荷會在外加 [[電場]] 下產生極化，這會改變材料內部的有效電場與儲能能力。

## 物理解讀
把電介質插入 [[電容器]] 後，系統通常能在相同電壓下儲存更多電荷，等效上就是電容增大。

## 相關連結
- [[電場]]
- [[電容器]]
- [[平行板電容器]]
- [[介電常數]]
""",
    "02_concepts/介電常數.md": """---
type: concept
title: 介電常數
domain: 電磁學
summary: 介電常數描述材料對外加電場的回應強弱，是刻畫電介質效應的重要參數。
prerequisites: ["[[電介質]]", "[[電容器]]"]
related_laws: []
related_quantities: []
related_concepts: ["[[平行板電容器]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 介電常數

## 核心想法
介電常數反映材料在電場中極化的程度。相對介電常數越大，材料對電容器的增容效果通常越明顯。

## 基本關係
在理想平行板模型中，插入電介質後電容常寫成
$$
C = \\kappa C_0
$$
其中 $\\kappa$ 為相對介電常數。

## 相關連結
- [[電介質]]
- [[電容器]]
- [[平行板電容器]]
""",
    "02_concepts/電場能.md": """---
type: concept
title: 電場能
domain: 電磁學
summary: 電場能描述能量以電場形式儲存在系統中的方式，是理解電容器與場觀點的重要概念。
prerequisites: ["[[電場]]", "[[電容器]]", "[[電位差]]"]
related_laws: []
related_quantities: ["[[電位差]]"]
related_concepts: ["[[平行板電容器]]", "[[電場]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 電場能

## 核心想法
能量不必只存成粒子動能或熱，也可以直接存進電場本身。電容器就是最直觀的例子。

## 典型公式
對電容器，
$$
U = \\frac{1}{2}CV^2 = \\frac{Q^2}{2C} = \\frac{1}{2}QV
$$

## 物理解讀
這個觀點的重要性在於：能量不是黏在某個導線上，而是分布在場的結構中。

## 相關連結
- [[電場]]
- [[電容器]]
- [[平行板電容器]]
- [[電位差]]
""",
    "02_concepts/節點分析.md": """---
type: concept
title: 節點分析
domain: 電磁學
summary: 節點分析以節點電位為未知量，利用基爾霍夫電流定律建立方程，是並聯與多支路電路的標準方法。
prerequisites: ["[[基爾霍夫電流定律]]", "[[並聯電路]]", "[[電位差]]"]
related_laws: ["[[基爾霍夫電流定律]]", "[[歐姆定律]]"]
related_quantities: ["[[電位差]]", "[[電流]]"]
related_concepts: ["[[迴路分析]]", "[[直流電路]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 節點分析

## 核心想法
節點分析把各節點的電位當作主要未知量，然後用 [[基爾霍夫電流定律]] 把支路電流全部寫成節點電位差的函數。

## 為什麼有效
在支路很多的 [[並聯電路]] 中，直接追每條電流很煩；改追節點電位通常更乾淨。

## 相關連結
- [[基爾霍夫電流定律]]
- [[歐姆定律]]
- [[並聯電路]]
- [[迴路分析]]
- [[直流電路]]
""",
    "02_concepts/迴路分析.md": """---
type: concept
title: 迴路分析
domain: 電磁學
summary: 迴路分析以回路電流為未知量，利用基爾霍夫電壓定律建立方程，是串聯與多迴路電路的標準方法。
prerequisites: ["[[基爾霍夫電壓定律]]", "[[串聯電路]]", "[[電位差]]"]
related_laws: ["[[基爾霍夫電壓定律]]", "[[歐姆定律]]"]
related_quantities: ["[[電位差]]", "[[電流]]"]
related_concepts: ["[[節點分析]]", "[[直流電路]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 迴路分析

## 核心想法
迴路分析把獨立回路中的假設電流當作未知量，接著用 [[基爾霍夫電壓定律]] 把每一圈的電位升降寫成方程。

## 為什麼有效
對以 [[串聯電路]] 為骨架的多迴路系統，迴路分析通常比直接做節點記帳更直觀。

## 相關連結
- [[基爾霍夫電壓定律]]
- [[歐姆定律]]
- [[串聯電路]]
- [[節點分析]]
- [[直流電路]]
""",
}


def write_file(base: Path, relative_path: str, content: str) -> None:
    target = base / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def main() -> None:
    vault = resolve_vault_path()
    for relative_path, content in NOTES.items():
        write_file(vault, relative_path, content)
    print(f"wrote={len(NOTES)} notes")


if __name__ == "__main__":
    main()
