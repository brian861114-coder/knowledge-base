#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


NOTES: dict[str, str] = {
    "02_concepts/非保守力.md": """---
type: concept
title: 非保守力
domain: 力學
summary: 非保守力做功通常依賴路徑，並會讓機械能不再單純以動能和位能彼此交換。
prerequisites: ["[[保守力]]", "[[力]]", "[[位能]]"]
related_laws: ["[[機械能守恆]]"]
related_quantities: []
related_concepts: ["[[保守力]]", "[[耗散]]", "[[黏滯力]]"]
math_tools: []
tags: [physics, mechanics, concept]
updated: 2026-06-04
---

# 非保守力

## 概念摘要
非保守力是做功結果依賴路徑的力。你把物體從 A 搬到 B，走不同路徑，這類力可能做出不同總功，這就和 [[保守力]] 根本不是同一類東西。

## 和保守力的差別
保守力可由位能函數描述，非保守力通常不行。前者常把能量在動能和位能之間搬來搬去；後者則常把可用機械能抽走，轉成熱或其他形式。

## 常見例子
- 摩擦力
- 空氣阻力
- 黏滯阻力

## 物理直覺
非保守力的核心不是「壞力」，而是它會讓系統記得你怎麼走過來。只要歷程有差，結果就可能不同。

## 相關概念
- [[保守力]]
- [[耗散]]
- [[黏滯力]]
""",
    "02_concepts/耗散.md": """---
type: concept
title: 耗散
domain: 力學
summary: 耗散描述系統中可用機械能逐步轉為較難回收的形式，例如熱，使得宏觀有序運動衰減。
prerequisites: ["[[非保守力]]", "[[能量]]"]
related_laws: []
related_quantities: []
related_concepts: ["[[非保守力]]", "[[阻尼振動]]", "[[黏滯力]]", "[[熵]]"]
math_tools: []
tags: [physics, mechanics, concept]
updated: 2026-06-04
---

# 耗散

## 概念摘要
耗散是指有序的宏觀能量逐步流向不容易直接回收的形式，最常見的是熱。這會讓運動衰減、振幅下降、流體動能被磨掉。

## 典型來源
- 摩擦
- 黏滯
- 電阻損耗
- 材料內部阻尼

## 在振動中的角色
如果系統存在明顯耗散，理想的永久振盪通常就不存在，最後會看到 [[阻尼振動]] 或需要外界持續餵能量的 [[受迫振動]]。

## 物理直覺
耗散不是能量消失，而是能量變得分散、碎裂、難以重新集中成你想要的宏觀運動。

## 相關概念
- [[非保守力]]
- [[阻尼振動]]
- [[熵]]
""",
    "02_concepts/不穩定平衡.md": """---
type: concept
title: 不穩定平衡
domain: 力學
summary: 不穩定平衡是系統在平衡點附近只要受到微小擾動，就會偏離原位置而不是回復的平衡型態。
prerequisites: ["[[穩定平衡]]", "[[有效位能]]"]
related_laws: []
related_quantities: []
related_concepts: ["[[穩定平衡]]", "[[平衡]]", "[[有效位能]]"]
math_tools: []
tags: [physics, mechanics, concept]
updated: 2026-06-04
---

# 不穩定平衡

## 概念摘要
不穩定平衡是看起來平衡、但其實一碰就倒的狀態。系統在該點附近若受微小擾動，不會被拉回去，反而會越跑越遠。

## 位能視角
若用位能看，不穩定平衡常對應局部極大點。球放在山頂就是標準例子，看似靜止，但那只是暫時沒人碰它。

## 和穩定平衡的差別
[[穩定平衡]] 對小擾動有回復傾向；不穩定平衡則對小擾動有放大傾向。

## 物理直覺
平衡不等於安全。很多系統在某一瞬間合力為零，但只要曲率方向錯了，平衡點就只是懸在崩潰邊緣。

## 相關概念
- [[穩定平衡]]
- [[平衡]]
- [[有效位能]]
""",
    "02_concepts/章動.md": """---
type: concept
title: 章動
domain: 力學
summary: 章動是轉動軸在進動之外額外出現的週期性擺動或起伏，常見於受力不完全對稱的陀螺與天體轉動問題。
prerequisites: ["[[進動]]", "[[角動量]]", "[[轉矩]]"]
related_laws: ["[[角動量定理]]"]
related_quantities: ["[[角動量]]"]
related_concepts: ["[[進動]]", "[[陀螺]]"]
math_tools: []
tags: [physics, mechanics, concept]
updated: 2026-06-04
---

# 章動

## 概念摘要
章動是轉動軸在 [[進動]] 之外，還伴隨額外上下擺動或振幅起伏的現象。簡單說，進動像是在繞圈，章動則是那個繞圈本身還在顫。

## 為什麼會出現
若角動量、幾何軸與外力矩條件無法形成乾淨穩定的單一圓錐運動，就可能疊出章動。

## 和進動的差別
[[進動]] 強調轉動軸方向緩慢繞轉；章動則強調這個繞轉過程中還有週期性起伏。

## 相關概念
- [[進動]]
- [[陀螺]]
- [[角動量]]
""",
    "02_concepts/滾動.md": """---
type: concept
title: 滾動
domain: 力學
summary: 滾動是物體平動與轉動耦合的運動型態；更完整的主頁可見滾動運動。
prerequisites: ["[[滾動運動]]", "[[轉矩]]"]
related_laws: ["[[轉動版牛頓第二定律]]"]
related_quantities: ["[[轉動慣量]]"]
related_concepts: ["[[滾動運動]]", "[[圓周運動]]"]
math_tools: []
tags: [physics, mechanics, concept]
updated: 2026-06-04
---

# 滾動

## 名稱說明
`滾動` 是你最直覺會搜尋的詞，但本庫既有完整主頁是 [[滾動運動]]。這一頁主要是名稱對齊，不讓節點因叫法不同而藏起來。

## 概念摘要
滾動不是單純在滑，也不是單純在自轉，而是平動與轉動同時存在的耦合運動。

## 和既有節點的關係
若你要完整內容，直接讀 [[滾動運動]]。那邊才是主頁。

## 相關概念
- [[滾動運動]]
- [[轉動慣量]]
- [[轉矩]]
""",
    "03_quantities/角頻率.md": """---
type: quantity
title: 角頻率
symbol: \\omega
unit: rad/s
dimension: T^-1
domain: 振動與波動
summary: 角頻率描述系統相位隨時間前進的快慢，與普通頻率相差一個 2π 因子。
related_concepts: ["[[頻率]]", "[[相位]]", "[[簡諧運動]]", "[[交流電]]"]
related_laws: []
measurement_methods: []
tags: [physics, waves, quantity]
updated: 2026-06-04
---

# 角頻率

## 量綱摘要
角頻率記作
$$
\\omega,
$$
描述相位每單位時間前進多少弧度。

## 和頻率的關係
若普通頻率為 $f$，則
$$
\\omega=2\\pi f.
$$

## 物理意義
頻率告訴你每秒幾個週期，角頻率則直接用弧度速度描述週期演化。對微分方程、振動、交流與波動分析來說，角頻率通常更順手。

## 相關概念
- [[頻率]]
- [[相位]]
- [[簡諧運動]]
""",
    "02_concepts/正常模態.md": """---
type: concept
title: 正常模態
domain: 振動與波動
summary: 正常模態是多自由度或連續系統中彼此可獨立振動的基本模式；本庫既有更一般的模態節點。
prerequisites: ["[[模態]]", "[[自由度]]", "[[矩陣]]"]
related_laws: []
related_quantities: ["[[頻率]]"]
related_concepts: ["[[模態]]", "[[共振]]", "[[簡諧運動]]"]
math_tools: ["[[矩陣]]", "[[向量]]"]
tags: [physics, waves, concept]
updated: 2026-06-04
---

# 正常模態

## 概念摘要
正常模態是耦合系統中最自然的獨立振動模式。找到它們之後，原本糾纏在一起的運動常能拆成互不干擾的基本成分。

## 和模態的關係
`正常模態` 是 [[模態]] 在振動問題中的核心版本。不是所有模態語境都一定指正常模態，但很多物理題最後都在找這一組最自然的基底。

## 物理直覺
多自由度系統看起來很亂，是因為你站在錯的座標上。正常模態的作用就是把問題轉到系統自己最舒服的語言。

## 相關概念
- [[模態]]
- [[自由度]]
- [[共振]]
""",
    "03_quantities/黏度.md": """---
type: quantity
title: 黏度
symbol: \\eta
unit: Pa·s
dimension: M L^-1 T^-1
domain: 流體力學
summary: 黏度描述流體內部抵抗速度梯度與剪切流動的程度，是區分層流與紊流的重要參數。
related_concepts: ["[[黏滯力]]", "[[層流]]", "[[紊流]]"]
related_laws: ["[[伯努力方程]]"]
measurement_methods: []
tags: [physics, fluid, quantity]
updated: 2026-06-04
---

# 黏度

## 量綱摘要
黏度衡量流體內部對相對滑動的抗拒程度。黏度越大，流體越不願讓相鄰流層輕鬆錯動。

## 符號與單位
常用符號
$$
\\eta
$$
SI 單位常寫作 `Pa·s`。

## 物理意義
黏度不是「稠」這種口語形容而已，它直接控制流體中的耗散、速度分布、邊界層與流動穩定性。

## 和其他主題的關係
- 和 [[黏滯力]] 直接相關。
- 和 [[雷諾數]] 一起決定流動較偏向 [[層流]] 還是 [[紊流]]。
- [[伯努力方程]] 的理想形式常忽略黏度。

## 相關概念
- [[黏滯力]]
- [[層流]]
- [[紊流]]
""",
    "01_laws/歐拉－拉格朗日方程.md": """---
type: law
title: 歐拉－拉格朗日方程
domain: 力學
summary: 歐拉－拉格朗日方程是由作用量駐值條件推出的運動方程，構成拉格朗日力學的核心。
applicability: 適用於可由廣義座標與拉格朗日量表述的系統；遇到非完整約束或顯式耗散時需更小心處理。
prerequisites: ["[[拉格朗日力學]]", "[[作用量]]", "[[廣義座標]]"]
related_concepts: ["[[拉格朗日力學]]", "[[最小作用量原理]]", "[[哈密頓量]]"]
related_quantities: []
related_laws: ["[[最小作用量原理]]"]
experiments: []
math_tools: ["[[向量]]"]
derived_results: ["[[哈密頓方程]]"]
modern_connections: []
tags: [physics, mechanics, law]
updated: 2026-06-04
---

# 歐拉－拉格朗日方程

## 定律摘要
歐拉－拉格朗日方程把「作用量取駐值」這件事翻譯成可解的運動方程，是 [[拉格朗日力學]] 真正落地的地方。

## 數學表述
若拉格朗日量為 $L(q_i,\dot q_i,t)$，則
$$
\\frac{d}{dt}\\left(\\frac{\\partial L}{\\partial \\dot q_i}\\right)-\\frac{\\partial L}{\\partial q_i}=0.
$$

## 物理意義
這條式子不是在炫數學技巧，而是在說：動力學可以不用直接追力，而改用整體變分結構來產生。

## 相關概念
- [[拉格朗日力學]]
- [[最小作用量原理]]
- [[作用量]]
""",
    "01_laws/最小作用量原理.md": """---
type: law
title: 最小作用量原理
domain: 力學
summary: 最小作用量原理指出實際運動路徑使作用量取駐值，並由此導出歐拉－拉格朗日方程。
applicability: 適用於可用作用量描述的系統；更精確地說是駐值原理，不必字面上真的最小。
prerequisites: ["[[作用量]]", "[[拉格朗日力學]]"]
related_concepts: ["[[作用量]]", "[[歐拉－拉格朗日方程]]", "[[諾特定理]]"]
related_quantities: []
related_laws: ["[[歐拉－拉格朗日方程]]"]
experiments: []
math_tools: ["[[向量]]"]
derived_results: ["[[歐拉－拉格朗日方程]]"]
modern_connections: []
tags: [physics, mechanics, law]
updated: 2026-06-04
---

# 最小作用量原理

## 定律摘要
最小作用量原理說，系統真實走出的歷史，會讓作用量
$$
S=\\int L\,dt
$$
取駐值。名字叫最小，但更精確的說法其實是「駐值」。

## 物理意義
這條原理的強度在於，它不直接從某一瞬間的受力出發，而是一次看整段歷史，然後挑出整體上自洽的路徑。

## 與其他節點的關係
從這裡變分出去，就得到 [[歐拉－拉格朗日方程]]；而對稱性再往前推，就會碰到 [[諾特定理]]。

## 相關概念
- [[作用量]]
- [[歐拉－拉格朗日方程]]
- [[諾特定理]]
""",
    "02_concepts/哈密頓量.md": """---
type: concept
title: 哈密頓量
domain: 力學
summary: 哈密頓量是把系統寫成廣義座標與廣義動量函數後得到的核心生成量，在很多情況下與總能量密切相關。
prerequisites: ["[[拉格朗日力學]]", "[[作用量]]", "[[廣義座標]]"]
related_laws: ["[[哈密頓方程]]"]
related_quantities: []
related_concepts: ["[[哈密頓方程]]", "[[相空間]]", "[[正則變換]]"]
math_tools: ["[[向量]]"]
tags: [physics, mechanics, concept]
updated: 2026-06-04
---

# 哈密頓量

## 概念摘要
哈密頓量通常記作
$$
H(q_i,p_i,t),
$$
是把系統改寫成廣義座標與廣義動量語言後的核心函數。

## 和能量的關係
在很多常見保守系統裡，哈密頓量等同於總能量；但這不是宇宙鐵律，條件不對時兩者不能直接畫等號。

## 在理論中的角色
哈密頓量不只是拿來記錄能量，它還生成時間演化。這就是為什麼它會直接出現在 [[哈密頓方程]] 中。

## 相關概念
- [[哈密頓方程]]
- [[相空間]]
- [[正則變換]]
""",
    "01_laws/哈密頓方程.md": """---
type: law
title: 哈密頓方程
domain: 力學
summary: 哈密頓方程用廣義座標與廣義動量的一階方程組描述系統演化，是哈密頓力學的核心形式。
applicability: 適用於可在相空間中以哈密頓量描述的系統。
prerequisites: ["[[哈密頓量]]", "[[相空間]]", "[[廣義座標]]"]
related_concepts: ["[[哈密頓量]]", "[[相空間]]", "[[泊松括號]]", "[[正則變換]]"]
related_quantities: []
related_laws: ["[[歐拉－拉格朗日方程]]"]
experiments: []
math_tools: ["[[向量]]"]
derived_results: []
modern_connections: []
tags: [physics, mechanics, law]
updated: 2026-06-04
---

# 哈密頓方程

## 定律摘要
哈密頓方程把運動方程寫成一組一階方程，而不是像牛頓或拉格朗日形式那樣主要看二階加速度結構。

## 數學表述
$$
\\dot q_i=\\frac{\\partial H}{\\partial p_i},\qquad
\\dot p_i=-\\frac{\\partial H}{\\partial q_i}.
$$

## 物理意義
這套形式把時間演化搬進 [[相空間]]。你不再只看位置怎麼動，而是同時追蹤座標與動量如何共同流動。

## 相關概念
- [[哈密頓量]]
- [[相空間]]
- [[泊松括號]]
""",
    "02_concepts/相空間.md": """---
type: concept
title: 相空間
domain: 力學
summary: 相空間是以座標與動量共同作為座標軸的狀態空間，用來完整表示系統即時狀態與其演化軌道。
prerequisites: ["[[哈密頓量]]", "[[廣義座標]]"]
related_laws: ["[[哈密頓方程]]"]
related_quantities: []
related_concepts: ["[[哈密頓量]]", "[[哈密頓方程]]", "[[正則變換]]"]
math_tools: ["[[向量]]", "[[矩陣]]"]
tags: [physics, mechanics, concept]
updated: 2026-06-04
---

# 相空間

## 概念摘要
相空間不是普通幾何空間，而是拿每個自由度的座標與動量一起當成軸所構成的狀態空間。

## 為什麼重要
在相空間裡，一個系統的瞬時狀態對應一個點，時間演化則對應一條軌跡。這比只看位置空間完整得多。

## 物理直覺
如果你只知道物體在哪裡，但不知道它正朝哪裡衝，那你根本不知道它的狀態。相空間就是拒絕這種半殘描述。

## 相關概念
- [[哈密頓量]]
- [[哈密頓方程]]
- [[正則變換]]
""",
    "02_concepts/泊松括號.md": """---
type: concept
title: 泊松括號
domain: 力學
summary: 泊松括號描述相空間中兩個函數之間的基本代數關係，並可用來表達哈密頓系統的時間演化。
prerequisites: ["[[哈密頓方程]]", "[[相空間]]"]
related_laws: ["[[哈密頓方程]]"]
related_quantities: []
related_concepts: ["[[相空間]]", "[[正則變換]]", "[[諾特定理]]"]
math_tools: ["[[向量]]"]
tags: [physics, mechanics, concept]
updated: 2026-06-04
---

# 泊松括號

## 概念摘要
對兩個相空間函數 $f(q,p,t)$ 與 $g(q,p,t)$，泊松括號定義為
$$
\\{f,g\\}=
\\sum_i\\left(
\\frac{\\partial f}{\\partial q_i}\\frac{\\partial g}{\\partial p_i}
-\\frac{\\partial f}{\\partial p_i}\\frac{\\partial g}{\\partial q_i}
\\right).
$$

## 為什麼重要
它不是裝飾符號，而是哈密頓力學的運算骨架。很多守恆條件、對稱結構與生成量都可用它寫得非常乾淨。

## 相關概念
- [[哈密頓方程]]
- [[相空間]]
- [[正則變換]]
""",
    "02_concepts/正則變換.md": """---
type: concept
title: 正則變換
domain: 力學
summary: 正則變換是在保留哈密頓方程形式不變的前提下，對相空間變數做的變換。
prerequisites: ["[[哈密頓方程]]", "[[相空間]]", "[[泊松括號]]"]
related_laws: ["[[哈密頓方程]]"]
related_quantities: []
related_concepts: ["[[相空間]]", "[[泊松括號]]", "[[哈密頓量]]"]
math_tools: ["[[矩陣]]", "[[向量]]"]
tags: [physics, mechanics, concept]
updated: 2026-06-04
---

# 正則變換

## 概念摘要
正則變換是在不破壞哈密頓結構的情況下，改換相空間變數的方式。它的價值在於：換了語言，但物理骨架沒被拆掉。

## 物理意義
好的正則變換能把原本糾纏的問題變乾淨，例如把哈密頓量變成更容易積分或更容易辨認守恆量的形式。

## 相關概念
- [[相空間]]
- [[泊松括號]]
- [[哈密頓量]]
""",
    "01_laws/諾特定理.md": """---
type: law
title: 諾特定理
domain: 力學
summary: 諾特定理指出連續對稱性對應守恆量，將作用量的對稱結構與守恆律直接連接起來。
applicability: 適用於可由作用量表述並具有連續對稱性的系統。
prerequisites: ["[[對稱性]]", "[[守恆律]]", "[[最小作用量原理]]"]
related_concepts: ["[[對稱性]]", "[[守恆量]]", "[[作用量]]"]
related_quantities: ["[[頻率]]"]
related_laws: ["[[最小作用量原理]]", "[[角動量守恆]]", "[[機械能守恆]]"]
experiments: []
math_tools: ["[[向量]]"]
derived_results: ["[[守恆律]]"]
modern_connections: []
tags: [physics, mechanics, law]
updated: 2026-06-04
---

# 諾特定理

## 定律摘要
諾特定理說明：每一個連續對稱性，對應一個守恆量。這句話幾乎把現代理論力學最漂亮的骨架直接講完了。

## 經典對應
- 時間平移對稱 -> 能量守恆
- 空間平移對稱 -> 動量守恆
- 旋轉對稱 -> 角動量守恆

## 物理意義
這條定理的力量在於，它不再把守恆律當成彼此無關的神祕規矩，而是把它們全都追溯到對稱性。

## 與其他節點的關係
若沒有 [[最小作用量原理]] 與作用量語言，諾特定理很難以最乾淨的形式表達。

## 相關概念
- [[對稱性]]
- [[守恆律]]
- [[最小作用量原理]]
- [[作用量]]
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
