#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


NOTES: dict[str, str] = {
    "02_concepts/RLC電路.md": """---
type: concept
title: RLC電路
domain: 電磁學
summary: RLC電路同時包含電阻、電感與電容器，是研究交流共振、頻率響應與阻尼的標準模型。
prerequisites: ["[[電阻]]", "[[電感]]", "[[電容器]]", "[[交流電]]"]
related_laws: ["[[歐姆定律]]"]
related_quantities: ["[[阻抗]]", "[[感抗]]", "[[電容抗]]"]
related_concepts: ["[[RL電路]]", "[[RC電路]]", "[[變壓器]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-03
---

# RLC電路

## 核心想法
RLC電路把耗散、磁場儲能與電場儲能放進同一系統，因此能展現共振、阻尼與選頻等純電阻電路沒有的行為。

## 物理解讀
[[電阻]] 決定能量如何被耗散；[[電感]] 把能量暫存在磁場；[[電容器]] 則把能量暫存在電場。三者的拉扯決定了整個交流回應。

## 分析重點
- 總 [[阻抗]] 隨頻率改變。
- [[感抗]] 與 [[電容抗]] 可能互相抵消。
- 在特定頻率附近，系統會出現共振。

## 相關連結
- [[交流電]]
- [[阻抗]]
- [[感抗]]
- [[電容抗]]
- [[RL電路]]
- [[RC電路]]
""",
    "02_concepts/熱膨脹.md": """---
type: concept
title: 熱膨脹
domain: 熱力學
summary: 熱膨脹描述物體因溫度上升而尺寸增加的現象，是熱學與材料性質的基本橋接主題。
prerequisites: ["[[溫度]]", "[[熱]]"]
related_laws: []
related_quantities: []
related_concepts: ["[[彈性]]"]
math_tools: []
tags: [physics, thermodynamics, concept]
updated: 2026-06-03
---

# 熱膨脹

## 核心想法
溫度升高時，粒子的平均振動幅度增加，材料的平均間距通常也跟著增加，因此巨觀尺寸會膨脹。

## 典型關係
對線膨脹，可寫成
$$
\\Delta L = \\alpha L_0 \\Delta T
$$

## 物理解讀
熱膨脹不是所有材料都一樣大，也不是任何溫度範圍都精確線性。線性公式只是小溫差下的常用近似。

## 相關連結
- [[溫度]]
- [[熱]]
- [[彈性]]
""",
    "02_concepts/熱機.md": """---
type: concept
title: 熱機
domain: 熱力學
summary: 熱機把高溫熱源提供的部分熱量轉換為機械功，是熱力學定律的經典應用。
prerequisites: ["[[熱力學第一定律]]", "[[熱力學第二定律]]", "[[卡諾循環]]"]
related_laws: ["[[熱力學第一定律]]", "[[熱力學第二定律]]"]
related_quantities: ["[[效率]]"]
related_concepts: ["[[卡諾循環]]"]
math_tools: []
tags: [physics, thermodynamics, concept]
updated: 2026-06-03
---

# 熱機

## 核心想法
熱機從高溫熱源吸熱，排出一部分熱到低溫熱源，剩下的部分才有機會轉成有用的機械功。

## 物理解讀
[[熱力學第一定律]] 告訴你能量如何記帳；[[熱力學第二定律]] 告訴你不可能把吸進來的熱百分之百全變成功。

## 典型關係
若吸收熱量為 $Q_H$，排出熱量為 $Q_C$，輸出功為 $W$，則
$$
W = Q_H - Q_C
$$

## 相關連結
- [[熱力學第一定律]]
- [[熱力學第二定律]]
- [[效率]]
- [[卡諾循環]]
""",
    "03_quantities/效率.md": """---
type: quantity
title: 效率
symbol: \\eta
unit: 1
dimension: 1
domain: 熱力學
summary: 效率表示系統把輸入能量轉成有用輸出的比例，是分析熱機與能量轉換裝置的核心量。
related_concepts: ["[[熱機]]", "[[卡諾循環]]"]
related_laws: ["[[熱力學第二定律]]"]
measurement_methods: []
tags: [physics, thermodynamics, quantity]
updated: 2026-06-03
---

# 效率

## 定義
效率量化輸出中真正有用的部分占輸入總量的比例。

## 數學表達
對熱機，
$$
\\eta = \\frac{W}{Q_H} = 1 - \\frac{Q_C}{Q_H}
$$

## 符號與單位
- 符號：$\\eta$
- 無因次

## 物理解讀
效率高不代表能量憑空增加，只代表損失占比更小。[[熱力學第二定律]] 直接限制了熱機效率不可能任意接近 100%。

## 相關連結
- [[熱機]]
- [[卡諾循環]]
- [[熱力學第二定律]]
""",
    "03_quantities/波速.md": """---
type: quantity
title: 波速
symbol: v
unit: m/s
dimension: L T^-1
domain: 振動與波動
summary: 波速描述波形在介質或空間中傳播的速度，是波動分析的基本量。
related_concepts: ["[[機械波]]", "[[聲波]]"]
related_laws: []
measurement_methods: []
tags: [physics, waves, quantity]
updated: 2026-06-03
---

# 波速

## 定義
波速表示相位或擾動在空間中前進的速度。

## 數學表達
$$
v = f\\lambda
$$

## 符號與單位
- 符號：$v$
- SI 單位：m/s

## 相關連結
- [[波長]]
- [[頻率]]
- [[機械波]]
- [[聲波]]
""",
    "03_quantities/波長.md": """---
type: quantity
title: 波長
symbol: \\lambda
unit: m
dimension: L
domain: 振動與波動
summary: 波長是波在空間中一個完整週期所對應的長度，是波動結構的基本尺度。
related_concepts: ["[[機械波]]", "[[聲波]]"]
related_laws: []
measurement_methods: []
tags: [physics, waves, quantity]
updated: 2026-06-03
---

# 波長

## 定義
波長是相鄰同相位兩點之間的距離，例如相鄰波峰之間的距離。

## 符號與單位
- 符號：$\\lambda$
- SI 單位：m

## 相關連結
- [[波速]]
- [[頻率]]
- [[機械波]]
- [[聲波]]
""",
    "03_quantities/頻率.md": """---
type: quantity
title: 頻率
symbol: f
unit: Hz
dimension: T^-1
domain: 振動與波動
summary: 頻率表示每秒完成多少次振動或週期，是連接時間尺度與波動尺度的核心量。
related_concepts: ["[[機械波]]", "[[聲波]]", "[[交流電]]"]
related_laws: []
measurement_methods: []
tags: [physics, waves, quantity]
updated: 2026-06-03
---

# 頻率

## 定義
頻率表示單位時間內完成的週期數。

## 數學表達
$$
f = \\frac{1}{T}
$$

## 符號與單位
- 符號：$f$
- SI 單位：Hz

## 相關連結
- [[波速]]
- [[波長]]
- [[機械波]]
- [[聲波]]
- [[交流電]]
""",
    "03_quantities/折射率.md": """---
type: quantity
title: 折射率
symbol: n
unit: 1
dimension: 1
domain: 光學
summary: 折射率量化光在介質中的傳播速度相對於真空的減慢程度，是幾何光學的核心參數。
related_concepts: ["[[折射定律]]", "[[惠更斯原理]]"]
related_laws: ["[[折射定律]]"]
measurement_methods: []
tags: [physics, optics, quantity]
updated: 2026-06-03
---

# 折射率

## 定義
折射率定義為真空中光速與介質中光速的比值。

## 數學表達
$$
n = \\frac{c}{v}
$$

## 符號與單位
- 符號：$n$
- 無因次

## 物理解讀
折射率越大，表示光在介質中傳得越慢，光線偏折的程度通常也越顯著。

## 相關連結
- [[折射定律]]
- [[惠更斯原理]]
""",
    "02_concepts/薄膜干涉.md": """---
type: concept
title: 薄膜干涉
domain: 光學
summary: 薄膜干涉描述光在薄層介質上下表面反射後產生的相位差與干涉現象。
prerequisites: ["[[干涉]]", "[[折射率]]", "[[波長]]"]
related_laws: []
related_quantities: ["[[波長]]", "[[折射率]]"]
related_concepts: ["[[雙縫干涉]]"]
math_tools: []
tags: [physics, optics, concept]
updated: 2026-06-03
---

# 薄膜干涉

## 核心想法
當光在薄膜上下表面反射時，兩束反射光會因路徑差與相位反轉產生干涉，形成明暗或彩色條紋。

## 物理解讀
薄膜干涉的難點不在「會不會干涉」，而在你有沒有把額外光程與反射相位反轉都算進去。

## 相關連結
- [[干涉]]
- [[折射率]]
- [[波長]]
- [[雙縫干涉]]
""",
    "02_concepts/單縫繞射.md": """---
type: concept
title: 單縫繞射
domain: 光學
summary: 單縫繞射描述光通過有限寬度狹縫後形成的擴散與明暗分布，是波動光學的經典模型。
prerequisites: ["[[繞射]]", "[[波長]]"]
related_laws: []
related_quantities: ["[[波長]]"]
related_concepts: ["[[雙縫干涉]]"]
math_tools: []
tags: [physics, optics, concept]
updated: 2026-06-03
---

# 單縫繞射

## 核心想法
狹縫本身不是一個純幾何洞，而是會把入射波重新分佈成具有角度展開的波前，因此屏幕上會出現中央亮紋與側邊次亮紋。

## 典型條件
暗紋條件可寫成
$$
a\\sin\\theta = m\\lambda, \\quad m=1,2,3,\\dots
$$

## 相關連結
- [[繞射]]
- [[波長]]
- [[雙縫干涉]]
""",
    "02_concepts/雙縫干涉.md": """---
type: concept
title: 雙縫干涉
domain: 光學
summary: 雙縫干涉描述兩個相干波源疊加後形成規律明暗條紋，是波動性最經典的展示之一。
prerequisites: ["[[干涉]]", "[[波長]]"]
related_laws: []
related_quantities: ["[[波長]]"]
related_concepts: ["[[薄膜干涉]]", "[[單縫繞射]]"]
math_tools: []
tags: [physics, optics, concept]
updated: 2026-06-03
---

# 雙縫干涉

## 核心想法
兩道相干波從不同狹縫出發後，在屏幕上不同位置會因路徑差不同而形成相長或相消干涉。

## 典型條件
亮紋條件為
$$
d\\sin\\theta = m\\lambda
$$

## 物理解讀
雙縫干涉之所以重要，不只是它會出條紋，而是它直接暴露出波的相位疊加結構。

## 相關連結
- [[干涉]]
- [[波長]]
- [[薄膜干涉]]
- [[單縫繞射]]
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
