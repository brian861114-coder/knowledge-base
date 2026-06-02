#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


NOTES: dict[str, str] = {
    "03_quantities/電流.md": """---
type: quantity
title: 電流
symbol: I
unit: A
dimension: I
domain: 電磁學
summary: 電流是單位時間內穿過截面的電荷量，描述電荷流動的強弱與方向。
related_concepts: ["[[電荷]]", "[[直流電路]]", "[[交流電]]"]
related_laws: ["[[歐姆定律]]", "[[安培定律]]"]
measurement_methods: []
tags: [physics, electromagnetism, quantity]
updated: 2026-06-02
---

# 電流

## 定義
電流描述電荷穿過某一截面的速率。若約定正電荷流動方向為正，則電流方向與正電荷運動方向一致，與電子實際漂移方向相反。

## 數學表達
$$
I = \\frac{\\Delta Q}{\\Delta t}
$$

在瞬時形式下可寫成
$$
I = \\frac{dQ}{dt}
$$

## 符號與單位
- 符號：$I$
- SI 單位：A

## 物理解讀
在 [[直流電路]] 中，電流常近似為穩定不變；在 [[交流電]] 中，電流則會隨時間週期性改變。電流本身不是「被消耗掉」的量，真正被轉換的是電荷攜帶的能量。

## 常見誤解
- 把電流和電子速度視為同一件事。電流是整體通量，電子漂移速度通常很小。
- 認為電流會在元件中逐段減少。對穩態電路而言，串聯支路中的電流相同。

## 相關連結
- [[電荷]]
- [[直流電路]]
- [[交流電]]
- [[歐姆定律]]
- [[安培定律]]
""",
    "03_quantities/電阻.md": """---
type: quantity
title: 電阻
symbol: R
unit: \\Omega
dimension: M L^2 T^-3 I^-2
domain: 電磁學
summary: 電阻量化材料或元件阻礙電流通過的程度，是電路分析中的核心參數。
related_concepts: ["[[電流]]", "[[電位差]]", "[[直流電路]]"]
related_laws: ["[[歐姆定律]]"]
measurement_methods: []
tags: [physics, electromagnetism, quantity]
updated: 2026-06-02
---

# 電阻

## 定義
電阻描述導體對電流的阻礙程度。固定材料與幾何形狀下，電阻越大，建立相同電流所需的電位差越大。

## 數學表達
由 [[歐姆定律]] 可得
$$
R = \\frac{V}{I}
$$

對均勻導體，還有
$$
R = \\rho \\frac{L}{A}
$$

## 符號與單位
- 符號：$R$
- SI 單位：$\\Omega$

## 物理解讀
電阻同時受到材料性質與幾何尺寸影響。長而細的導體通常電阻較大；短而粗的導體通常電阻較小。電阻也是焦耳熱產生的直接來源之一。

## 常見誤解
- 把電阻當成元件「消耗電流」的能力。元件轉換的是能量，不是把電流吃掉。
- 認為所有元件都嚴格服從 [[歐姆定律]]。事實上，只有歐姆性元件才有近似線性關係。

## 相關連結
- [[電流]]
- [[電位差]]
- [[直流電路]]
- [[歐姆定律]]
""",
    "03_quantities/電動勢.md": """---
type: quantity
title: 電動勢
symbol: \\mathcal{E}
unit: V
dimension: M L^2 T^-3 I^-1
domain: 電磁學
summary: 電動勢是非靜電作用對單位電荷提供的能量，決定電源推動電荷繞行回路的能力。
related_concepts: ["[[電位差]]", "[[直流電路]]", "[[磁通量]]"]
related_laws: ["[[法拉第定律]]", "[[楞次定律]]"]
measurement_methods: []
tags: [physics, electromagnetism, quantity]
updated: 2026-06-02
---

# 電動勢

## 定義
電動勢不是一種力，而是非靜電作用對單位電荷所提供的能量。化學電池、發電機與變動磁場都能產生電動勢。

## 數學表達
一般定義為
$$
\\mathcal{E} = \\frac{W_{\\text{non-elec}}}{q}
$$

對感應情況，[[法拉第定律]] 給出
$$
\\mathcal{E} = -\\frac{d\\Phi_B}{dt}
$$

## 符號與單位
- 符號：$\\mathcal{E}$
- SI 單位：V

## 物理解讀
在電池中，電動勢來自化學作用；在感應情況下，電動勢來自磁通量變化。它決定回路中可建立多大的電流，但實際電流大小還取決於總電阻。

## 常見誤解
- 把電動勢和端電壓視為完全相同。理想電源下近似相同，但實際電源還有內阻效應。
- 看到負號就以為電動勢一定是負值。負號表達的是感應方向，而不是單純大小為負。

## 相關連結
- [[電位差]]
- [[直流電路]]
- [[磁通量]]
- [[法拉第定律]]
- [[楞次定律]]
""",
    "03_quantities/磁通量.md": """---
type: quantity
title: 磁通量
symbol: \\Phi_B
unit: Wb
dimension: M L^2 T^-2 I^-1
domain: 電磁學
summary: 磁通量量化磁場穿過某個面積的總效果，是理解電磁感應的核心量。
related_concepts: ["[[磁場]]", "[[電動勢]]"]
related_laws: ["[[法拉第定律]]", "[[楞次定律]]"]
measurement_methods: []
tags: [physics, electromagnetism, quantity]
updated: 2026-06-02
---

# 磁通量

## 定義
磁通量描述磁場穿過指定面積的總量。它不是單純把磁場大小乘上面積，而是要考慮磁場與面法向量的夾角。

## 數學表達
一般形式為
$$
\\Phi_B = \\int \\vec B \\cdot d\\vec A
$$

若磁場均勻且面積為平面，可寫成
$$
\\Phi_B = BA\\cos\\theta
$$

## 符號與單位
- 符號：$\\Phi_B$
- SI 單位：Wb

## 物理解讀
當磁通量隨時間改變時，回路中就可能出現感應 [[電動勢]]。因此磁通量是連接 [[磁場]] 與 [[法拉第定律]] 的橋樑。

## 常見誤解
- 只看 $B$ 的大小而忽略方向，這會直接算錯磁通量。
- 把磁通量變化等同於磁場變化。面積變化或角度變化也會造成磁通量改變。

## 相關連結
- [[磁場]]
- [[電動勢]]
- [[法拉第定律]]
- [[楞次定律]]
""",
    "03_quantities/電感.md": """---
type: quantity
title: 電感
symbol: L
unit: H
dimension: M L^2 T^-2 I^-2
domain: 電磁學
summary: 電感衡量回路以磁場儲能並反抗電流變化的能力，是感應與交流分析的重要參數。
related_concepts: ["[[磁通量]]", "[[交流電]]"]
related_laws: ["[[法拉第定律]]", "[[楞次定律]]"]
measurement_methods: []
tags: [physics, electromagnetism, quantity]
updated: 2026-06-02
---

# 電感

## 定義
電感描述回路在電流改變時產生感應電動勢的能力。電感越大，系統越傾向反抗電流的快速變化。

## 數學表達
若磁通量與電流成正比，可寫成
$$
\\Phi_B \\propto I
$$

感應電動勢滿足
$$
\\mathcal{E} = -L\\frac{dI}{dt}
$$

## 符號與單位
- 符號：$L$
- SI 單位：H

## 物理解讀
電感可視為電路中的慣性。電阻反抗電流本身，電感反抗的是電流變化率。這也是為什麼線圈在 [[交流電]] 中具有顯著作用。

## 常見誤解
- 把電感和電阻混為一談。兩者都影響電流，但物理機制完全不同。
- 認為只有獨立元件才有電感。任何有磁場耦合的回路都存在某種程度的電感。

## 相關連結
- [[磁通量]]
- [[交流電]]
- [[法拉第定律]]
- [[楞次定律]]
""",
    "02_concepts/直流電路.md": """---
type: concept
title: 直流電路
domain: 電磁學
summary: 直流電路研究在穩態條件下電流、電位差與電阻之間的關係，是電磁學中最基本的模型之一。
prerequisites: ["[[電流]]", "[[電位差]]", "[[電阻]]"]
related_laws: ["[[歐姆定律]]"]
related_quantities: ["[[電流]]", "[[電位差]]", "[[電阻]]", "[[電動勢]]"]
related_concepts: ["[[交流電]]", "[[電容器]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 直流電路

## 核心想法
直流電路關心的是穩態下各元件如何分配電位差、如何決定支路電流，以及電源如何透過 [[電動勢]] 持續驅動電荷流動。

## 基本構成
最典型的直流電路由電源、導線與負載組成。若負載可視為歐姆性元件，就能直接使用 [[歐姆定律]] 分析。

## 典型問題
- 已知電壓與電阻，求電流。
- 已知支路結構，求各支路上的電位差與電流分配。
- 估算元件上的能量轉換與發熱。

## 物理解讀
直流電路不是「電荷被推著走」這麼粗糙。更精確地說，電源建立電場，電場驅動載流子，元件再把電能轉換為熱、光或其他形式。

## 常見誤解
- 把導線當成完全不參與物理過程的背景。實際上導線內部電場與邊界條件都決定穩態分布。
- 認為電流離開電池後會逐步變少。對串聯穩態回路而言，電流相同。

## 相關連結
- [[電流]]
- [[電位差]]
- [[電阻]]
- [[電動勢]]
- [[歐姆定律]]
- [[交流電]]
""",
    "01_laws/安培定律.md": """---
type: law
title: 安培定律
domain: 電磁學
summary: 安培定律把封閉路徑上的磁場環流與其包圍的總電流連起來，是高對稱磁場分析的核心工具。
applicability: 適用於具有良好對稱性的穩恒電流問題。若考慮時間變化電場，需使用安培-馬克士威方程。
prerequisites: ["[[磁場]]", "[[電流]]", "[[向量]]"]
related_concepts: ["[[磁通量]]"]
related_quantities: ["[[電流]]"]
related_laws: ["[[畢奧-沙伐定律]]", "[[麥克斯威方程組]]"]
experiments: []
math_tools: ["[[積分]]"]
derived_results: []
modern_connections: []
tags: [physics, electromagnetism, law]
updated: 2026-06-02
---

# 安培定律

## 敘述
安培定律說明：沿著任意封閉路徑計算磁場的線積分，其結果與該路徑所包圍的總電流成正比。

## 數學表達
對穩恒電流，
$$
\\oint \\vec B \\cdot d\\vec l = \\mu_0 I_{\\text{enc}}
$$

若納入位移電流修正，則得到
$$
\\oint \\vec B \\cdot d\\vec l = \\mu_0 I_{\\text{enc}} + \\mu_0\\varepsilon_0\\frac{d\\Phi_E}{dt}
$$

## 物理解讀
這條定律的強項不是任何情況都能直接計算，而是在圓柱、平面或環形對稱下，能把原本困難的磁場分布問題壓縮成代數與積分問題。

## 與其他定律的關係
[[畢奧-沙伐定律]] 可以從電流元逐點累積磁場；[[安培定律]] 則在高對稱情況下更有效率。兩者描述的是同一類物理，但計算策略不同。

## 常見誤解
- 把安培定律當成任何幾何下的快速公式。沒有對稱性時，它通常無法直接給出磁場大小。
- 忘記包圍電流的概念，只看路徑上某一點的局部電流密度。

## 相關連結
- [[磁場]]
- [[電流]]
- [[磁通量]]
- [[畢奧-沙伐定律]]
- [[麥克斯威方程組]]
- [[積分]]
""",
    "01_laws/畢奧-沙伐定律.md": """---
type: law
title: 畢奧-沙伐定律
domain: 電磁學
summary: 畢奧-沙伐定律給出微小電流元對空間某點磁場的貢獻，是磁場直接計算的基本定律。
applicability: 適用於穩恒電流所產生的磁場計算，特別適合對稱性不足但幾何已知的問題。
prerequisites: ["[[磁場]]", "[[電流]]", "[[向量]]"]
related_concepts: ["[[磁力]]"]
related_quantities: ["[[電流]]"]
related_laws: ["[[安培定律]]"]
experiments: []
math_tools: ["[[積分]]"]
derived_results: []
modern_connections: []
tags: [physics, electromagnetism, law]
updated: 2026-06-02
---

# 畢奧-沙伐定律

## 敘述
畢奧-沙伐定律描述一段微小電流元如何在空間某點產生磁場。它是從局部電流分布出發計算磁場的基本工具。

## 數學表達
$$
d\\vec B = \\frac{\\mu_0}{4\\pi}\\frac{I\\,d\\vec l \\times \\hat r}{r^2}
$$

## 物理解讀
磁場方向由叉積決定，因此天然帶有右手定則的方向資訊。當幾何複雜、難以直接套用 [[安培定律]] 時，畢奧-沙伐定律往往更直接。

## 典型用途
- 計算有限長導線的磁場。
- 計算圓形線圈中心與軸線上的磁場。
- 建立螺線管與環形線圈分析的局部觀點。

## 常見誤解
- 只記公式而忽略向量方向，最後得到大小對但方向錯的答案。
- 認為這條定律與 [[安培定律]] 互相矛盾。它們只是不同表述與不同計算工具。

## 相關連結
- [[磁場]]
- [[電流]]
- [[磁力]]
- [[安培定律]]
- [[積分]]
""",
    "01_laws/楞次定律.md": """---
type: law
title: 楞次定律
domain: 電磁學
summary: 楞次定律規定感應電流的方向總是反抗造成它的磁通量變化，保證能量守恆不被破壞。
applicability: 適用於各種電磁感應情況，包括運動感應與變壓感應。
prerequisites: ["[[磁通量]]", "[[電動勢]]", "[[磁場]]"]
related_concepts: ["[[交流電]]"]
related_quantities: ["[[電動勢]]", "[[磁通量]]"]
related_laws: ["[[法拉第定律]]"]
experiments: []
math_tools: []
derived_results: []
modern_connections: []
tags: [physics, electromagnetism, law]
updated: 2026-06-02
---

# 楞次定律

## 敘述
楞次定律指出：感應電流的方向，總會使它所產生的磁場去反抗原本磁通量的變化。

## 與法拉第定律的關係
在
$$
\\mathcal{E} = -\\frac{d\\Phi_B}{dt}
$$
中的負號，正是 [[楞次定律]] 的數學表現。這個負號不是裝飾，而是方向資訊。

## 物理解讀
如果感應電流反而強化原本的磁通量變化，就能憑空放大能量，這顯然荒謬。楞次定律正是避免這種荒謬結果的方向法則。

## 典型判斷方式
1. 先判斷穿過回路的 [[磁通量]] 是增加還是減少。
2. 再判斷回路要產生哪個方向的 [[磁場]] 才能反抗這種變化。
3. 最後用右手定則決定感應電流方向。

## 常見誤解
- 把「反抗磁通量變化」誤讀成「反抗磁通量本身」。
- 看到負號就只做代數操作，完全不處理方向。

## 相關連結
- [[磁通量]]
- [[電動勢]]
- [[磁場]]
- [[法拉第定律]]
- [[交流電]]
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
    print(f"rewrote={len(NOTES)} notes")


if __name__ == "__main__":
    main()
