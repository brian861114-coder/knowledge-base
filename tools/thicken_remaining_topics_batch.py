#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


NOTES: dict[str, str] = {
    "02_concepts/RLC電路.md": """---
type: concept
title: RLC電路
domain: 電磁學
summary: RLC電路同時包含電阻、電感與電容器，是交流共振、阻尼與頻率選擇現象的標準模型。
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
RLC電路把 [[電阻]]、[[電感]] 與 [[電容器]] 放進同一回路，因此系統同時具有耗散、磁場儲能與電場儲能三種行為。這使它成為交流與共振分析最標準的模型。

## 物理解讀
[[電阻]] 會把能量耗散成熱；[[電感]] 傾向維持電流；[[電容器]] 傾向維持電壓。當交流頻率改變時，這三種效應的相對強弱也會跟著改變，所以總響應絕不會像直流電路那樣單純。

## 頻率響應
在串聯 RLC 模型中，總 [[阻抗]] 可寫成
$$
Z = \\sqrt{R^2 + (X_L - X_C)^2}
$$
其中 $X_L$ 為 [[感抗]]，$X_C$ 為 [[電容抗]]。

## 共振觀點
當感抗與電容抗彼此抵消時，系統的總阻抗降到特別小，電流響應變得特別強，這就是共振。共振不是魔法，只是儲存在磁場與電場中的能量剛好以特定節奏交換。

## 典型用途
- 選頻電路
- 濾波器
- 諧振器
- 交流暫態與穩態分析

## 常見誤解
- 以為 RLC 只是把三個元件串起來。真正重要的是它如何產生頻率選擇與相位結構。
- 只記阻抗公式，卻不理解共振時能量在電感與電容之間來回交換。

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
summary: 熱膨脹描述材料因溫度上升而尺寸增加的現象，是熱學、材料性質與工程應用之間的橋接主題。
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
溫度升高時，粒子的平均振動幅度增加，材料內部的平均間距通常也跟著變大，因此巨觀尺寸會膨脹。這是從微觀熱運動直接長到巨觀形變的現象。

## 典型關係
對線膨脹，可近似寫成
$$
\\Delta L = \\alpha L_0 \\Delta T
$$
其中 $\\alpha$ 為線膨脹係數。

## 面積與體積觀點
若溫差不大，面積與體積也會隨溫度改變，只是對應的膨脹係數不同。這也是橋梁、鐵軌與容器設計必須預留伸縮空間的理由。

## 物理解讀
熱膨脹不是每種材料都一樣大，也不是任何溫度範圍都線性。線性膨脹公式只是小溫差與普通材料下的近似模型。

## 常見誤解
- 把熱膨脹當成材料一定「變軟」。膨脹和材料剛性不是同一件事。
- 以為固體、液體、氣體都遵守同一個簡單線性公式。實際上只有某些情況能這樣近似。

## 相關連結
- [[溫度]]
- [[熱]]
- [[彈性]]
""",
    "02_concepts/熱機.md": """---
type: concept
title: 熱機
domain: 熱力學
summary: 熱機把高溫熱源提供的部分熱量轉換為機械功，是熱力學第一、第二定律的經典應用。
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
熱機從高溫熱源吸收熱量，把其中一部分轉成有用功，另一部分則必須排到低溫熱源。這不是技術限制而已，而是熱力學結構本身逼出來的結果。

## 能量記帳
若吸收熱量為 $Q_H$，排出熱量為 $Q_C$，輸出功為 $W$，則
$$
W = Q_H - Q_C
$$
這是 [[熱力學第一定律]] 的直接記帳。

## 為什麼不能全轉成功
[[熱力學第二定律]] 告訴你，不可能把從單一熱源吸收的熱量百分之百轉成機械功。換句話說，排熱不是工程師偷懶，而是自然規則。

## 物理解讀
熱機的本質不是「會動的機器」，而是利用溫差來驅動循環過程。沒有溫差，熱機就沒有方向。

## 典型例子
- 蒸汽機
- 內燃機
- 渦輪機

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
summary: 效率量化系統把輸入能量轉成有用輸出的比例，是分析熱機與能量轉換裝置的核心量。
related_concepts: ["[[熱機]]", "[[卡諾循環]]"]
related_laws: ["[[熱力學第二定律]]"]
measurement_methods: []
tags: [physics, thermodynamics, quantity]
updated: 2026-06-03
---

# 效率

## 定義
效率描述輸入能量中有多少比例最後變成我們真正想要的輸出。

## 數學表達
對熱機，
$$
\\eta = \\frac{W}{Q_H} = 1 - \\frac{Q_C}{Q_H}
$$

## 符號與單位
- 符號：$\\eta$
- 無因次

## 物理解讀
效率不是越靠近 1 越理所當然。對熱機而言，[[熱力學第二定律]] 明確限制了效率上限，而 [[卡諾循環]] 則提供理想上界。

## 常見誤解
- 把效率低視為純技術失誤。很多情況下，低於 100% 不是缺陷，而是自然律要求。
- 忘記效率只看比例，不直接告訴你總輸出功率大小。

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
summary: 波速描述波形在介質或空間中傳播的速度，是波動分析最基本的量之一。
related_concepts: ["[[機械波]]", "[[聲波]]"]
related_laws: []
measurement_methods: []
tags: [physics, waves, quantity]
updated: 2026-06-03
---

# 波速

## 定義
波速表示某個波形特徵，例如波峰、固定相位面或擾動前沿，在空間中前進的速度。

## 數學表達
$$
v = f\\lambda
$$

## 符號與單位
- 符號：$v$
- SI 單位：m/s

## 物理解讀
波速由介質性質決定，不一定等於介質粒子的運動速度。這是很多初學者會搞混的地方。

## 常見誤解
- 把波速與粒子振動速度當成同一件事。
- 認為頻率越高波一定傳得越快。對很多介質中的線性波，波速主要由介質決定。

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
summary: 波長是波在空間中一個完整週期對應的長度，是波動結構最直觀的尺度。
related_concepts: ["[[機械波]]", "[[聲波]]"]
related_laws: []
measurement_methods: []
tags: [physics, waves, quantity]
updated: 2026-06-03
---

# 波長

## 定義
波長是相鄰同相位兩點之間的距離，例如相鄰波峰或相鄰波谷之間的距離。

## 與其他量的關係
波長與 [[頻率]]、[[波速]] 之間滿足
$$
v = f\\lambda
$$

## 符號與單位
- 符號：$\\lambda$
- SI 單位：m

## 物理解讀
波長短不一定代表波比較「強」，而是代表空間週期更短。光學中的干涉與繞射尺度往往直接受波長支配。

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
頻率表示單位時間內完成的週期數，是振動與波動最基本的時間尺度。

## 數學表達
$$
f = \\frac{1}{T}
$$

## 符號與單位
- 符號：$f$
- SI 單位：Hz

## 物理解讀
在給定介質中，若波速固定，頻率越高通常意味著 [[波長]] 越短。對 [[交流電]] 而言，頻率還會直接影響阻抗、感抗與電容抗。

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
折射率定義為真空中光速與介質中光速的比值：
$$
n = \\frac{c}{v}
$$

## 符號與單位
- 符號：$n$
- 無因次

## 物理解讀
折射率越大，表示光在該介質中傳得越慢。這個量不只是查表常數，它直接控制光線偏折、全反射條件與薄膜干涉的相位結構。

## 與折射現象的關係
[[折射定律]] 可寫成
$$
n_1\\sin\\theta_1 = n_2\\sin\\theta_2
$$
因此折射率差異越大，光路偏折效果通常越明顯。

## 相關連結
- [[折射定律]]
- [[惠更斯原理]]
- [[薄膜干涉]]
""",
    "02_concepts/薄膜干涉.md": """---
type: concept
title: 薄膜干涉
domain: 光學
summary: 薄膜干涉描述光在薄層介質上下表面反射後產生的相位差與干涉現象，是波動光學的重要模型。
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
當光在薄膜上下表面反射時，會產生兩束具有路徑差的反射光。這兩束光再疊加時，就會因相位差不同而形成亮紋、暗紋或彩色圖樣。

## 為什麼不只是路徑差
薄膜干涉的坑在於：除了幾何路徑差，反射時是否發生相位反轉也必須算進去。少算這件事，答案通常整組錯掉。

## 典型應用
- 肥皂泡彩紋
- 鍍膜鏡面
- 抗反射鍍膜

## 物理解讀
薄膜干涉是把 [[折射率]]、[[波長]] 與相位條件一起綁進真實現象的典型範例，因此它比純雙縫問題更接近工程與自然界。

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
狹縫不是理想幾何開口而已，它會把入射波重新分佈成具有角度展開的波前，因此屏幕上會出現中央亮紋與兩側次亮紋。

## 暗紋條件
對寬度為 $a$ 的單縫，暗紋條件可寫成
$$
a\\sin\\theta = m\\lambda, \\quad m=1,2,3,\\dots
$$

## 物理解讀
中央亮紋特別寬，正是單縫繞射最顯眼的特徵之一。這也說明波長越長、狹縫越窄，繞射展開越明顯。

## 與干涉的差別
雙縫干涉主要看兩個波源的疊加；單縫繞射則是同一個有限開口內部各部分波前的自我疊加。

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
當兩道相干波從不同狹縫出發，在屏幕上不同位置重疊時，因路徑差不同而形成相長或相消干涉，於是出現規律亮暗條紋。

## 典型條件
亮紋條件為
$$
d\\sin\\theta = m\\lambda
$$
暗紋條件則對應半整數倍波長的路徑差。

## 物理解讀
雙縫干涉的重要性不在於它「很漂亮」，而在於它直接把相位疊加、相干條件與波長尺度全部攤在你面前。

## 與單縫的關係
真實雙縫圖樣其實常疊在單縫繞射包絡之下，因此干涉與繞射在實驗上不是完全分家的兩件事。

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
