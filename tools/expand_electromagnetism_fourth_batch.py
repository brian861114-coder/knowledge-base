#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


NOTES: dict[str, str] = {
    "01_laws/安培-馬克士威方程.md": """---
type: law
title: 安培-馬克士威方程
domain: 電磁學
summary: 安培-馬克士威方程把導電電流與位移電流一起納入磁場來源，是麥克斯威方程組的關鍵一環。
applicability: 適用於一般電磁場問題，特別是電場隨時間變化時。
prerequisites: ["[[安培定律]]", "[[位移電流]]", "[[電場]]", "[[磁場]]"]
related_concepts: ["[[電磁波]]", "[[麥克斯威方程組]]"]
related_quantities: []
related_laws: ["[[安培定律]]"]
experiments: []
math_tools: ["[[積分]]"]
derived_results: []
modern_connections: []
tags: [physics, electromagnetism, law]
updated: 2026-06-02
---

# 安培-馬克士威方程

## 敘述
安培定律若只包含導電電流，對充電中的電容器會出現邏輯缺口。馬克士威補上位移電流項後，磁場來源才在數學與物理上完整一致。

## 數學表達
積分形式為
$$
\\oint \\vec B\\cdot d\\vec l = \\mu_0 I_{\\text{enc}} + \\mu_0\\varepsilon_0\\frac{d\\Phi_E}{dt}
$$

微分形式為
$$
\\nabla \\times \\vec B = \\mu_0 \\vec J + \\mu_0\\varepsilon_0\\frac{\\partial \\vec E}{\\partial t}
$$

## 物理解讀
這條方程真正厲害的地方不是補了一項，而是讓變動電場也能成為磁場來源。沒有這一步，[[電磁波]] 根本長不出來。

## 相關連結
- [[安培定律]]
- [[位移電流]]
- [[電場]]
- [[磁場]]
- [[麥克斯威方程組]]
- [[電磁波]]
""",
    "02_concepts/位移電流修正.md": """---
type: concept
title: 位移電流修正
domain: 電磁學
summary: 位移電流修正是馬克士威為安培定律加入的補項，用來維持連續性與自洽性。
prerequisites: ["[[安培定律]]", "[[位移電流]]", "[[電容器]]"]
related_laws: ["[[安培-馬克士威方程]]"]
related_quantities: []
related_concepts: ["[[電磁波]]", "[[麥克斯威方程組]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 位移電流修正

## 核心想法
位移電流修正不是在真空中「硬塞一股假電流」，而是承認變動電場在場方程裡也扮演源項角色。

## 為什麼必要
若不加這項修正，對充電中的 [[電容器]] 使用 [[安培定律]] 時，會因取不同積分面而得到互相衝突的結果。

## 物理解讀
位移電流修正讓電荷守恆、場方程與波動傳播三件事能同時成立。這不是數學裝飾，是整套電磁學能站住腳的補丁。

## 相關連結
- [[安培定律]]
- [[安培-馬克士威方程]]
- [[位移電流]]
- [[電容器]]
- [[電磁波]]
""",
    "02_concepts/電磁場能量流.md": """---
type: concept
title: 電磁場能量流
domain: 電磁學
summary: 電磁場能量流描述能量如何在空間中隨電場與磁場共同傳遞，是場觀點下的能量運輸概念。
prerequisites: ["[[電場]]", "[[磁場]]", "[[電磁波]]"]
related_laws: ["[[安培-馬克士威方程]]"]
related_quantities: ["[[坡印廷向量]]"]
related_concepts: ["[[麥克斯威方程組]]"]
math_tools: ["[[向量]]"]
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 電磁場能量流

## 核心想法
電磁能量不是只能沿著導線「跑」。在場觀點下，能量可以透過周圍空間由電場與磁場共同傳遞。

## 物理解讀
這個概念直接打臉那種把電路能量想成電子小球在銅線裡搬運的粗糙圖像。導線重要，但能量流本身往往分布在導線附近的場中。

## 相關連結
- [[電場]]
- [[磁場]]
- [[電磁波]]
- [[坡印廷向量]]
- [[麥克斯威方程組]]
""",
    "03_quantities/坡印廷向量.md": """---
type: quantity
title: 坡印廷向量
symbol: \\vec S
unit: W/m^2
dimension: M T^-3
domain: 電磁學
summary: 坡印廷向量量化電磁場每單位面積、每單位時間的能量流率，是描述電磁能量傳輸方向與強度的量。
related_concepts: ["[[電磁場能量流]]", "[[電磁波]]"]
related_laws: ["[[安培-馬克士威方程]]"]
measurement_methods: []
tags: [physics, electromagnetism, quantity]
updated: 2026-06-02
---

# 坡印廷向量

## 定義
坡印廷向量描述電磁場的能量流密度，也就是單位面積上每秒通過多少電磁能量，以及它往哪個方向流。

## 數學表達
在真空中可寫成
$$
\\vec S = \\frac{1}{\\mu_0}\\vec E \\times \\vec B
$$

## 符號與單位
- 符號：$\\vec S$
- SI 單位：W/m$^2$

## 物理解讀
方向由 $\\vec E \\times \\vec B$ 決定，因此自然給出能量傳播方向。對 [[電磁波]] 而言，坡印廷向量就對應波的能流方向。

## 相關連結
- [[電磁場能量流]]
- [[電磁波]]
- [[電場]]
- [[磁場]]
""",
    "02_concepts/電磁波傳播.md": """---
type: concept
title: 電磁波傳播
domain: 電磁學
summary: 電磁波傳播描述變動電場與磁場如何彼此驅動並在空間中自我維持地向前傳播。
prerequisites: ["[[電磁波]]", "[[安培-馬克士威方程]]", "[[法拉第定律]]"]
related_laws: ["[[安培-馬克士威方程]]", "[[法拉第定律]]"]
related_quantities: ["[[坡印廷向量]]"]
related_concepts: ["[[電磁場能量流]]"]
math_tools: ["[[向量]]"]
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 電磁波傳播

## 核心想法
變動磁場誘發電場，變動電場又誘發磁場。這種互相驅動讓場不需要介質也能自我維持並向前傳播。

## 物理解讀
電磁波不是「電場在前面跑、磁場在後面追」。兩者是耦合結構，彼此垂直，並共同垂直於傳播方向。

## 相關連結
- [[電磁波]]
- [[法拉第定律]]
- [[安培-馬克士威方程]]
- [[坡印廷向量]]
- [[電磁場能量流]]
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
