#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


NOTES: dict[str, str] = {
    "01_laws/電磁波方程.md": """---
type: law
title: 電磁波方程
domain: 電磁學
summary: 電磁波方程描述真空中的電場與磁場如何滿足波動方程，並以光速傳播。
applicability: 適用於真空或可近似為均勻線性介質中的自由傳播區域；若介質有耗散、色散或複雜邊界，必須回到更完整的麥克斯威方程組與邊界條件。
prerequisites: ["[[麥克斯威方程組]]", "[[電磁波]]", "[[向量]]"]
related_concepts: ["[[電磁波]]", "[[電磁波傳播]]", "[[邊界條件]]"]
related_quantities: ["[[真空光速]]", "[[波長]]", "[[頻率]]"]
related_laws: ["[[麥克斯威方程組]]"]
experiments: []
math_tools: ["[[向量]]"]
derived_results: ["[[真空光速]]"]
modern_connections: ["[[狹義相對論]]"]
tags: [physics, electromagnetism, law]
updated: 2026-06-04
---

# 電磁波方程

## 定律摘要
電磁波方程說明：在無自由電荷、無自由電流的區域，電場與磁場都滿足波動方程，因此電磁擾動可以自行傳播，而不是非得靠介質才走得動。

## 適用條件
最乾淨的形式出現在真空：
$$
\nabla\cdot\vec E=0,\qquad \nabla\cdot\vec B=0,
$$
$$
\nabla\times\vec E=-\frac{\partial \vec B}{\partial t},\qquad
\nabla\times\vec B=\mu_0\varepsilon_0\frac{\partial \vec E}{\partial t}.
$$

## 數學表述
由上式可推出
$$
\nabla^2\vec E=\mu_0\varepsilon_0\frac{\partial^2\vec E}{\partial t^2},
$$
$$
\nabla^2\vec B=\mu_0\varepsilon_0\frac{\partial^2\vec B}{\partial t^2}.
$$

因此波速為
$$
v=\frac{1}{\sqrt{\mu_0\varepsilon_0}}=c.
$$

## 符號說明與單位
- $\vec E$：電場，單位 V/m。
- $\vec B$：磁場，單位 T。
- $\mu_0$：真空磁導率。
- $\varepsilon_0$：真空介電常數。
- $c$：[[真空光速]]。

## 物理直覺
這條方程真正厲害的地方，不是把二階偏微分寫得很漂亮，而是告訴你電場與磁場可以彼此驅動。變動電場生磁場，變動磁場生電場，兩者互相接力，最後就變成自我維持的波。

## 推導思路
1. 從 [[麥克斯威方程組]] 取旋度形式出發。
2. 對 $\nabla\times\vec E$ 或 $\nabla\times\vec B$ 再取一次旋度。
3. 使用向量恆等式
$$
\nabla\times(\nabla\times\vec F)=\nabla(\nabla\cdot\vec F)-\nabla^2\vec F.
$$
4. 在真空中代入 $\nabla\cdot\vec E=0$、$\nabla\cdot\vec B=0$，就得到波動方程。

## 物理意義
電磁波方程把光從「現象」升級成「場的動力學結果」。這不是語文修飾，而是把光學和電磁學接成同一條主線。

## 典型應用
- 分析平面電磁波。
- 從場方程推出 [[真空光速]]。
- 連接 [[電磁場能量流]] 與 [[坡印廷向量]]。
- 作為理解天線、波導與光傳播的起點。

## 相關概念
- [[麥克斯威方程組]]
- [[電磁波]]
- [[電磁波傳播]]
- [[真空光速]]
""",
    "01_laws/斯涅爾定律.md": """---
type: law
title: 斯涅爾定律
domain: 光學
summary: 斯涅爾定律描述光通過介面時入射角與折射角之間的定量關係，也就是常說的折射定律。
applicability: 適用於幾何光學近似、均勻各向同性介質與清楚界面；若介質高度非均勻、各向異性或必須處理偏振依賴反射，單靠這條式子不夠。
prerequisites: ["[[光線模型]]", "[[折射率]]", "[[三角函數]]"]
related_concepts: ["[[折射]]", "[[全反射]]", "[[惠更斯原理]]"]
related_quantities: ["[[折射率]]"]
related_laws: ["[[折射定律]]"]
experiments: []
math_tools: ["[[三角函數]]"]
derived_results: ["[[全反射]]"]
modern_connections: []
tags: [physics, optics, law]
updated: 2026-06-04
---

# 斯涅爾定律

## 定律摘要
斯涅爾定律就是 [[折射定律]] 的常見名稱。它把「光會彎」這種直觀印象，壓成一條可計算的角度關係。

## 數學表述
$$
n_1\sin\theta_1=n_2\sin\theta_2
$$

若用波速表示，也可寫成
$$
\frac{\sin\theta_1}{\sin\theta_2}=\frac{v_1}{v_2}.
$$

## 符號說明與單位
- $n_1,n_2$：兩介質的 [[折射率]]。
- $\theta_1$：入射角，以法線為基準。
- $\theta_2$：折射角，以法線為基準。

## 物理直覺
光不是因為撞到界面突然改變心情才轉彎，而是因為不同介質中的傳播速度不同。波前不同部分跨入新介質的時間不同，整體幾何就被迫改向。

## 和既有節點的關係
若你只想找正式名稱，讀這頁就夠；若你要看更完整的定律型寫法，直接看 [[折射定律]]。這兩頁講的是同一件事，不是兩條不同法律。

## 典型應用
- 空氣到玻璃的折射角計算。
- 臨界角與 [[全反射]] 判斷。
- 透鏡與棱鏡的基本光路分析。

## 相關概念
- [[折射]]
- [[折射率]]
- [[折射定律]]
- [[全反射]]
""",
    "02_concepts/反射.md": """---
type: concept
title: 反射
domain: 光學
summary: 反射是波或光在界面上被重新導向的現象；在幾何光學中最核心的局部規則是反射定律。
prerequisites: ["[[光線模型]]", "[[邊界條件]]"]
related_laws: ["[[反射定律]]"]
related_quantities: []
related_concepts: ["[[折射]]", "[[全反射]]", "[[繞射]]"]
math_tools: []
tags: [physics, optics, concept]
updated: 2026-06-04
---

# 反射

## 概念摘要
反射是波或光到達介面後，部分能量返回原介質的現象。最基本的例子是平面鏡反射，但真正的核心不是鏡子，而是界面如何重排波的方向與能量。

## 與定律的關係
在幾何光學近似下，[[反射定律]] 給出最直接的角度規則：
入射角等於反射角，且入射線、反射線與法線共平面。

## 物理直覺
反射不是「彈回去」那種幼稚比喻就能交代完的事。更精確地說，界面條件限制了場或波前能怎麼接續，最後留下的可觀測結果就是反射方向被固定。

## 常見分類
- 鏡面反射：方向明確，可用光線模型處理。
- 漫反射：表面粗糙，局部法線亂成一團，方向分散。
- 全反射：光嘗試進入另一介質卻失敗，能量留在原介質內部。

## 與其他主題的連接
- 和 [[折射]] 一起構成最基本的界面光學。
- 和 [[全反射]] 連接，因為全反射本質上是特殊條件下的界面反射。
- 和 [[繞射]] 區分，因為後者需要顯式處理孔徑與波前展開。

## 相關概念
- [[反射定律]]
- [[折射]]
- [[全反射]]
""",
    "02_concepts/折射.md": """---
type: concept
title: 折射
domain: 光學
summary: 折射是波或光跨越介面後因傳播速度改變而改變方向的現象，其核心定量規則是折射定律，也就是斯涅爾定律。
prerequisites: ["[[光線模型]]", "[[折射率]]", "[[惠更斯原理]]"]
related_laws: ["[[折射定律]]", "[[斯涅爾定律]]"]
related_quantities: ["[[折射率]]"]
related_concepts: ["[[反射]]", "[[全反射]]", "[[薄透鏡公式]]"]
math_tools: ["[[三角函數]]"]
tags: [physics, optics, concept]
updated: 2026-06-04
---

# 折射

## 概念摘要
折射是光或其他波穿過介面後方向改變的現象。真正改變的不是頻率，而是相速度與波長；方向轉折只是這件事的幾何外觀。

## 核心規則
折射最重要的定量規則是 [[折射定律]]，也就是 [[斯涅爾定律]]。若介質折射率較大，光在該介質中傳播較慢，波前轉向法線。

## 物理直覺
折射最容易被學爛的地方，是把它背成角度代數。正確直覺是：同一個波前不同部分跨過界面的時間不同，所以整個波前被迫旋轉。

## 典型情境
- 空氣到水面，光向法線偏折。
- 玻璃到空氣，光背離法線偏折。
- 入射角過大時，不再有實際穿透光路，而轉入 [[全反射]]。

## 與其他主題的連接
- [[折射率]] 決定偏折程度。
- [[薄透鏡公式]] 與透鏡成像，本質上是大量折射面效果的整理。
- [[反射]] 與折射同時發生，差別只是能量分到哪裡。

## 相關概念
- [[折射定律]]
- [[斯涅爾定律]]
- [[折射率]]
- [[全反射]]
""",
    "03_quantities/真空光速.md": """---
type: quantity
title: 真空光速
symbol: c
unit: m/s
dimension: L T^-1
domain: 光學
summary: 真空光速是電磁波在真空中的傳播速度，也是相對論中時空結構的基本常數。
related_concepts: ["[[電磁波]]", "[[狹義相對論]]"]
related_laws: ["[[電磁波方程]]", "[[麥克斯威方程組]]"]
measurement_methods: []
tags: [physics, optics, quantity]
updated: 2026-06-04
---

# 真空光速

## 量綱摘要
真空光速是光與所有無質量電磁訊號在真空中的傳播速度，記作
$$
c.
$$

## 數值
在 SI 制中，
$$
c = 299\,792\,458\ \text{m/s}.
$$

這不是近似值，而是 SI 定義中的精確值。

## 與電磁學的關係
由 [[電磁波方程]] 與 [[麥克斯威方程組]] 可得
$$
c=\frac{1}{\sqrt{\mu_0\varepsilon_0}}.
$$

這件事的殺傷力很大，因為它直接把光學和電磁學焊死在一起。

## 物理意義
在古典電磁學裡，$c$ 是電磁波速度；在 [[狹義相對論]] 裡，$c$ 更進一步成為時空結構的上限速度與轉換常數。你若把它只當成「光跑多快」，那等於只看見表皮。

## 常見使用情境
- 波速公式中的基準常數。
- 介質中速度關係
$$
v=\frac{c}{n}.
$$
- 相對論能量與動量關係。

## 相關概念
- [[電磁波方程]]
- [[折射率]]
- [[狹義相對論]]
""",
    "03_quantities/波印廷向量.md": """---
type: quantity
title: 波印廷向量
symbol: \\vec S
unit: W/m^2
dimension: M T^-3
domain: 電磁學
summary: 波印廷向量表示電磁能量流密度；更常見也更標準的譯名是坡印廷向量。
related_concepts: ["[[電磁場能量流]]", "[[電磁波]]"]
related_laws: ["[[電磁波方程]]", "[[麥克斯威方程組]]"]
measurement_methods: []
tags: [physics, electromagnetism, quantity]
updated: 2026-06-04
---

# 波印廷向量

## 名稱說明
這個詞常被寫成「波印廷向量」，但更常見的正式譯名是 [[坡印廷向量]]。這一頁保留你會搜尋的名稱，避免節點名不一致把東西藏起來。

## 數學表述
在真空中，
$$
\vec S=\frac{1}{\mu_0}\vec E\times\vec B.
$$

## 物理意義
$\vec S$ 的方向給出電磁能量流方向，大小對應單位面積、單位時間穿過的能量。換句話說，它不是抽象裝飾，而是直接回答能量往哪裡走。

## 和既有節點的關係
若你要讀完整內容，直接看 [[坡印廷向量]]。這一頁的任務很單純：把 `波印廷向量` 這個常見寫法納入圖譜，不再讓搜尋失手。

## 相關概念
- [[坡印廷向量]]
- [[電磁場能量流]]
- [[電磁波]]
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
