#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


NOTES: dict[str, str] = {
    "01_laws/轉動版牛頓第二定律.md": """---
type: law
title: 轉動版牛頓第二定律
domain: 力學
summary: 轉動版牛頓第二定律把合轉矩與角加速度連起來，是剛體動力學的核心方程。
applicability: 適用於固定軸或可明確指定轉軸的剛體轉動問題。
prerequisites: ["[[轉矩]]", "[[角加速度]]", "[[轉動慣量]]"]
related_concepts: ["[[滾動運動]]", "[[角動量守恆]]"]
related_quantities: ["[[轉矩]]", "[[角加速度]]", "[[轉動慣量]]"]
related_laws: ["[[牛頓第二定律]]"]
experiments: []
math_tools: []
derived_results: []
modern_connections: []
tags: [physics, mechanics, law]
updated: 2026-06-02
---

# 轉動版牛頓第二定律

## 敘述
剛體的轉動問題中，合轉矩扮演平移問題裡合力的角色，而角加速度則扮演加速度的角色。

## 數學表達
對固定轉軸且轉動慣量為常數的情況，
$$
\\sum \\tau = I\\alpha
$$

## 物理解讀
這條定律不是把平移公式硬換字母而已。真正的差別在於轉動慣量依賴質量分布，轉矩還依賴力臂與方向。

## 相關連結
- [[轉矩]]
- [[角加速度]]
- [[轉動慣量]]
- [[牛頓第二定律]]
- [[滾動運動]]
""",
    "01_laws/角動量守恆.md": """---
type: law
title: 角動量守恆
domain: 力學
summary: 在系統所受外轉矩為零時，總角動量保持不變，是轉動問題的關鍵守恆律。
applicability: 適用於外轉矩可忽略或恰為零的粒子系統與剛體系統。
prerequisites: ["[[角動量]]", "[[轉矩]]"]
related_concepts: ["[[進動]]", "[[陀螺]]"]
related_quantities: ["[[角動量]]", "[[轉矩]]"]
related_laws: []
experiments: []
math_tools: ["[[向量]]"]
derived_results: []
modern_connections: []
tags: [physics, mechanics, law]
updated: 2026-06-02
---

# 角動量守恆

## 敘述
若系統所受外轉矩為零，則總角動量不隨時間改變。

## 數學表達
$$
\\frac{d\\vec L}{dt} = \\vec \\tau_{\\text{ext}}
$$

因此當
$$
\\vec \\tau_{\\text{ext}} = 0
$$
時，有
$$
\\vec L = \\text{constant}
$$

## 物理解讀
這條守恆律是從轉矩與角動量的關係長出來的，不是獨立掉下來的神諭。它對碰撞、縮手旋轉、軌道運動與陀螺都很有殺傷力。

## 相關連結
- [[角動量]]
- [[轉矩]]
- [[進動]]
- [[陀螺]]
""",
    "01_laws/平行軸定理.md": """---
type: law
title: 平行軸定理
domain: 力學
summary: 平行軸定理給出剛體繞任一平行於質心軸的轉軸時，其轉動慣量與質心轉動慣量之間的關係。
applicability: 適用於已知質心轉動慣量、且新轉軸與質心軸平行的剛體問題。
prerequisites: ["[[轉動慣量]]", "[[質心]]"]
related_concepts: ["[[滾動運動]]"]
related_quantities: ["[[轉動慣量]]"]
related_laws: []
experiments: []
math_tools: []
derived_results: []
modern_connections: []
tags: [physics, mechanics, law]
updated: 2026-06-02
---

# 平行軸定理

## 敘述
若某轉軸與穿過質心的軸平行，則新軸的轉動慣量等於質心軸轉動慣量加上總質量乘以兩軸距離平方。

## 數學表達
$$
I = I_{cm} + Md^2
$$

## 物理解讀
這條定理告訴你：同一個物體的轉動慣量不是固定單一數值，而是隨轉軸位置改變。離質心越遠，轉動就越不容易改變。

## 相關連結
- [[轉動慣量]]
- [[質心]]
- [[滾動運動]]
""",
    "02_concepts/進動.md": """---
type: concept
title: 進動
domain: 力學
summary: 進動是高速旋轉物體在外轉矩作用下，角動量方向緩慢改變的現象。
prerequisites: ["[[角動量守恆]]", "[[轉矩]]", "[[角動量]]"]
related_laws: ["[[角動量守恆]]"]
related_quantities: ["[[角動量]]", "[[轉矩]]"]
related_concepts: ["[[陀螺]]"]
math_tools: ["[[向量]]"]
tags: [physics, mechanics, concept]
updated: 2026-06-02
---

# 進動

## 核心想法
當旋轉中的物體受到與角動量不平行的外轉矩時，角動量向量的方向會改變，但大小可能近似維持不變，這就表現為進動。

## 物理解讀
進動最容易讓人犯的錯，是以為外力矩會直接把物體「壓倒」。實際上，高速旋轉物體往往先改變的是角動量方向，而不是立刻倒下。

## 相關連結
- [[角動量守恆]]
- [[角動量]]
- [[轉矩]]
- [[陀螺]]
""",
    "02_concepts/陀螺.md": """---
type: concept
title: 陀螺
domain: 力學
summary: 陀螺是具有顯著自旋角動量的系統，其穩定性與進動行為是角動量物理的經典展示。
prerequisites: ["[[角動量]]", "[[進動]]", "[[轉動慣量]]"]
related_laws: ["[[角動量守恆]]"]
related_quantities: ["[[角動量]]", "[[轉動慣量]]"]
related_concepts: ["[[進動]]"]
math_tools: []
tags: [physics, mechanics, concept]
updated: 2026-06-02
---

# 陀螺

## 核心想法
陀螺的重要性不在玩具本身，而在它把 [[角動量守恆]]、[[轉矩]] 和 [[進動]] 同時攤在你面前。

## 物理解讀
自旋夠大的陀螺，對外轉矩的回應主要表現為軸向改變，而不是馬上倒下。這使它成為理解旋轉穩定性的最佳教材之一。

## 相關連結
- [[角動量]]
- [[角動量守恆]]
- [[進動]]
- [[轉動慣量]]
""",
    "03_quantities/楊氏模數.md": """---
type: quantity
title: 楊氏模數
symbol: E
unit: Pa
dimension: M L^-1 T^-2
domain: 力學
summary: 楊氏模數量化材料在拉伸或壓縮時抵抗形變的能力，是描述縱向彈性的核心參數。
related_concepts: ["[[彈性]]", "[[應力]]", "[[應變]]"]
related_laws: ["[[虎克定律]]"]
measurement_methods: []
tags: [physics, mechanics, quantity]
updated: 2026-06-02
---

# 楊氏模數

## 定義
楊氏模數描述材料在小形變範圍內，正應力與正應變之間的比例常數。

## 數學表達
$$
E = \\frac{\\sigma}{\\varepsilon}
$$

## 符號與單位
- 符號：$E$
- SI 單位：Pa

## 相關連結
- [[彈性]]
- [[應力]]
- [[應變]]
- [[虎克定律]]
""",
    "03_quantities/剪切模數.md": """---
type: quantity
title: 剪切模數
symbol: G
unit: Pa
dimension: M L^-1 T^-2
domain: 力學
summary: 剪切模數量化材料抵抗剪切形變的能力，是描述橫向變形的重要參數。
related_concepts: ["[[彈性]]", "[[剪應力]]", "[[應變]]"]
related_laws: ["[[虎克定律]]"]
measurement_methods: []
tags: [physics, mechanics, quantity]
updated: 2026-06-02
---

# 剪切模數

## 定義
剪切模數描述材料在剪切應力作用下，剪應力與剪應變之間的比例常數。

## 數學表達
$$
G = \\frac{\\tau}{\\gamma}
$$

## 符號與單位
- 符號：$G$
- SI 單位：Pa

## 相關連結
- [[彈性]]
- [[剪應力]]
- [[應變]]
""",
    "03_quantities/體積彈性模數.md": """---
type: quantity
title: 體積彈性模數
symbol: B
unit: Pa
dimension: M L^-1 T^-2
domain: 力學
summary: 體積彈性模數量化材料抵抗體積改變的能力，常用來描述流體與固體的可壓縮性。
related_concepts: ["[[彈性]]", "[[壓力]]", "[[體應變]]"]
related_laws: []
measurement_methods: []
tags: [physics, mechanics, quantity]
updated: 2026-06-02
---

# 體積彈性模數

## 定義
體積彈性模數描述材料在均勻壓力作用下，抵抗體積變化的能力。

## 數學表達
$$
B = -\\frac{\\Delta P}{\\Delta V / V}
$$

## 符號與單位
- 符號：$B$
- SI 單位：Pa

## 相關連結
- [[彈性]]
- [[壓力]]
- [[體應變]]
""",
    "03_quantities/剪應力.md": """---
type: quantity
title: 剪應力
symbol: \\tau
unit: Pa
dimension: M L^-1 T^-2
domain: 力學
summary: 剪應力表示平行於截面的內力強度，是描述材料剪切變形的基本量。
related_concepts: ["[[剪切模數]]", "[[彈性]]"]
related_laws: []
measurement_methods: []
tags: [physics, mechanics, quantity]
updated: 2026-06-02
---

# 剪應力

## 定義
剪應力是作用在截面切向方向上的內力除以面積，用來描述材料受剪時的應力狀態。

## 數學表達
$$
\\tau = \\frac{F_{\\parallel}}{A}
$$

## 符號與單位
- 符號：$\\tau$
- SI 單位：Pa

## 相關連結
- [[剪切模數]]
- [[彈性]]
""",
    "03_quantities/體應變.md": """---
type: quantity
title: 體應變
symbol: \\Delta V / V
unit: 1
dimension: 1
domain: 力學
summary: 體應變量化材料體積相對改變的程度，是研究可壓縮性與體積彈性模數的基本量。
related_concepts: ["[[體積彈性模數]]", "[[彈性]]"]
related_laws: []
measurement_methods: []
tags: [physics, mechanics, quantity]
updated: 2026-06-02
---

# 體應變

## 定義
體應變表示體積改變相對於原本體積的比例，是描述整體壓縮或膨脹程度的量。

## 數學表達
$$
\\text{體應變} = \\frac{\\Delta V}{V}
$$

## 符號與單位
- 常用寫法：$\\Delta V / V$
- 無因次

## 相關連結
- [[體積彈性模數]]
- [[彈性]]
- [[壓力]]
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
