#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


NOTES: dict[str, str] = {
    "02_concepts/碰撞.md": """---
type: concept
title: 碰撞
domain: 力學
summary: 碰撞研究物體在短時間強作用下如何交換動量與能量，是動量守恆應用的核心主題。
prerequisites: ["[[動量]]", "[[動量守恆]]"]
related_laws: ["[[動量守恆]]"]
related_quantities: ["[[動量]]", "[[動能]]"]
related_concepts: ["[[角動量與碰撞]]"]
math_tools: []
tags: [physics, mechanics, concept]
updated: 2026-06-02
---

# 碰撞

## 核心想法
碰撞問題的關鍵不在碰得多大聲，而在作用時間極短時，哪些量仍然能當成近似守恆。

## 物理解讀
對封閉系統而言，[[動量守恆]] 幾乎總是主角；動能是否守恆，則取決於碰撞是否為彈性碰撞。

## 相關連結
- [[動量]]
- [[動量守恆]]
- [[動能]]
- [[角動量與碰撞]]
""",
    "03_quantities/角位移.md": """---
type: quantity
title: 角位移
symbol: \\theta
unit: rad
dimension: 1
domain: 力學
summary: 角位移描述物體繞固定軸轉過的角度，是轉動運動學最基本的量。
related_concepts: ["[[定軸轉動運動學]]"]
related_laws: []
measurement_methods: []
tags: [physics, mechanics, quantity]
updated: 2026-06-02
---

# 角位移

## 定義
角位移表示物體繞某轉軸從初始方向轉到末端方向的改變量。

## 符號與單位
- 符號：$\\theta$
- SI 單位：rad

## 相關連結
- [[定軸轉動運動學]]
- [[角速度]]
- [[角加速度]]
""",
    "02_concepts/定軸轉動運動學.md": """---
type: concept
title: 定軸轉動運動學
domain: 力學
summary: 定軸轉動運動學研究剛體繞固定轉軸時的角位移、角速度與角加速度關係。
prerequisites: ["[[角位移]]", "[[角速度]]", "[[角加速度]]"]
related_laws: []
related_quantities: ["[[角位移]]", "[[角速度]]", "[[角加速度]]"]
related_concepts: ["[[轉動運動學方程]]", "[[滾動運動]]"]
math_tools: []
tags: [physics, mechanics, concept]
updated: 2026-06-02
---

# 定軸轉動運動學

## 核心想法
定軸轉動運動學就是把直線運動學的語言轉到旋轉問題：位置換成角位移，速度換成角速度，加速度換成角加速度。

## 物理解讀
只要轉軸固定，很多問題都能被壓縮成一維角變數分析。真正的難點通常不在運動學，而在後續動力學與能量連結。

## 相關連結
- [[角位移]]
- [[角速度]]
- [[角加速度]]
- [[轉動運動學方程]]
- [[滾動運動]]
""",
    "01_laws/轉動運動學方程.md": """---
type: law
title: 轉動運動學方程
domain: 力學
summary: 在角加速度為常數時，轉動運動學方程給出角位移、角速度與時間之間的標準關係。
applicability: 適用於定軸轉動且角加速度可視為常數的情況。
prerequisites: ["[[角位移]]", "[[角速度]]", "[[角加速度]]"]
related_concepts: ["[[定軸轉動運動學]]"]
related_quantities: ["[[角位移]]", "[[角速度]]", "[[角加速度]]"]
related_laws: []
experiments: []
math_tools: []
derived_results: []
modern_connections: []
tags: [physics, mechanics, law]
updated: 2026-06-02
---

# 轉動運動學方程

## 敘述
若角加速度為常數，轉動問題就有一套與等加速度直線運動平行的標準方程。

## 數學表達
$$
\\omega = \\omega_0 + \\alpha t
$$

$$
\\theta = \\theta_0 + \\omega_0 t + \\frac{1}{2}\\alpha t^2
$$

$$
\\omega^2 = \\omega_0^2 + 2\\alpha(\\theta - \\theta_0)
$$

## 相關連結
- [[定軸轉動運動學]]
- [[角位移]]
- [[角速度]]
- [[角加速度]]
""",
    "02_concepts/角動量與碰撞.md": """---
type: concept
title: 角動量與碰撞
domain: 力學
summary: 角動量與碰撞研究粒子或剛體在碰撞過程中如何以角動量守恆約束碰後運動。
prerequisites: ["[[角動量守恆]]", "[[碰撞]]", "[[轉動慣量]]"]
related_laws: ["[[角動量守恆]]"]
related_quantities: ["[[角動量]]", "[[轉動慣量]]"]
related_concepts: ["[[滾動運動]]"]
math_tools: ["[[向量]]"]
tags: [physics, mechanics, concept]
updated: 2026-06-02
---

# 角動量與碰撞

## 核心想法
碰撞問題若涉及偏心撞擊或碰後轉動，只看線動量往往不夠，還必須同時顧到角動量。

## 物理解讀
選對轉軸可以讓外衝量矩消失，這時 [[角動量守恆]] 會比直接硬算力還乾淨得多。

## 相關連結
- [[角動量守恆]]
- [[碰撞]]
- [[角動量]]
- [[轉動慣量]]
""",
    "02_concepts/軌道角動量.md": """---
type: concept
title: 軌道角動量
domain: 力學
summary: 軌道角動量描述物體繞某參考點運動時的角動量，是中心力與軌道運動的核心量。
prerequisites: ["[[角動量]]", "[[萬有引力定律]]", "[[向量]]"]
related_laws: ["[[角動量守恆]]"]
related_quantities: ["[[角動量]]"]
related_concepts: ["[[重力]]"]
math_tools: ["[[向量]]"]
tags: [physics, mechanics, concept]
updated: 2026-06-02
---

# 軌道角動量

## 核心想法
當物體不是原地自轉，而是繞某點公轉時，它仍然有角動量，這就是軌道角動量。

## 數學表達
對質點，
$$
\\vec L = \\vec r \\times \\vec p
$$

## 物理解讀
在中心力問題中，力與位置向量平行，因此外轉矩為零，這就是軌道角動量守恆的根源。

## 相關連結
- [[角動量]]
- [[角動量守恆]]
- [[萬有引力定律]]
- [[重力]]
""",
    "03_quantities/比熱.md": """---
type: quantity
title: 比熱
symbol: c
unit: J/(kg\\cdot K)
dimension: L^2 T^-2 \\Theta^-1
domain: 熱力學
summary: 比熱量化單位質量物質升高單位溫度所需的熱量，是熱學最基本的材料參數之一。
related_concepts: ["[[熱]]", "[[溫度]]", "[[理想氣體]]"]
related_laws: ["[[熱力學第一定律]]"]
measurement_methods: []
tags: [physics, thermodynamics, quantity]
updated: 2026-06-02
---

# 比熱

## 定義
比熱表示每單位質量的物質，溫度升高一單位所需吸收的熱量。

## 數學表達
$$
Q = mc\\Delta T
$$

## 符號與單位
- 符號：$c$
- SI 單位：J/(kg·K)

## 相關連結
- [[熱]]
- [[溫度]]
- [[熱力學第一定律]]
""",
    "02_concepts/潛熱.md": """---
type: concept
title: 潛熱
domain: 熱力學
summary: 潛熱描述物質在相變過程中於溫度不變時吸收或放出的熱量。
prerequisites: ["[[熱]]", "[[溫度]]"]
related_laws: ["[[熱力學第一定律]]"]
related_quantities: ["[[比熱]]"]
related_concepts: []
math_tools: []
tags: [physics, thermodynamics, concept]
updated: 2026-06-02
---

# 潛熱

## 核心想法
物質在熔化、汽化等相變過程中，即使溫度不變，也可能持續吸收或放出熱量。這部分能量就是潛熱。

## 數學表達
$$
Q = mL
$$

## 相關連結
- [[熱]]
- [[溫度]]
- [[熱力學第一定律]]
""",
    "02_concepts/理想氣體.md": """---
type: concept
title: 理想氣體
domain: 熱力學
summary: 理想氣體模型把分子視為體積可忽略、只在碰撞時交互作用的粒子，是熱學與統計物理的基礎近似。
prerequisites: ["[[溫度]]", "[[壓力]]", "[[分子運動論]]"]
related_laws: ["[[熱力學第一定律]]"]
related_quantities: []
related_concepts: ["[[狀態方程]]", "[[內能]]"]
math_tools: []
tags: [physics, thermodynamics, concept]
updated: 2026-06-02
---

# 理想氣體

## 核心想法
理想氣體模型故意忽略分子體積與長程交互作用，留下最乾淨的壓力、體積、溫度關係。

## 物理解讀
這不是世界真相，而是一個極有用的近似。很多熱學公式之所以能寫得這麼漂亮，就是靠這個近似撐起來的。

## 相關連結
- [[溫度]]
- [[壓力]]
- [[分子運動論]]
- [[狀態方程]]
- [[內能]]
""",
    "01_laws/狀態方程.md": """---
type: law
title: 狀態方程
domain: 熱力學
summary: 理想氣體狀態方程把壓力、體積、溫度與粒子數連成單一關係，是氣體模型的核心方程。
applicability: 適用於理想氣體近似下的平衡態問題。
prerequisites: ["[[理想氣體]]", "[[壓力]]", "[[溫度]]"]
related_concepts: ["[[分子運動論]]"]
related_quantities: []
related_laws: []
experiments: []
math_tools: []
derived_results: []
modern_connections: []
tags: [physics, thermodynamics, law]
updated: 2026-06-02
---

# 狀態方程

## 敘述
理想氣體的壓力、體積與溫度並不是彼此獨立，而是滿足單一狀態方程。

## 數學表達
$$
PV = nRT
$$

## 物理解讀
這條式子把巨觀量連在一起，但它背後的微觀圖像來自 [[分子運動論]]。

## 相關連結
- [[理想氣體]]
- [[壓力]]
- [[溫度]]
- [[分子運動論]]
""",
    "02_concepts/分子運動論.md": """---
type: concept
title: 分子運動論
domain: 熱力學
summary: 分子運動論用大量微觀粒子的運動來解釋氣體的壓力、溫度與內能，是理想氣體模型的微觀基礎。
prerequisites: ["[[理想氣體]]", "[[動能]]"]
related_laws: ["[[狀態方程]]"]
related_quantities: ["[[溫度]]"]
related_concepts: ["[[內能]]"]
math_tools: []
tags: [physics, thermodynamics, concept]
updated: 2026-06-02
---

# 分子運動論

## 核心想法
分子運動論把氣體視為大量粒子不停運動與碰撞的集合，壓力來自粒子撞牆，溫度則和平均動能相關。

## 物理解讀
這套觀點把巨觀熱學和微觀力學接起來。你不再只看到公式，而是知道這些公式為什麼長這樣。

## 相關連結
- [[理想氣體]]
- [[狀態方程]]
- [[動能]]
- [[內能]]
- [[溫度]]
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
