#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


NOTES: dict[str, str] = {
    "02_concepts/機械平衡.md": """---
type: concept
title: 機械平衡
domain: 力學
summary: 機械平衡指物體在平移與轉動上都沒有加速度，是靜力學與結構分析的核心條件。
prerequisites: ["[[牛頓第二定律]]", "[[轉矩]]", "[[向量]]"]
related_laws: ["[[牛頓第二定律]]"]
related_quantities: ["[[轉矩]]", "[[重力]]"]
related_concepts: ["[[靜力平衡]]", "[[質心]]", "[[彈性]]"]
math_tools: ["[[向量]]"]
tags: [physics, mechanics, concept]
updated: 2026-06-02
---

# 機械平衡

## 核心想法
真正的機械平衡不是只有合力為零，還必須連合轉矩也為零。否則物體雖然不平移，仍然可能開始轉動。

## 條件
對剛體而言，平衡條件通常寫成
$$
\\sum \\vec F = 0, \\qquad \\sum \\tau = 0
$$

## 物理解讀
機械平衡把平移與轉動兩個自由度同時管住，因此是連接 [[牛頓第二定律]] 與剛體靜力分析的橋樑。

## 相關連結
- [[靜力平衡]]
- [[轉矩]]
- [[質心]]
- [[彈性]]
- [[牛頓第二定律]]
""",
    "02_concepts/靜力平衡.md": """---
type: concept
title: 靜力平衡
domain: 力學
summary: 靜力平衡是機械平衡的特殊情況，物體保持靜止且合力與合轉矩皆為零。
prerequisites: ["[[機械平衡]]", "[[轉矩]]"]
related_laws: ["[[牛頓第二定律]]"]
related_quantities: ["[[轉矩]]", "[[重力]]"]
related_concepts: ["[[質心]]", "[[彈性]]"]
math_tools: ["[[向量]]"]
tags: [physics, mechanics, concept]
updated: 2026-06-02
---

# 靜力平衡

## 核心想法
如果物體原本靜止，而且滿足合力為零與合轉矩為零，那它就維持靜止，這就是靜力平衡。

## 典型應用
- 梁與支架受力分析
- 懸掛物體的張力分配
- 重心與支點位置判斷

## 物理解讀
靜力平衡問題看起來像代數題，但本質是把平移與轉動條件一起考慮。只顧其中一個，答案就會錯。

## 相關連結
- [[機械平衡]]
- [[轉矩]]
- [[質心]]
- [[彈性]]
""",
    "02_concepts/彈性.md": """---
type: concept
title: 彈性
domain: 力學
summary: 彈性描述物體在受力變形後恢復原狀的傾向，是材料力學與固體形變分析的基礎。
prerequisites: ["[[虎克定律]]", "[[力]]"]
related_laws: ["[[虎克定律]]"]
related_quantities: ["[[應力]]", "[[應變]]"]
related_concepts: ["[[機械平衡]]"]
math_tools: []
tags: [physics, mechanics, concept]
updated: 2026-06-02
---

# 彈性

## 核心想法
彈性關心的不是「東西會不會彈回來」這種口語描述，而是材料在外力作用下如何產生可逆形變，以及這種形變與受力之間的關係。

## 物理解讀
在小形變範圍內，許多材料近似服從 [[虎克定律]]；超出這個範圍後，關係可能不再線性，甚至進入塑性變形。

## 相關連結
- [[虎克定律]]
- [[應力]]
- [[應變]]
- [[機械平衡]]
""",
    "03_quantities/應力.md": """---
type: quantity
title: 應力
symbol: \\sigma
unit: Pa
dimension: M L^-1 T^-2
domain: 力學
summary: 應力表示單位面積上承受的內力強度，是描述材料受力狀態的基本量。
related_concepts: ["[[彈性]]", "[[應變]]"]
related_laws: ["[[虎克定律]]"]
measurement_methods: []
tags: [physics, mechanics, quantity]
updated: 2026-06-02
---

# 應力

## 定義
應力描述材料內部抵抗外力的強度，定義為作用力除以受力截面積。

## 數學表達
$$
\\sigma = \\frac{F}{A}
$$

## 符號與單位
- 符號：$\\sigma$
- SI 單位：Pa

## 相關連結
- [[彈性]]
- [[應變]]
- [[虎克定律]]
""",
    "03_quantities/應變.md": """---
type: quantity
title: 應變
symbol: \\varepsilon
unit: 1
dimension: 1
domain: 力學
summary: 應變量化材料形變的相對大小，是描述伸長、壓縮或剪切變形的基本量。
related_concepts: ["[[彈性]]", "[[應力]]"]
related_laws: ["[[虎克定律]]"]
measurement_methods: []
tags: [physics, mechanics, quantity]
updated: 2026-06-02
---

# 應變

## 定義
對一維拉伸問題，應變表示長度改變相對於原長度的比例。

## 數學表達
$$
\\varepsilon = \\frac{\\Delta L}{L_0}
$$

## 符號與單位
- 符號：$\\varepsilon$
- 無因次

## 相關連結
- [[彈性]]
- [[應力]]
- [[虎克定律]]
""",
    "03_quantities/角速度.md": """---
type: quantity
title: 角速度
symbol: \\omega
unit: rad/s
dimension: T^-1
domain: 力學
summary: 角速度描述物體轉動快慢與方向，是轉動運動學的核心量。
related_concepts: ["[[轉動慣量]]", "[[角加速度]]", "[[滾動運動]]"]
related_laws: []
measurement_methods: []
tags: [physics, mechanics, quantity]
updated: 2026-06-02
---

# 角速度

## 定義
角速度是角位移對時間的變化率，用來描述物體轉得多快以及沿哪個軸轉動。

## 數學表達
$$
\\omega = \\frac{d\\theta}{dt}
$$

## 符號與單位
- 符號：$\\omega$
- SI 單位：rad/s

## 相關連結
- [[角加速度]]
- [[轉動慣量]]
- [[滾動運動]]
""",
    "03_quantities/角加速度.md": """---
type: quantity
title: 角加速度
symbol: \\alpha
unit: rad/s^2
dimension: T^-2
domain: 力學
summary: 角加速度描述角速度隨時間的變化，是轉動版的加速度。
related_concepts: ["[[角速度]]", "[[轉動慣量]]"]
related_laws: []
measurement_methods: []
tags: [physics, mechanics, quantity]
updated: 2026-06-02
---

# 角加速度

## 定義
角加速度是角速度對時間的變化率，描述轉動快慢如何改變。

## 數學表達
$$
\\alpha = \\frac{d\\omega}{dt}
$$

## 符號與單位
- 符號：$\\alpha$
- SI 單位：rad/s$^2$

## 相關連結
- [[角速度]]
- [[轉動慣量]]
""",
    "03_quantities/轉動慣量.md": """---
type: quantity
title: 轉動慣量
symbol: I
unit: kg\\cdot m^2
dimension: M L^2
domain: 力學
summary: 轉動慣量量化物體對角加速度的抗拒程度，是轉動版的慣性質量。
related_concepts: ["[[角速度]]", "[[角加速度]]", "[[轉動動能]]"]
related_laws: []
measurement_methods: []
tags: [physics, mechanics, quantity]
updated: 2026-06-02
---

# 轉動慣量

## 定義
轉動慣量描述質量相對轉軸的分布如何影響物體改變轉動狀態的難易程度。

## 數學表達
對質點系統，
$$
I = \\sum m_i r_i^2
$$

連續體則寫成
$$
I = \\int r^2\\,dm
$$

## 符號與單位
- 符號：$I$
- SI 單位：kg·m$^2$

## 相關連結
- [[角速度]]
- [[角加速度]]
- [[轉動動能]]
- [[轉矩]]
""",
    "03_quantities/轉動動能.md": """---
type: quantity
title: 轉動動能
symbol: K_{rot}
unit: J
dimension: M L^2 T^-2
domain: 力學
summary: 轉動動能是物體因轉動而具有的能量，與轉動慣量和角速度有關。
related_concepts: ["[[轉動慣量]]", "[[角速度]]", "[[滾動運動]]"]
related_laws: []
measurement_methods: []
tags: [physics, mechanics, quantity]
updated: 2026-06-02
---

# 轉動動能

## 定義
當物體繞軸轉動時，除了平移動能之外，還可能具有轉動動能。

## 數學表達
$$
K_{rot} = \\frac{1}{2}I\\omega^2
$$

## 符號與單位
- 符號：$K_{rot}$
- SI 單位：J

## 相關連結
- [[轉動慣量]]
- [[角速度]]
- [[滾動運動]]
""",
    "02_concepts/滾動運動.md": """---
type: concept
title: 滾動運動
domain: 力學
summary: 滾動運動同時包含平移與轉動，是連接剛體運動學與能量分析的重要主題。
prerequisites: ["[[角速度]]", "[[轉動動能]]", "[[速度]]"]
related_laws: []
related_quantities: ["[[角速度]]", "[[轉動動能]]"]
related_concepts: ["[[轉動慣量]]", "[[機械能守恆]]"]
math_tools: []
tags: [physics, mechanics, concept]
updated: 2026-06-02
---

# 滾動運動

## 核心想法
滾動運動不是單純平移加上單純轉動的鬆散拼裝，而是兩者之間存在幾何約束。

## 無滑動條件
若純滾動且不打滑，則滿足
$$
v_{cm} = \\omega R
$$

## 物理解讀
滾動問題的關鍵在於能量與運動學都要同時顧到。只看平移或只看轉動，通常都不夠。

## 相關連結
- [[角速度]]
- [[轉動動能]]
- [[轉動慣量]]
- [[機械能守恆]]
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
