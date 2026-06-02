#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


NOTES: dict[str, str] = {
    "01_laws/基爾霍夫電流定律.md": """---
type: law
title: 基爾霍夫電流定律
domain: 電磁學
summary: 基爾霍夫電流定律指出流入節點的總電流等於流出節點的總電流，本質上反映電荷守恆。
applicability: 適用於集總電路模型中的節點分析，特別常見於直流與低頻交流電路。
prerequisites: ["[[電流]]", "[[直流電路]]"]
related_concepts: ["[[交流電]]"]
related_quantities: ["[[電流]]"]
related_laws: ["[[基爾霍夫電壓定律]]", "[[歐姆定律]]"]
experiments: []
math_tools: []
derived_results: []
modern_connections: []
tags: [physics, electromagnetism, law]
updated: 2026-06-02
---

# 基爾霍夫電流定律

## 敘述
在任一節點上，流入的總電流必須等於流出的總電流。若不是如此，節點上的電荷就會無限制堆積，穩態模型立刻崩潰。

## 數學表達
$$
\\sum I_{\\text{in}} = \\sum I_{\\text{out}}
$$

或等價寫成
$$
\\sum I = 0
$$

## 物理解讀
這條定律本質上不是電路技巧，而是守恆律。節點分析之所以有效，是因為電荷在穩態下不能憑空消失，也不能無限制累積。

## 常見誤解
- 把支路電流方向先驗地當成已知。方向通常只是先假設，最後由正負號決定真假。
- 以為只有直流電路才適用。只要集總近似成立，交流分析同樣能用。

## 相關連結
- [[電流]]
- [[直流電路]]
- [[交流電]]
- [[基爾霍夫電壓定律]]
- [[歐姆定律]]
""",
    "01_laws/基爾霍夫電壓定律.md": """---
type: law
title: 基爾霍夫電壓定律
domain: 電磁學
summary: 基爾霍夫電壓定律指出沿封閉回路的電位升降總和為零，是迴路分析的核心。
applicability: 適用於集總電路模型中的迴路分析。當磁通量快速變化時，需小心與感應電動勢共同處理。
prerequisites: ["[[電位差]]", "[[直流電路]]", "[[電動勢]]"]
related_concepts: ["[[交流電]]"]
related_quantities: ["[[電位差]]", "[[電動勢]]"]
related_laws: ["[[基爾霍夫電流定律]]", "[[歐姆定律]]"]
experiments: []
math_tools: []
derived_results: []
modern_connections: []
tags: [physics, electromagnetism, law]
updated: 2026-06-02
---

# 基爾霍夫電壓定律

## 敘述
沿著任一封閉回路繞行，所有電位升與電位降的代數和為零。這條定律讓複雜回路可以拆成可解的迴路方程。

## 數學表達
$$
\\sum \\Delta V = 0
$$

若回路中含有電源與電阻，常寫成
$$
\\sum \\mathcal{E} - \\sum IR = 0
$$

## 物理解讀
它反映的是回路中能量分配的平衡。電源提供的能量，必須由元件上的電位降與其他能量轉換完整對應。

## 常見誤解
- 以為任何情況都能直接用純電位差總和為零。若存在顯著的感應電動勢，就必須把感應項明確納入。
- 把正負號規則當成物理內容本身。那只是你選擇繞行方向與元件極性的記帳方式。

## 相關連結
- [[電位差]]
- [[電動勢]]
- [[直流電路]]
- [[交流電]]
- [[基爾霍夫電流定律]]
- [[歐姆定律]]
""",
    "02_concepts/自感.md": """---
type: concept
title: 自感
domain: 電磁學
summary: 自感是回路中電流變化時，由自身磁通量變化而產生感應電動勢的現象。
prerequisites: ["[[電感]]", "[[磁通量]]", "[[電流]]"]
related_laws: ["[[法拉第定律]]", "[[楞次定律]]"]
related_quantities: ["[[電感]]", "[[電動勢]]", "[[磁通量]]"]
related_concepts: ["[[RL電路]]", "[[交流電]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 自感

## 核心想法
當回路中的 [[電流]] 改變時，它自己產生的磁場也跟著改變，進而改變穿過自身的 [[磁通量]]，於是回路又對自己產生感應 [[電動勢]]。這就是自感。

## 物理解讀
自感使得回路不願意讓電流突然改變，所以常被比喻成電路中的慣性。這個比喻不完美，但在理解暫態行為時很有用。

## 數學關係
若電感為 $L$，則自感電動勢滿足
$$
\\mathcal{E} = -L\\frac{dI}{dt}
$$

## 典型場景
- 開關剛接通或斷開的瞬間。
- 線圈中的暫態電流變化。
- [[RL電路]] 的充放電過程。

## 相關連結
- [[電感]]
- [[磁通量]]
- [[電動勢]]
- [[法拉第定律]]
- [[楞次定律]]
- [[RL電路]]
""",
    "02_concepts/互感.md": """---
type: concept
title: 互感
domain: 電磁學
summary: 互感是某一回路中的電流變化，透過磁通量耦合在另一回路中產生感應電動勢的現象。
prerequisites: ["[[電感]]", "[[磁通量]]", "[[電流]]"]
related_laws: ["[[法拉第定律]]", "[[楞次定律]]"]
related_quantities: ["[[電動勢]]", "[[磁通量]]"]
related_concepts: ["[[變壓器]]", "[[交流電]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 互感

## 核心想法
一個回路中的電流改變時，會改變周圍磁場與穿過另一回路的 [[磁通量]]，於是第二個回路中出現感應 [[電動勢]]。這就是互感。

## 物理解讀
互感是「兩個回路彼此耦合」的版本，自感則是「回路和自己耦合」。兩者的數學形式相似，但物理對象不同。

## 數學關係
若互感係數為 $M$，可寫成
$$
\\mathcal{E}_2 = -M\\frac{dI_1}{dt}
$$

## 典型場景
- 緊鄰的線圈彼此感應。
- [[變壓器]] 一次側與二次側的耦合。
- 電路中不希望出現的寄生耦合。

## 相關連結
- [[電感]]
- [[磁通量]]
- [[電動勢]]
- [[法拉第定律]]
- [[楞次定律]]
- [[變壓器]]
""",
    "02_concepts/位移電流.md": """---
type: concept
title: 位移電流
domain: 電磁學
summary: 位移電流是麥克斯威為修正安培定律而引入的項，用來描述時間變化電場所造成的磁場效應。
prerequisites: ["[[電場]]", "[[磁場]]", "[[安培定律]]"]
related_laws: ["[[安培定律]]"]
related_quantities: []
related_concepts: ["[[麥克斯威方程組]]", "[[電磁波]]", "[[電容器]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 位移電流

## 核心想法
如果只把導體中的真實電流放進 [[安培定律]]，那麼在充電中的 [[電容器]] 之間會出現邏輯斷裂。麥克斯威為此引入位移電流項，讓時間變化的電場也能成為磁場來源。

## 數學表達
位移電流對應的修正項為
$$
\\mu_0\\varepsilon_0\\frac{d\\Phi_E}{dt}
$$

因此安培-麥克斯威形式可寫成
$$
\\oint \\vec B\\cdot d\\vec l = \\mu_0 I_{\\text{enc}} + \\mu_0\\varepsilon_0\\frac{d\\Phi_E}{dt}
$$

## 物理解讀
位移電流不是「真的有電子穿過真空」。它描述的是變動電場在方程中扮演與電流相似的源項角色。

## 相關連結
- [[電場]]
- [[磁場]]
- [[安培定律]]
- [[麥克斯威方程組]]
- [[電磁波]]
- [[電容器]]
""",
    "02_concepts/RL電路.md": """---
type: concept
title: RL電路
domain: 電磁學
summary: RL電路由電阻與電感組成，其暫態行為由自感效應主導，是理解電流建立與衰減的重要模型。
prerequisites: ["[[電阻]]", "[[電感]]", "[[電流]]"]
related_laws: ["[[歐姆定律]]", "[[楞次定律]]"]
related_quantities: ["[[電阻]]", "[[電感]]", "[[電流]]"]
related_concepts: ["[[自感]]", "[[交流電]]", "[[感抗]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# RL電路

## 核心想法
RL電路把 [[電阻]] 與 [[電感]] 放在同一個回路中，因此除了穩態關係之外，還會出現由 [[自感]] 造成的暫態建立與衰減。

## 物理解讀
接通電源瞬間，電感阻止電流立刻跳到最終值；切斷電源時，電感又傾向維持原有電流。這就是 RL 電路最核心的物理。

## 交流觀點
在 [[交流電]] 中，電感會帶來 [[感抗]]，使電流相位落後電壓。

## 相關連結
- [[電阻]]
- [[電感]]
- [[電流]]
- [[自感]]
- [[感抗]]
- [[交流電]]
""",
    "02_concepts/RC電路.md": """---
type: concept
title: RC電路
domain: 電磁學
summary: RC電路由電阻與電容器組成，用來描述充放電、時間常數與交流濾波等典型現象。
prerequisites: ["[[電阻]]", "[[電容器]]", "[[電位差]]"]
related_laws: ["[[歐姆定律]]"]
related_quantities: ["[[電阻]]", "[[電位差]]"]
related_concepts: ["[[直流電路]]", "[[交流電]]", "[[電容抗]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# RC電路

## 核心想法
RC電路結合了 [[電阻]] 與 [[電容器]]。它最有價值的地方不在於「再多一個元件」，而在於系統開始具備儲能與時間延遲。

## 物理解讀
充電時，電容器上的電位差逐漸升高；放電時，儲存在電場中的能量逐漸釋出。這使 RC 電路成為理解時間常數與濾波的基本模型。

## 交流觀點
在 [[交流電]] 中，電容器會帶來 [[電容抗]]，使電流相位超前電壓。

## 相關連結
- [[電阻]]
- [[電容器]]
- [[電位差]]
- [[直流電路]]
- [[交流電]]
- [[電容抗]]
""",
    "02_concepts/RLC電路.md": """---
type: concept
title: RLC電路
domain: 電磁學
summary: RLC電路同時包含電阻、電感與電容器，是研究交流頻率響應與共振現象的標準模型。
prerequisites: ["[[電阻]]", "[[電感]]", "[[電容器]]"]
related_laws: ["[[歐姆定律]]", "[[楞次定律]]"]
related_quantities: ["[[電阻]]", "[[電感]]"]
related_concepts: ["[[交流電]]", "[[阻抗]]", "[[感抗]]", "[[電容抗]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# RLC電路

## 核心想法
RLC電路把耗散、磁場儲能與電場儲能三件事放進同一系統，因此會出現頻率選擇與共振等純電阻電路看不到的行為。

## 物理解讀
當電感與電容的效應彼此抵消時，系統的總 [[阻抗]] 會降到特別小，電流響應會特別強，這就是共振的電路版本。

## 分析重點
- 電阻決定能量耗散。
- 電感決定磁場儲能。
- 電容器決定電場儲能。

## 相關連結
- [[交流電]]
- [[阻抗]]
- [[感抗]]
- [[電容抗]]
- [[電阻]]
- [[電感]]
- [[電容器]]
""",
    "02_concepts/變壓器.md": """---
type: concept
title: 變壓器
domain: 電磁學
summary: 變壓器利用互感與交流磁通量變化，在不同線圈之間傳遞能量並改變電壓與電流比例。
prerequisites: ["[[互感]]", "[[交流電]]", "[[法拉第定律]]"]
related_laws: ["[[法拉第定律]]", "[[楞次定律]]"]
related_quantities: ["[[電動勢]]"]
related_concepts: ["[[磁通量]]", "[[位移電流]]"]
math_tools: []
tags: [physics, electromagnetism, concept]
updated: 2026-06-02
---

# 變壓器

## 核心想法
變壓器利用一次側電流建立變動磁場，再透過鐵芯與磁通量耦合，在二次側產生感應 [[電動勢]]。沒有變動磁通量，就沒有變壓器作用。

## 理想關係
若忽略能量損失，理想變壓器滿足
$$
\\frac{V_s}{V_p} = \\frac{N_s}{N_p}
$$

## 物理解讀
變壓器不是把「電流直接搬過去」，而是透過 [[互感]] 和 [[法拉第定律]] 進行能量轉移。它只能靠變動磁場工作，因此本質上依賴 [[交流電]]。

## 相關連結
- [[互感]]
- [[交流電]]
- [[法拉第定律]]
- [[楞次定律]]
- [[磁通量]]
- [[電動勢]]
""",
    "03_quantities/阻抗.md": """---
type: quantity
title: 阻抗
symbol: Z
unit: \\Omega
dimension: M L^2 T^-3 I^-2
domain: 電磁學
summary: 阻抗是交流電路中對電流的總體阻礙，結合了電阻與反應性元件的效果。
related_concepts: ["[[交流電]]", "[[RLC電路]]", "[[RL電路]]", "[[RC電路]]"]
related_laws: []
measurement_methods: []
tags: [physics, electromagnetism, quantity]
updated: 2026-06-02
---

# 阻抗

## 定義
在 [[交流電]] 中，元件不只表現出純粹的 [[電阻]]，還會因電感或電容造成相位差。阻抗就是把這些效果一起納入的總體量。

## 數學表達
對串聯 RLC 模型，阻抗大小常寫成
$$
Z = \\sqrt{R^2 + (X_L - X_C)^2}
$$

## 符號與單位
- 符號：$Z$
- SI 單位：$\\Omega$

## 物理解讀
阻抗越大，交流電流越難建立；但這個「難」不只是耗散，還包含儲能元件造成的相位延遲或超前。

## 相關連結
- [[交流電]]
- [[RL電路]]
- [[RC電路]]
- [[RLC電路]]
- [[感抗]]
- [[電容抗]]
""",
    "03_quantities/感抗.md": """---
type: quantity
title: 感抗
symbol: X_L
unit: \\Omega
dimension: M L^2 T^-3 I^-2
domain: 電磁學
summary: 感抗量化電感在交流電路中對電流變化的阻礙效果，頻率越高通常越大。
related_concepts: ["[[交流電]]", "[[RL電路]]", "[[RLC電路]]"]
related_laws: []
measurement_methods: []
tags: [physics, electromagnetism, quantity]
updated: 2026-06-02
---

# 感抗

## 定義
感抗是電感在交流情況下表現出的等效阻礙。它不是額外長出來的電阻，而是 [[電感]] 對電流變化率的反應。

## 數學表達
$$
X_L = \\omega L
$$

## 符號與單位
- 符號：$X_L$
- SI 單位：$\\Omega$

## 物理解讀
頻率越高，電流變化越快，電感越強烈地反抗這種變化，所以感抗會增大。

## 相關連結
- [[交流電]]
- [[RL電路]]
- [[RLC電路]]
- [[電感]]
- [[阻抗]]
""",
    "03_quantities/電容抗.md": """---
type: quantity
title: 電容抗
symbol: X_C
unit: \\Omega
dimension: M L^2 T^-3 I^-2
domain: 電磁學
summary: 電容抗量化電容器在交流電路中對電流的反應效果，頻率越高通常越小。
related_concepts: ["[[交流電]]", "[[RC電路]]", "[[RLC電路]]"]
related_laws: []
measurement_methods: []
tags: [physics, electromagnetism, quantity]
updated: 2026-06-02
---

# 電容抗

## 定義
電容抗是電容器在交流情況下表現出的等效阻礙。它反映電容器儲放電對交流電流的影響。

## 數學表達
$$
X_C = \\frac{1}{\\omega C}
$$

## 符號與單位
- 符號：$X_C$
- SI 單位：$\\Omega$

## 物理解讀
頻率越高，電容器越容易在短時間內完成充放電，因此電容抗會下降。

## 相關連結
- [[交流電]]
- [[RC電路]]
- [[RLC電路]]
- [[電容器]]
- [[阻抗]]
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
