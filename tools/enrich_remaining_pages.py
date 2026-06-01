#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")


def strip_wikilink(value: str) -> str:
    cleaned = value.strip().strip("'\"")
    match = WIKILINK_RE.fullmatch(cleaned)
    if not match:
        return cleaned
    return (match.group(2) or match.group(1)).strip()


def parse_list(raw: str) -> list[str]:
    raw = raw.strip()
    if raw == "[]":
        return []
    if not (raw.startswith("[") and raw.endswith("]")):
        return [strip_wikilink(raw)] if raw else []
    inner = raw[1:-1].strip()
    if not inner:
        return []
    items: list[str] = []
    for part in inner.split(","):
        item = strip_wikilink(part)
        if item:
            items.append(item)
    return items


def parse_frontmatter(text: str) -> tuple[str, dict[str, object]]:
    if not text.startswith("---\n"):
        return "", {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", {}
    raw = text[4:end]
    data: dict[str, object] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            data[key] = parse_list(value)
        else:
            data[key] = value.strip("'\"")
    return raw, data


def serial_links(items: list[str], fallback: str) -> str:
    if not items:
        return fallback
    if len(items) == 1:
        return f"[[{items[0]}]]"
    if len(items) == 2:
        return f"[[{items[0]}]] 與 [[{items[1]}]]"
    return "、".join(f"[[{item}]]" for item in items[:-1]) + f" 與 [[{items[-1]}]]"


def bullet_links(items: list[str], fallback: str) -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- [[{item}]]" for item in items)


def render_bullets(items: list[str]) -> str:
    return "\n".join(f"- {normalize_display_math(item)}" for item in items)


def render_numbered(items: list[str]) -> str:
    return "\n".join(f"{index + 1}. {normalize_display_math(item)}" for index, item in enumerate(items))


def normalize_display_math(text: str) -> str:
    return text.replace("$$\\n", "$$\n").replace("\\n$$", "\n$$")


def pick(items: list[str], fallback: list[str]) -> list[str]:
    return items if items else fallback


LAW_DATA: dict[str, dict[str, object]] = {
    "牛頓第一定律": {
        "math": [r"$$\n\sum \vec F = 0 \Rightarrow \vec v = \text{constant}\n$$"],
        "intuition": "它真正說明的不是『沒有力就沒有運動』，而是『沒有淨力就不需要改變運動狀態』。這條定律把慣性參考系的概念說清楚，讓後續動力學方程有了落腳點。",
        "derivation": [
            "這條定律通常不從更基礎的經典定律推導，而是作為建立經典力學參考系的出發點。",
            "它同時也可視為牛頓第二定律在 $\sum \\vec F=0$ 時的特殊情形。"
        ],
        "misconceptions": ["把靜止誤當成『自然狀態』，忽略等速直線運動同樣是無淨力狀態。"],
    },
    "牛頓第二定律": {
        "math": [r"$$\n\sum \vec F = \frac{d\vec p}{dt}\n$$", r"質量固定時可寫成 $$\n\sum \vec F = m\vec a\n$$"],
        "intuition": "這條定律把『原因』和『結果』分開: 力不是用來維持速度，而是用來改變動量。",
        "derivation": [
            r"由動量定義 $\vec p=m\vec v$ 出發，對時間微分得到 $\dfrac{d\vec p}{dt}=m\dfrac{d\vec v}{dt}+\vec v\dfrac{dm}{dt}$。",
            r"在質量固定的情況下 $\dfrac{dm}{dt}=0$，因此化為 $\sum \vec F=m\vec a$。"
        ],
        "misconceptions": ["把 $F=ma$ 視為永遠成立，而忘記更一般的形式其實是 $\vec F=d\vec p/dt$。"],
    },
    "牛頓第三定律": {
        "math": [r"$$\n\vec F_{AB} = -\vec F_{BA}\n$$"],
        "intuition": "作用力與反作用力不是互相抵消在同一物體上，而是分別作用在不同物體，這正是系統角度重要的地方。",
        "derivation": ["若把兩個交互作用物體視為封閉系統，內力成對出現，總動量改變只能來自外力。"],
        "misconceptions": ["把作用力與反作用力畫在同一張自由體圖上。"],
    },
    "牛頓萬有引力定律": {
        "math": [r"$$\nF = G\frac{m_1m_2}{r^2}\n$$"],
        "intuition": "它把天體運動和地面落體放進同一個規律裡，是經典力學統一性的代表。",
        "derivation": ["可由開普勒行星運動定律反推中心力必須近似遵守反平方律，再由比例常數定義出萬有引力常數 $G$。"],
        "misconceptions": ["把重力加速度 $g$ 誤以為是萬有引力定律本身，而忽略它只是近地表近似。"],
    },
    "萬有引力定律": {
        "math": [r"$$\nF = G\frac{m_1m_2}{r^2}\n$$"],
        "intuition": "它提供了遠距交互作用的定量模型，讓軌道、潮汐與逃逸速度可以落到同一套計算框架。",
        "derivation": ["由天體運動資料配合反平方律假設，可建立對質點間吸引力的數學描述。"],
        "misconceptions": ["把所有重力問題都直接套用近地表 $mgh$，忽略球對稱引力其實來自更一般的引力勢。"],
    },
    "庫侖定律": {
        "math": [r"$$\nF = k\frac{|q_1q_2|}{r^2}\n$$", r"向量形式為 $$\n\vec F_{12}=k\frac{q_1q_2}{r^2}\hat r\n$$"],
        "intuition": "它是靜電學的起點，告訴我們點電荷如何在空間中建立作用。",
        "derivation": ["它來自實驗歸納；進一步可被高斯定律與對稱性觀點重新組織。"],
        "misconceptions": ["把電荷正負號只當數值大小，忽略方向其實由同號斥、異號吸決定。"],
    },
    "高斯定律": {
        "math": [r"$$\n\oint \vec E\cdot d\vec A = \frac{Q_{\text{enc}}}{\varepsilon_0}\n$$"],
        "intuition": "它不是另一條和庫侖定律競爭的公式，而是把局部場分布轉成整體通量條件的更高階描述。",
        "derivation": ["從點電荷電場的反平方律出發，可驗證任意包住電荷的閉曲面都有相同總通量；再藉疊加推廣到一般電荷分布。"],
        "misconceptions": ["以為高斯定律可以直接解所有電場題，忽略它只有在高對稱時才真正省算。"],
    },
    "法拉第定律": {
        "math": [r"$$\n\mathcal{E} = -\frac{d\Phi_B}{dt}\n$$"],
        "intuition": "它說明改變的磁通量如何產生感應電場，這是電與磁互相耦合的入口。",
        "derivation": ["從實驗事實可知感應電動勢與磁通變化率成正比；負號則由楞次定律表達系統反抗通量改變的方向性。"],
        "misconceptions": ["把感應電流方向只當背誦規則，而沒把楞次定律理解成能量守恆的要求。"],
    },
    "歐姆定律": {
        "math": [r"$$\nV=IR\n$$"],
        "intuition": "它把導體內部微觀散射的複雜細節壓縮成巨觀線性關係，讓電路可被快速建模。",
        "derivation": ["在材料與溫度條件固定且近似線性響應時，可由實驗觀察建立電壓與電流成正比的關係。"],
        "misconceptions": ["把它當成所有材料、所有電流範圍都成立的普遍真理。"],
    },
    "熱力學第一定律": {
        "math": [r"$$\n\Delta U = Q - W\n$$"],
        "intuition": "這條定律是熱學裡的記帳規則，指出熱與功不是系統狀態，而是改變內能的兩種路徑。",
        "derivation": ["由大量實驗可知能量不會憑空消失，只會以熱、功或其他形式在系統與環境之間轉移。"],
        "misconceptions": ["把熱量 $Q$ 誤當成系統內部『存著的東西』。"],
    },
    "熱力學第二定律": {
        "math": [r"可逆過程中 $$\ndS = \frac{\delta Q_{\mathrm{rev}}}{T}\n$$", r"孤立系統常見表述為 $$\n\Delta S \ge 0\n$$"],
        "intuition": "第二定律補上了第一定律缺少的方向性，說明不是所有能量守恆的過程都會自發發生。",
        "derivation": ["由卡諾循環分析可知，不可能把從單一熱源吸收的熱完全轉成機械功；進一步可用熵來量化這種限制。"],
        "misconceptions": ["把熵只理解成『混亂度』，卻忘了它是能和可逆熱量、溫度、微觀態數連接的狀態量。"],
    },
    "熱力學第零定律": {
        "math": [r"若 $A$ 與 $B$ 熱平衡，且 $B$ 與 $C$ 熱平衡，則 $A$ 與 $C$ 熱平衡。"],
        "intuition": "這條定律看似樸素，卻是把『溫度』當成可比較物理量的邏輯基礎。",
        "derivation": ["它作為熱學狀態比較的公理性起點，支撐溫度計與熱平衡概念。"],
        "misconceptions": ["以為它只是口語常識，而忽略它其實決定了溫度能否作為一致的狀態參數。"],
    },
    "理想氣體方程式": {
        "math": [r"$$\nPV=nRT\n$$"],
        "intuition": "它把大量分子平均行為壓縮成幾個巨觀狀態量的關係，是熱學最常用的近似模型之一。",
        "derivation": ["可由氣體實驗定律整合得到，也可由動力論在稀薄、弱交互作用氣體近似下推出。"],
        "misconceptions": ["把真實氣體在高壓或低溫下也當成理想氣體處理。"],
    },
    "伯努力方程": {
        "math": [r"$$\nP+\frac{1}{2}\rho v^2+\rho gy = \text{constant}\n$$"],
        "intuition": "它是流體中的能量守恆語言，讓壓力、流速與高度差能放在同一條線上比較。",
        "derivation": ["沿流線把不可壓、無黏滯穩定流體的牛頓第二定律積分，可得到伯努力方程。"],
        "misconceptions": ["在明顯有黏滯耗散、渦流或壓縮效應時仍硬套伯努力方程。"],
    },
    "連續方程": {
        "math": [r"$$\nA_1v_1=A_2v_2\n$$", r"更一般的守恆形式可寫成 $$\n\frac{\partial \rho}{\partial t}+\nabla\cdot(\rho\vec v)=0\n$$"],
        "intuition": "它本質上是質量守恆在流體中的表達，說明流入與流出的平衡如何限制速度分布。",
        "derivation": ["對一小段流管套用質量守恆，在穩定不可壓近似下即得到截面積與流速的反比關係。"],
        "misconceptions": ["把 $Av$ 恆定錯用到可壓縮或非穩定流。"],
    },
    "機械能守恆": {
        "math": [r"$$\nK_i+U_i = K_f+U_f\n$$"],
        "intuition": "它把運動細節壓縮成狀態比較，只要非保守力不做功或可忽略，很多題目都能直接跳過受力微分方程。",
        "derivation": ["由功-能定理配合保守力所做功可寫成位能差，可推出機械能總和保持不變。"],
        "misconceptions": ["在有摩擦、阻力或外力做功時仍直接套用守恆。"],
    },
    "功能定理": {
        "math": [r"$$\nW_{\text{net}}=\Delta K\n$$"],
        "intuition": "它把力學問題從『力如何改變運動』轉成『功如何改變動能』，常是解題最省力的橋樑。",
        "derivation": [r"由 $\sum F_x=ma_x$ 與 $a_x=v\dfrac{dv}{dx}$ 可得 $\sum F_x\,dx = mv\,dv$，積分後得到淨功等於動能變化。"],
        "misconceptions": ["把任一單一力所做功都直接等同於總動能變化。"],
    },
    "動量定理": {
        "math": [r"$$\n\vec J = \int \vec F\,dt = \Delta \vec p\n$$"],
        "intuition": "它特別適合處理短時間大作用力的問題，因為這時候力的細節波形常不重要，總衝量才重要。",
        "derivation": [r"由 $\vec F=\dfrac{d\vec p}{dt}$ 對時間積分，立即得到衝量等於動量改變。"],
        "misconceptions": ["只記得『碰撞用動量』，卻不知道它根本來自牛頓第二定律的時間積分。"],
    },
    "動量守恆": {
        "math": [r"$$\n\sum \vec p_i = \sum \vec p_f\n$$"],
        "intuition": "它的力量在於不需要知道碰撞細節，只要總外力衝量可忽略，就能跨整個過程比較初末狀態。",
        "derivation": ["把系統內各物體的牛頓第二定律加總，內力成對抵消後，總動量改變只由外力決定；若外力衝量近似為零，則總動量守恆。"],
        "misconceptions": ["以為動量守恆一定只適用於碰撞。"],
    },
    "火箭方程": {
        "math": [r"$$\n\Delta v = v_e \ln \frac{m_i}{m_f}\n$$"],
        "intuition": "它展示了變質量系統的本質: 速度提升不是直接靠『推空氣』，而是靠噴出質量攜帶反向動量。",
        "derivation": ["對火箭與剛噴出的燃料小系統套用動量守恆，取微分形式後積分即可得到齊奧爾科夫斯基火箭方程。"],
        "misconceptions": ["把 $F=ma$ 直接套到整個變質量系統而不處理質量流出。"],
    },
    "虎克定律": {
        "math": [r"$$\nF=-kx\n$$"],
        "intuition": "它不是所有彈性行為的普遍真理，而是平衡點附近最重要的線性近似。",
        "derivation": ["若位能在穩定平衡點附近展開，最低階非零項通常是二次項，因此對應的恢復力在小位移下近似線性。"],
        "misconceptions": ["在大變形時仍假設彈簧力和位移完全成正比。"],
    },
    "質能等價": {
        "math": [r"$$\nE = mc^2\n$$"],
        "intuition": "它說明質量不是和能量平行並列的另一種東西，而是能量的一種表現方式。",
        "derivation": ["由狹義相對論的能量-動量關係可得靜止粒子的本徵能量為 $E_0=mc^2$。"],
        "misconceptions": ["把它誤解成『質量總會完全轉成光』，而不是更一般的能量關係。"],
    },
    "折射定律": {
        "math": [r"$$\nn_1\sin\theta_1 = n_2\sin\theta_2\n$$"],
        "intuition": "它描述波前在不同介質中因相速度改變而重新排列方向。",
        "derivation": ["可由惠更斯原理或費馬最短時間原理推出。"],
        "misconceptions": ["只背公式，不分辨角度必須以法線為基準。"],
    },
    "反射定律": {
        "math": [r"$$\n\theta_i = \theta_r\n$$"],
        "intuition": "它反映了邊界條件與幾何對稱性，而不是單純光線『彈回去』的口語印象。",
        "derivation": ["可由費馬原理或幾何對稱性得到。"],
        "misconceptions": ["把角度當成相對鏡面而不是相對法線測量。"],
    },
    "薄透鏡公式": {
        "math": [r"$$\n\frac{1}{f}=\frac{1}{d_o}+\frac{1}{d_i}\n$$"],
        "intuition": "它把幾何成像問題壓縮成物距、像距與焦距之間的代數關係。",
        "derivation": ["在近軸近似下，由相似三角形關係可推出薄透鏡成像公式。"],
        "misconceptions": ["忽略正負號約定與近軸近似條件。"],
    },
    "阿基米德原理": {
        "math": [r"$$\nF_b = \rho_{\text{fluid}} g V_{\text{disp}}\n$$"],
        "intuition": "浮力並不是額外神秘的向上力，而是流體壓力隨深度改變所產生的合力結果。",
        "derivation": ["由浸沒物體上下表面的壓力差積分，可得到淨向上力等於排開流體重量。"],
        "misconceptions": ["以為浮力只和物體重量有關，而忽略它主要由流體密度與排開體積決定。"],
    },
    "麥克斯威方程組": {
        "math": [
            r"$$\n\nabla\cdot\vec E=\frac{\rho}{\varepsilon_0}\n$$",
            r"$$\n\nabla\cdot\vec B=0\n$$",
            r"$$\n\nabla\times\vec E=-\frac{\partial \vec B}{\partial t}\n$$",
            r"$$\n\nabla\times\vec B=\mu_0\vec J+\mu_0\varepsilon_0\frac{\partial \vec E}{\partial t}\n$$",
        ],
        "intuition": "它們不是四條分散規則，而是把電荷、電流、電場與磁場的生成和耦合統一起來的語言。",
        "derivation": ["在大學普通物理層次，通常以實驗歸納配合高斯定律、法拉第定律與位移電流修正來理解它們的來源。"],
        "misconceptions": ["把四條方程分開背誦，卻看不出它們共同決定了電磁波。"],
    },
}


QUANTITY_DATA: dict[str, dict[str, str]] = {
    "速度": {"definition": "瞬時速度是位置對時間的導數，描述物體運動快慢與方向。", "meaning": "它衡量的是位置改變的速率與方向結構，而不只是快慢。"},
    "加速度": {"definition": "加速度是速度對時間的導數，或位置對時間的二階導數。", "meaning": "它衡量的是運動狀態改變得多快，直接反映受力效果。"},
    "質量": {"definition": "在普通物理中，質量表徵慣性大小，也進入引力作用的強度描述。", "meaning": "它衡量系統抗拒速度改變的程度。"},
    "動量": {"definition": "動量定義為 $\vec p=m\vec v$，是描述運動狀態最核心的向量量之一。", "meaning": "它衡量的是運動狀態的累積效果，特別適合處理交互作用與碰撞。"},
    "壓力": {"definition": "壓力是單位面積所受正向力，常寫作 $P=F_{\perp}/A$。", "meaning": "它衡量的是作用在面上的力如何分布。"},
    "密度": {"definition": "密度是單位體積所含的質量，寫作 $\rho=m/V$。", "meaning": "它衡量的是物質在空間中的集中程度。"},
    "流量": {"definition": "體積流量描述單位時間通過截面的流體體積，常寫作 $Q=Av$。", "meaning": "它衡量的是輸運過程的通過速率。"},
    "電荷": {"definition": "電荷是電磁交互作用的源頭性物理量，決定物體如何產生與感受電場。", "meaning": "它衡量的是物體參與電磁作用的能力與符號性質。"},
}


EXPERIMENT_DATA: dict[str, dict[str, object]] = {
    "雙狹縫實驗": {
        "observables": ["條紋間距", "亮暗分布", "在單光子條件下長時間累積出的統計圖樣"],
        "results": "理想情況下會出現規律的干涉條紋，顯示振幅疊加而不是單純粒子軌跡相加。",
        "impact": "它先是波動光學的關鍵證據，後來又成為理解量子測量與波粒二象性的經典入口。",
    },
    "密立根油滴實驗": {
        "observables": ["油滴半徑估計值", "上升與下降速度", "平衡時外加電場強度"],
        "results": "可由多次量測萃取出電荷量呈離散整數倍，進而估計基本電荷 $e$。",
        "impact": "它讓電荷量子化從猜想變成可重複量測的結果。 ",
    },
}


TOOL_DATA: dict[str, dict[str, object]] = {
    "向量": {
        "definition": "向量是在座標變換下有特定分量轉換規則的量，在普通物理裡常先從幾何箭頭與分量表示入門。",
        "operations": ["向量分解與分量合成", "以內積提取同向成分", "以外積描述面積、轉矩與磁力方向"],
    },
    "導數": {
        "definition": "導數描述函數對自變數的局部變化率，是把連續變化寫成數學語言的第一步。",
        "operations": ["由 $x(t)$ 求 $v=dx/dt$", "由 $v(t)$ 求 $a=dv/dt$", "利用鏈鎖律切換不同變數表示法"],
    },
    "積分": {
        "definition": "積分把局部貢獻累加成整體結果，在物理中經常代表累積量、總量或由微元拼回巨觀量。",
        "operations": ["由速度積分求位移", "由力對位移積分求功", "由密度函數積分求總質量或總電荷"],
    },
}

CORE_LAW_OVERRIDES: dict[str, dict[str, object]] = {
    "牛頓第二定律": {
        "history": "牛頓第二定律的重要性不只在於公式本身，而在於它把『交互作用』和『運動狀態改變』之間的因果關係真正定量化。它是整個經典動力學的骨架，後續的受力分析、能量法與動量法都能回溯到這個核心。",
        "verification": "[[小車軌道實驗]]、低摩擦滑車量測與圓周運動分析都能檢驗加速度如何隨淨力與質量改變。",
        "applications": [
            "建立自由體圖後，依不同方向分量列式，處理斜面、張力、摩擦與聯立多物體問題。",
            "在圓周運動中，把向心需求寫成徑向淨力條件，判斷是哪一個真實作用力提供曲率。",
            "在變質量或高速度問題中，退回一般形式 $\\dfrac{d\\vec p}{dt}$，而不是機械地套用 $m\\vec a$。"
        ],
        "problem_frames": [
            "先選系統，再選座標，最後才寫方程。很多錯誤其實發生在列式之前。",
            "若題目真正要的是速度、位移或臨界條件，先判斷直接動力學還是能量法更省力。",
            "遇到接觸力與約束問題時，先找幾何或運動學關係，再做受力分析。"
        ],
        "boundary": [
            "常見形式 $F=ma$ 預設質量固定。",
            "必須在慣性參考系中使用；非慣性系需加入慣性力。",
            "相對論情況下仍應以 $d\\vec p/dt$ 為主。"
        ],
    },
    "功能定理": {
        "history": "功能定理的重要處在於，它讓我們不必每次都沿時間追蹤加速度，而能直接用總做功比較初末態。這是從力學微分方程走向能量觀點的第一座橋。",
        "verification": "滑車受恆力加速、斜面滑動與彈簧釋放都能把淨功和動能變化直接對比。",
        "applications": [
            "處理位移已知但時間不重要的受力問題。",
            "快速判斷多個力共同作用下速度會增加還是減少。",
            "作為位能、保守力與機械能守恆的過渡入口。"
        ],
        "problem_frames": [
            "先列出哪些力真的做功，哪些力因位移垂直而不做功。",
            "若力隨位置改變，要主動回到積分形式。",
            "若最終目標只是速度與位移，通常比直接求 $a(t)$ 更有效率。"
        ],
        "boundary": [
            "它談的是淨功與動能變化，不是任一單一力都直接對應總動能變化。",
            "若要進一步談位能，需再引入保守力假設。",
            "高速度情況下動能形式要改寫。"
        ],
    },
    "動量守恆": {
        "history": "動量守恆真正厲害的地方，是它把注意力從『碰撞細節』移到『系統與外界的交換』。只要外力衝量可忽略，再複雜的內部作用也能被壓縮成初末態關係。",
        "verification": "[[兩滑車碰撞實驗]]、反沖模型與火箭噴流分析都能直接展示總動量的守恆。",
        "applications": [
            "一維與二維碰撞、爆炸分裂、反沖與火箭推進。",
            "和能量條件聯立，區分彈性碰撞與非彈性碰撞。",
            "在短時間強交互作用中，把整個過程壓縮成初末態比較。"
        ],
        "problem_frames": [
            "第一步永遠是選系統，分清楚哪些力算外力。",
            "若碰撞時間很短，常可近似忽略重力等長時效應。",
            "二維問題要按分量守恆，不能把向量關係誤寫成純量大小守恆。"
        ],
        "boundary": [
            "守恆的是總動量向量，不是速度或動能。",
            "若外力衝量不可忽略，就要改寫成總動量改變等於外力衝量。",
            "內部耗散不破壞動量守恆，但通常會影響能量關係。"
        ],
    },
    "機械能守恆": {
        "history": "機械能守恆把原本依賴局部受力與路徑積分的資訊，濃縮成狀態量之間的比較。這種『只看初末態』的能力，是大學力學解題效率大幅提升的來源。",
        "verification": "[[滑軌能量轉換實驗]]、擺動系統與低摩擦滑動過程都能近似看到動能與位能的互換。",
        "applications": [
            "求最低高度、最大壓縮量、臨界速度與逃逸條件。",
            "在路徑複雜但非保守力可忽略時，快速連接初態與末態。",
            "作為小振動、位能井與穩定平衡分析的基礎。"
        ],
        "problem_frames": [
            "先確認非保守力是否可以忽略，或是否需要額外加入耗散做功項。",
            "先選好位能零點，再把所有初末態能量寫完整。",
            "若還需要中間受力資訊，先用能量求速度，再回頭接動力學方程。"
        ],
        "boundary": [
            "關鍵是系統選擇與非保守力處理，不是看到位能就自動守恆。",
            "位能零點可自由選，但能量差不能亂改。",
            "若有摩擦或外力輸入，應改寫成含非保守功的能量平衡。"
        ],
    },
    "高斯定律": {
        "history": "高斯定律的重要不只在於它是一條公式，而在於它把靜電學從『點對點作用』提升到『整體幾何通量』的層次。這也是場論視角真正開始發揮威力的地方。",
        "verification": "[[法拉第冰桶實驗]]、導體靜電平衡性質，以及對已知對稱分布的場型反推都能支持高斯定律。",
        "applications": [
            "快速求解球對稱、柱對稱與平面對稱系統的電場。",
            "說明導體內部靜電平衡時電場為零、電荷分布在表面等結果。",
            "把電荷總量與場的幾何流出量聯繫起來，作為更完整電磁理論的基本方程之一。"
        ],
        "problem_frames": [
            "先問自己是否有足夠對稱，讓高斯面上的場大小固定或方向可控。",
            "高斯面是計算工具，不是實際物體表面。",
            "若對稱不足，定律仍成立，但未必能幫你把積分做完。"
        ],
        "boundary": [
            "定律本身普遍成立，但『好用』高度依賴對稱。",
            "應明確區分包圍電荷與外部電荷在通量問題中的角色。",
            "在動態電磁情況下，它仍成立，但要和其他方程一起看。"
        ],
    },
    "庫侖定律": {
        "history": "庫侖定律讓靜電學像萬有引力一樣，能從中心力與反平方律出發建立第一層模型。它是從單一電荷作用走向電場概念的起點。",
        "verification": "扭秤法、力平衡量測與由場分布回推作用規律，都能支撐電荷乘積與距離反平方的結構。",
        "applications": [
            "計算少量點電荷的作用力與平衡位置。",
            "作為建立電場定義的出發點，再過渡到連續分布積分。",
            "搭配向量分解與疊加處理非共線多電荷系統。"
        ],
        "problem_frames": [
            "先畫幾何配置，再判斷吸引或排斥，最後才做向量相加。",
            "若電荷很多，先想是否該改用電場或電位。",
            "遇到高對稱系統時，通常應改用高斯定律。"
        ],
        "boundary": [
            "最直接形式是點電荷模型；分布有尺寸時需積分或近似。",
            "在介質中常需改寫比例常數。",
            "本質上是靜電近似；若有明顯時間變化，要進入完整電磁描述。"
        ],
    },
    "熱力學第一定律": {
        "history": "第一定律來自機械功與熱量等價的建立過程。從焦耳等人的實驗開始，熱不再被理解成某種物質，而被納入能量守恆的統一圖像。",
        "verification": "熱功當量實驗、氣體壓縮膨脹與熱機能量平衡量測，都能支撐第一定律。",
        "applications": [
            "分析等容、等壓、等溫與絕熱過程中的熱、功與內能變化。",
            "把熱機、冷機與理想氣體循環寫成可逐段記帳的問題。",
            "在統計物理入口中，把微觀自由度變化連回巨觀能量收支。"
        ],
        "problem_frames": [
            "先分清楚系統、環境與符號約定，再寫 $\\Delta U = Q - W$。",
            "先問哪個量是狀態量，哪個量是過程量。",
            "若是一個循環，立刻利用整圈下來 $\\Delta U=0$ 來簡化。"
        ],
        "boundary": [
            "定律普遍成立，但不同教材對功的正負號約定可能不同。",
            "內能的內容可能包含化學、電磁或相變貢獻，不一定只像理想氣體那樣簡單。",
            "第一定律只談守恆，不單獨決定過程方向。"
        ],
    },
    "熱力學第二定律": {
        "history": "第二定律最初看起來像是在限制熱機效率，但它最後變成所有自然過程方向性的普遍語言。它補上了第一定律無法回答的『為什麼有些過程會自發發生』。",
        "verification": "熱機效率上限、不可逆傳熱、混合過程與冷熱自發流動方向，都是第二定律最直接的檢驗。",
        "applications": [
            "比較不同循環與熱機的理論效率上限。",
            "判斷一個過程是否能自發發生，以及逆轉它需要多少代價。",
            "把巨觀熱學限制和統計物理中的微觀態數觀點接起來。"
        ],
        "problem_frames": [
            "先判斷題目是要用熱機敘述、Clausius 敘述，還是直接用熵變分析。",
            "循環題通常先用第一定律做能量記帳，再用第二定律做方向與效率限制。",
            "看到『最大效率』『最小外功』『是否自發』這類字眼時，幾乎一定要用第二定律。"
        ],
        "boundary": [
            "公式 $dS=\\delta Q_{\\mathrm{rev}}/T$ 是沿可逆路徑定義狀態量，不能對所有不可逆過程直接用等號。",
            "第二定律限制的是過程方向與可達性，不是否定局部熵減在更大系統中的可能性。",
            "很多教材會交替使用熱機表述與熵表述，讀題時要先辨識語境。"
        ],
    },
    "虎克定律": {
        "history": "虎克定律看似只在講彈簧，實際上它是『平衡點附近線性恢復』的普遍模型。從普通力學到波動、場論與量子諧振子，都能看到它的影子。",
        "verification": "彈簧伸長量測、載重與位移的近線性區段，以及振動週期與彈性常數的對應都能驗證虎克近似。",
        "applications": [
            "建立簡諧運動方程 $m\\ddot x + kx = 0$。",
            "求彈簧能量、最大壓縮量與振動週期。",
            "作為任何穩定平衡附近小振動近似的基礎。"
        ],
        "problem_frames": [
            "先確認位移是否足夠小，系統是否還在線性響應區。",
            "若題目涉及振動，通常要連同位能 $U=\\frac12 kx^2$ 一起思考。",
            "多彈簧系統先求等效彈性常數，再進入動力學或能量分析。"
        ],
        "boundary": [
            "它是近似，不是所有變形範圍都成立。",
            "材料彈性與彈簧模型要分清楚，不同幾何與材料會改變有效 $k$。",
            "非線性區域應改回更完整的位能或材料模型。"
        ],
    },
    "伯努力方程": {
        "history": "伯努力方程的價值在於，它把流體運動從單純受力圖像提升到能量圖像。這使文氏管、皮托管與基礎流量估算都有了共同語言。",
        "verification": "[[文氏管]] 的壓差量測、皮托管速度估計與自由液面高度比較，都可以看見伯努力關係的近似成立。",
        "applications": [
            "求管道不同截面的壓力差與流速變化。",
            "結合連續方程分析收縮管、噴嘴與流量量測裝置。",
            "把流體問題轉寫成能量守恆近似，而不必逐點解完整流場。"
        ],
        "problem_frames": [
            "先確認是否為穩定、不可壓且可忽略黏滯的近似情境。",
            "再決定要沿同一條流線比較哪兩點，並把三項能量密度寫完整。",
            "若題目同時給了截面積，通常要和連續方程聯立。"
        ],
        "boundary": [
            "只適合在明確條件下沿流線使用。",
            "有泵浦、摩擦損失或渦流時，需加入額外能量項。",
            "高壓縮性流動不能直接沿用最簡單形式。"
        ],
    },
    "動量定理": {
        "history": "動量定理的力量，在於它把短時間、強作用的複雜過程濃縮成時間積分後的總效果。這讓我們不必完整知道碰撞時每一瞬間的力，只要掌握衝量就能描述狀態改變。",
        "verification": "[[兩滑車碰撞實驗]]、落球接觸時間量測與安全氣囊減衝分析，都能直接看見延長作用時間如何改變平均力而保持相同動量改變。",
        "applications": [
            "分析碰撞、擊球、爆炸反衝等短時大力問題。",
            "比較不同制動方式在相同動量改變下，平均力為何不同。",
            "作為從牛頓第二定律過渡到動量守恆與火箭方程的橋樑。"
        ],
        "problem_frames": [
            "先判斷題目要的是瞬時力、平均力，還是總衝量；三者不要混在一起。",
            "若受力隨時間改變，優先考慮面積觀點，也就是力-時間圖下的面積。",
            "若系統外力衝量可忽略，再往上升級成整體的動量守恆。"
        ],
        "boundary": [
            "動量定理始終成立，但計算時要明確分清系統與外力。",
            "衝量是向量，分量方向不能省略。",
            "若碰撞時間不短、外力不可忽略，就不能把問題直接當成封閉碰撞。"
        ],
    },
    "法拉第定律": {
        "history": "法拉第定律標誌著電與磁不再是彼此孤立的現象。它告訴我們，變動的磁場可以主動生成環形電場，這一步是從靜電學走向完整電磁學的真正轉折。",
        "verification": "[[法拉第圓盤]]、線圈穿磁通變化實驗、交流發電機模型與變壓器感應量測，都能直接支持磁通變化與感應電動勢之間的關係。",
        "applications": [
            "分析導體棒切割磁力線、線圈穿磁通改變與感應電流方向。",
            "理解發電機、變壓器、感應加熱與交流電源的工作核心。",
            "作為麥克斯威方程組中旋度形式的一個具體物理入口。"
        ],
        "problem_frames": [
            "先分清磁通改變來自磁場變、面積變，還是夾角變。",
            "再判斷感應電動勢是由哪一條閉合路徑定義，避免把局部電場和總電壓混淆。",
            "方向題一律回到楞次定律，從『反抗原本變化』去想，而不是死背手勢規則。"
        ],
        "boundary": [
            "磁通變化不等於磁場大小一定變，幾何改變同樣可以造成感應。",
            "符號中的負號表達方向性與能量守恆，不是單純數值相減。",
            "若路徑、面或場的定義沒說清楚，公式很容易被用錯。"
        ],
    },
    "連續方程": {
        "history": "連續方程的核心不是流體技巧，而是守恆思想。它把質量守恆翻成場的語言，讓『某處變多』必須對應到『別處流進來』，因此成為流體力學與場論的共同骨架。",
        "verification": "收縮管流速量測、[[文氏管]] 的截面比較與穩定流管路實驗，都能顯示流量如何在不同截面間保持一致。",
        "applications": [
            "處理穩定不可壓流中的管徑變化與流速比較。",
            "與伯努力方程聯立，求壓差、流速與流量。",
            "作為一般守恆方程進入流體與電磁場分析的入門形式。"
        ],
        "problem_frames": [
            "先判斷是否可以用穩定、不可壓近似；若可以，才可直接寫成 $A_1v_1=A_2v_2$。",
            "若題目出現密度變化，就要回到更一般的 $\nabla\\cdot(\\rho\\vec v)$ 形式思考。",
            "看到截面變窄、流速如何變、流量是否改變，幾乎都該先想到連續方程。"
        ],
        "boundary": [
            "最常見的簡式只適用於穩定不可壓流。",
            "連續方程守恆的是質量流，不是速度本身。",
            "若有洩漏、分支或源匯項，控制體的選取必須更小心。"
        ],
    },
    "理想氣體方程式": {
        "history": "理想氣體方程式把大量分子的複雜微觀運動壓縮成少數幾個巨觀變數之間的關係，是熱學裡最成功也最常用的近似模型之一。它之所以重要，不是因為永遠精確，而是因為它提供了清楚可算的第一層結構。",
        "verification": "波以耳、查理與亞佛加厥實驗關係的整合，以及稀薄氣體在常溫常壓下的狀態量測，都能支持 $PV=nRT$ 的近似成立。",
        "applications": [
            "連結壓力、體積、溫度與莫耳數，快速分析熱力學過程。",
            "與第一定律聯立，求等溫、等壓、等容與絕熱過程中的熱和功。",
            "作為動力學理論、比熱與內能模型的基礎入口。"
        ],
        "problem_frames": [
            "先確認系統是否可近似成稀薄、弱交互作用氣體。",
            "再判斷是哪一類過程固定了哪些狀態量，避免把過程條件和狀態方程混在一起。",
            "若題目要的是內能、功或熱，不要只停在 $PV=nRT$，要立刻接第一定律。"
        ],
        "boundary": [
            "高壓、低溫、接近液化或有強分子作用時，理想近似會失效。",
            "它是狀態方程，不直接告訴你熱與功如何分配。",
            "不同系統的自由度與比熱資訊需要額外模型補足。"
        ],
    },
    "牛頓萬有引力定律": {
        "history": "牛頓萬有引力定律最深刻的地方，在於它把地上的落體和天空中的行星放進同一套數學規律。這種『天地合一』的視角，是近代物理定律觀念真正成熟的代表。",
        "verification": "行星軌道資料、衛星運行週期、潮汐現象與近地表重力加速度估算，都能回過頭來檢驗反平方引力模型。",
        "applications": [
            "求兩質點間引力、軌道條件、逃逸速度與重力位能。",
            "處理球對稱天體外部場，連結到中心力與開普勒運動。",
            "作為理解近地表 $g$、潮汐與天體力學的共同基礎。"
        ],
        "problem_frames": [
            "先確認是質點模型、球對稱模型，還是需要做分佈積分。",
            "若題目提到軌道或週期，往往要把引力和向心需求聯立。",
            "若題目只在近地表小高度範圍內，再考慮是否可退化成 $mgh$ 或定值 $g$。"
        ],
        "boundary": [
            "近地表常數重力只是這條定律的小範圍近似。",
            "非球對稱或大尺度精密問題可能需要更完整模型。",
            "相對論強重力情境下，牛頓形式不再足夠。"
        ],
    },
    "熱力學第零定律": {
        "history": "第零定律看起來很樸素，卻替『溫度』這個量奠定了邏輯基礎。沒有這條定律，我們只能說兩物體彼此不再改變，卻無法把這種關係抽象成一個可比較、可量測的狀態參數。",
        "verification": "溫度計校準、不同材料溫度計在同一平衡狀態下給出一致讀值，都是第零定律最直接的操作性證據。",
        "applications": [
            "定義熱平衡，讓溫度成為可量測且可比較的物理量。",
            "支撐所有狀態方程、熱容量與熱接觸問題的基本語言。",
            "在統計物理中對應到不同系統達到同一熱參數的條件。"
        ],
        "problem_frames": [
            "看到熱接觸後最後溫度、平衡條件、溫度計讀值一致性時，先想到第零定律。",
            "把它當作『能否用同一個溫度描述系統』的前提，而不是拿來直接算熱量的工具。",
            "若後續要計算熱交換，再往第一定律與比熱模型延伸。"
        ],
        "boundary": [
            "它提供的是平衡判準，不直接給熱量或能量轉移公式。",
            "必須在可達熱平衡的條件下談論。",
            "非平衡系統中的『局部溫度』需要更細緻定義。"
        ],
    },
    "歐姆定律": {
        "history": "歐姆定律之所以經典，是因為它把材料內部複雜的載流子散射統計，濃縮成宏觀上易於使用的線性關係。這讓電路分析得以像代數一樣展開。",
        "verification": "電阻元件的伏安特性量測、不同長度與截面導線的比較，以及固定溫度下的線性擬合，都能檢驗歐姆區域是否成立。",
        "applications": [
            "求電路中的電流、電壓分配與功率耗散。",
            "連結材料電阻率、幾何尺寸與等效電阻。",
            "作為從微觀導電機制過渡到宏觀電路模型的第一步。"
        ],
        "problem_frames": [
            "先確認元件是否真的在歐姆區，也就是伏安關係近似線性。",
            "再分清楚局部形式 $\\vec J=\\sigma \\vec E$ 和電路形式 $V=IR$ 各自的語境。",
            "複雜電路先做串並聯、節點或回路化簡，再代入歐姆關係。"
        ],
        "boundary": [
            "二極體、燈泡、半導體等常不滿足固定電阻近似。",
            "溫度改變可能讓電阻不再視為常數。",
            "它是材料響應近似，不是所有導電現象的普遍真理。"
        ],
    },
    "折射定律": {
        "history": "折射定律的重要不只在計算角度，而在於它揭示了波前如何因介質中傳播速度改變而重新定向。這使幾何光學背後其實站著更深的波動觀點與變分原理。",
        "verification": "光線穿越水槽、玻璃板與稜鏡的角度量測，對不同入射角做資料擬合，都能驗證正弦比值與折射率的關係。",
        "applications": [
            "分析介面轉向、全反射條件與稜鏡偏折。",
            "作為薄透鏡、成像與光纖導引的局部基礎。",
            "把幾何光學和波速、波長改變的物理圖像接起來。"
        ],
        "problem_frames": [
            "先把所有角度都改成相對法線測量。",
            "再判斷光是進入高折射率還是低折射率介質，先預測偏向法線還是離開法線。",
            "若題目涉及臨界角或多層介質，要逐界面處理，不能一次跳到底。"
        ],
        "boundary": [
            "公式基於清楚介面與幾何光學近似。",
            "若尺寸接近波長、散射強或介質不均勻，需回到波動描述。",
            "全反射只發生在高折射率往低折射率傳播時。"
        ],
    },
    "反射定律": {
        "history": "反射定律看似簡單，卻是幾何光學對稱性最乾淨的例子之一。它讓我們看到，很多光路規則並不是憑經驗死記，而是能由更基本的最短時間原理或邊界幾何推出。",
        "verification": "平面鏡反射角量測、雷射入射與反射路徑實驗，都能穩定驗證入射角等於反射角。",
        "applications": [
            "處理平面鏡成像、反射路徑設計與多鏡面折返。",
            "作為光學儀器、望遠鏡與日常成像裝置中的局部規則。",
            "幫助建立法線、角度定義與邊界條件的標準語言。"
        ],
        "problem_frames": [
            "所有角度先相對法線，不要相對鏡面。",
            "畫圖時先找法線，再標入射與反射方向，幾何會清楚很多。",
            "若題目問像的位置，反射定律通常只是第一步，還要接幾何成像。"
        ],
        "boundary": [
            "理想形式主要對應鏡面反射；粗糙表面會出現漫反射。",
            "角度定義一旦錯，整題通常都會跟著偏掉。",
            "當需要波動相位資訊時，僅靠幾何反射定律不夠。"
        ],
    },
    "薄透鏡公式": {
        "history": "薄透鏡公式的價值，在於它把複雜的折射路徑壓縮成少數距離參數之間的可操作關係。對學習者來說，它是從單一介面折射走向完整成像系統的第一個總結工具。",
        "verification": "凸透鏡成像實驗、物距與像距掃描量測，以及焦距反推與直接量測的比對，都能驗證近軸近似下薄透鏡公式的有效性。",
        "applications": [
            "求像距、放大率、焦距與成像條件。",
            "分析照相機、投影機、放大鏡與顯微鏡的基本幾何成像。",
            "作為從單一折射規律進入光學系統設計的入門模型。"
        ],
        "problem_frames": [
            "先明確採用哪一套正負號約定，物距、像距、焦距都要一致。",
            "再判斷是真像還是虛像、放大還是縮小，先做物理解釋再代數求值。",
            "若題目同時問影像大小，別忘了把放大率公式一起聯立。"
        ],
        "boundary": [
            "核心前提是薄透鏡與近軸近似。",
            "大角度光線、像差或厚透鏡效應不能硬塞進簡式公式。",
            "不同課本符號慣例不同，做題前要先統一。"
        ],
    },
}


LAW_STEP_BY_STEP_OVERRIDES: dict[str, list[str]] = {
    "牛頓第二定律": [
        r"從動量定義 $\vec p = m\vec v$ 出發。",
        r"對時間微分，得到 $ \dfrac{d\vec p}{dt} = m\dfrac{d\vec v}{dt} + \vec v \dfrac{dm}{dt} $。",
        r"若質量固定，則 $dm/dt=0$，所以 $ \dfrac{d\vec p}{dt} = m\vec a $。",
        r"把外力定義成動量變化率，就得到一般形式 $ \sum \vec F = \dfrac{d\vec p}{dt} $。",
        r"因此在質量固定的普通物理問題中，可簡化成 $ \sum \vec F = m\vec a $。",
    ],
    "功能定理": [
        r"從一維牛頓第二定律 $F_x = ma_x$ 出發。",
        r"兩邊同乘位移微元 $dx$，得 $F_x\,dx = ma_x\,dx$。",
        r"利用 $ a_x = dv/dt = (dv/dx)(dx/dt) = v\,dv/dx $，右邊變成 $m v\,dv$。",
        r"因此 $F_x\,dx = m v\,dv$。",
        r"沿初態到末態積分，得到 $ \int F_x\,dx = \int m v\,dv = \dfrac12 m v_f^2 - \dfrac12 m v_i^2 $。",
        r"左邊就是淨功，所以得到 $ W_{\text{net}} = \Delta K $。",
    ],
    "機械能守恆": [
        r"先從功能定理開始: $ W_{\text{net}} = \Delta K $。",
        r"把總做功拆成保守力與非保守力兩部分，寫成 $ W_{\text{cons}} + W_{\text{noncons}} = \Delta K $。",
        r"若保守力可由位能描述，則 $ W_{\text{cons}} = -\Delta U $。",
        r"代回可得 $ -\Delta U + W_{\text{noncons}} = \Delta K $。",
        r"整理後得到 $ \Delta K + \Delta U = W_{\text{noncons}} $。",
        r"若非保守力做功為零，便得到 $ \Delta (K+U)=0 $，也就是 $K_i+U_i=K_f+U_f$。",
    ],
    "高斯定律": [
        r"先考慮位於球心的單一點電荷 $Q$，其電場大小為 $ E = \dfrac{1}{4\pi\varepsilon_0}\dfrac{Q}{r^2} $。",
        r"取半徑為 $r$ 的球面作為高斯面，因為球對稱，球面上各點電場大小相同且方向與面元平行。",
        r"因此通量積分可化成 $ \oint \vec E\cdot d\vec A = E \oint dA = E(4\pi r^2) $。",
        r"代入 $E$ 的表達式，得到 $ \oint \vec E\cdot d\vec A = \dfrac{1}{4\pi\varepsilon_0}\dfrac{Q}{r^2}(4\pi r^2)=Q/\varepsilon_0 $。",
        r"對多個點電荷可利用疊加原理逐項相加，結果只留下包圍電荷總量。",
        r"因此推廣到一般情形，就得到 $ \oint \vec E\cdot d\vec A = Q_{\text{enc}}/\varepsilon_0 $。",
    ],
    "法拉第定律": [
        r"先把穿過迴路所圍面積的磁通定義成 $ \Phi_B = \int \vec B\cdot d\vec A $。",
        r"實驗顯示，只要磁通隨時間改變，迴路中就會出現感應電動勢。",
        r"把這個比例關係寫成 $ \mathcal{E} \propto - d\Phi_B/dt $，負號由楞次定律決定方向。",
        r"選定 SI 制後，比例常數為 1，因此得到 $ \mathcal{E} = -\dfrac{d\Phi_B}{dt} $。",
        r"若用迴路積分表示感應電場，則可寫成 $ \oint \vec E\cdot d\vec l = -\dfrac{d}{dt}\int \vec B\cdot d\vec A $。",
        r"這就是法拉第定律的積分形式，也是旋度形式的起點。",
    ],
    "理想氣體方程式": [
        r"從實驗定律出發，固定溫度與莫耳數時有波以耳定律 $PV=\text{const}$。",
        r"固定壓力與莫耳數時有查理定律 $V\propto T$。",
        r"固定體積與莫耳數時有蓋-呂薩克關係 $P\propto T$。",
        r"再加上固定溫壓下體積與莫耳數成正比的亞佛加厥觀點，可把這些結果整合成 $PV \propto nT$。",
        r"引入比例常數 $R$，就得到狀態方程 $PV=nRT$。",
        r"若從動力學理論出發，亦可由分子平均平動動能與壁面碰撞壓力重建同一結果。",
    ],
    "熱力學第一定律": [
        r"把系統內部狀態量的改變記成 $\Delta U$。",
        r"若系統吸收熱量 $Q$，其內能傾向增加。",
        r"若系統對外做功 $W$，則這部分能量離開系統，因此內能減少。",
        r"把兩種能量交換方式合併記帳，就得到 $ \Delta U = Q - W $。",
        r"若教材採用『外界對系統做功為正』的約定，則公式會改寫，但物理內容相同。",
        r"因此第一定律本質上是在說能量不會憑空產生或消失，只會改變儲存位置與交換形式。",
    ],
    "薄透鏡公式": [
        r"在近軸近似下，取穿過透鏡中心的主光線近似不偏折，並考慮平行主軸的入射光經透鏡後通過焦點。",
        r"由幾何成像圖可建立兩組相似三角形，分別連結物高、像高、物距與像距。",
        r"由第一組相似關係可得放大率 $ m = -d_i/d_o $。",
        r"再利用焦點光線所形成的第二組相似關係，把焦距 $f$ 與像距、物距聯立。",
        r"消去像高與物高後，可得到 $ \dfrac{1}{f} = \dfrac{1}{d_o} + \dfrac{1}{d_i} $。",
        r"這個結果成立的核心前提，是薄透鏡與近軸光線近似。",
    ],
}


def law_override(title: str, key: str):
    return CORE_LAW_OVERRIDES.get(title, {}).get(key)


def law_math(title: str) -> list[str]:
    return list(LAW_DATA.get(title, {}).get("math", [f"{title} 常需要搭配前提條件與相關量一起理解，不能只背一條孤立公式。"]))


def law_intuition(title: str, domain: str) -> str:
    return str(LAW_DATA.get(title, {}).get("intuition", f"{title} 在 {domain} 中的角色，是把零散現象壓縮成可反覆使用的關係式，讓我們能從描述走到預測。"))


def law_derivation(title: str, prerequisites: list[str], quantities: list[str]) -> list[str]:
    fallback = [
        f"先確認 {title} 所依賴的理想化假設與適用範圍，這一步通常比代公式更重要。",
        f"再把 {serial_links(quantities, '相關物理量')} 與 {serial_links(prerequisites, '先備概念')} 連成數學關係，得到 {title} 的工作形式。"
    ]
    return list(law_override(title, "derivation") or LAW_DATA.get(title, {}).get("derivation", fallback))


def law_misconceptions(title: str) -> list[str]:
    return list(law_override(title, "misconceptions") or LAW_DATA.get(title, {}).get("misconceptions", [f"把 {title} 當成不分條件永遠可直接套用的口訣。"]))


def build_law(meta: dict[str, object]) -> str:
    title = str(meta.get("title", ""))
    domain = str(meta.get("domain", ""))
    summary = str(meta.get("summary", ""))
    applicability = str(meta.get("applicability", "需搭配具體模型、近似與邊界條件判斷。"))
    prerequisites = [str(x) for x in meta.get("prerequisites", [])]
    concepts = [str(x) for x in meta.get("related_concepts", [])]
    quantities = [str(x) for x in meta.get("related_quantities", [])]
    laws = [str(x) for x in meta.get("related_laws", [])]
    experiments = [str(x) for x in meta.get("experiments", [])]
    tools = [str(x) for x in meta.get("math_tools", [])]
    derived = [str(x) for x in meta.get("derived_results", [])]
    modern = [str(x) for x in meta.get("modern_connections", [])]
    history = str(law_override(title, "history") or f"{title} 的重要性，在於它把 {domain} 中某類反覆出現的現象抽象成穩定可重用的關係。它通常來自長期實驗累積、幾何直覺整理，或更基礎理論的極限形式。")
    verification = str(law_override(title, "verification") or f"{serial_links(experiments, '可由代表性教學實驗、觀測資料或高精度量測間接支持')} 提供了和 {title} 對照的檢驗方式。")
    derived_fallback = f"後續常見延伸可沿著 {serial_links(laws, '相關定律')} 與應用模型展開。"
    applications = list(law_override(title, "applications") or [
        f"用 {title} 把 {serial_links(quantities, '關鍵物理量')} 聯立起來，建立可求解模型。",
        f"把 {title} 與 {serial_links(concepts, f'{domain}中的相關概念')} 一起使用，判斷問題中真正受限制的是哪些量。"
    ])
    problem_frames = list(law_override(title, "problem_frames") or [])
    boundary = list(law_override(title, "boundary") or [])
    step_by_step = LAW_STEP_BY_STEP_OVERRIDES.get(title, [])
    body = (
        f"# {title}\n\n"
        f"## 定律摘要\n{summary}\n\n"
        f"## 適用條件\n{applicability}\n\n"
        f"## 數學表述\n{render_bullets(law_math(title))}\n\n"
        f"## 物理直覺\n{law_intuition(title, domain)}\n\n"
        f"## 歷史背景\n{history}\n\n"
        f"## 實驗驗證\n{verification}\n\n"
        f"## 推導\n{render_numbered(law_derivation(title, prerequisites, quantities))}\n\n"
    )
    if step_by_step:
        body += f"## 逐步數學推導\n{render_numbered(step_by_step)}\n\n"
    body += f"## 典型應用\n{render_bullets(applications)}\n\n"
    if problem_frames:
        body += f"## 解題框架\n{render_numbered(problem_frames)}\n\n"
    if boundary:
        body += f"## 使用邊界\n{render_bullets(boundary)}\n\n"
    body += (
        f"## 常見誤解\n{render_bullets(law_misconceptions(title))}\n\n"
        f"## 先備知識\n{bullet_links(prerequisites, f'可先回到 [[{domain}總覽]] 建立脈絡。')}\n\n"
        f"## 相關概念\n{bullet_links(concepts, f'可先從 [[{domain}總覽]] 追相關概念。')}\n\n"
        f"## 衍生結果\n{bullet_links(derived, derived_fallback)}\n\n"
        f"## 現代理論視角\n{serial_links(modern, '在更進階課程裡，這條定律通常會被放進更一般的理論框架中重新理解')}。\n"
    )
    return body


def build_quantity(meta: dict[str, object]) -> str:
    title = str(meta.get("title", ""))
    domain = str(meta.get("domain", ""))
    summary = str(meta.get("summary", ""))
    symbol = str(meta.get("symbol", ""))
    unit = str(meta.get("unit", ""))
    dimension = str(meta.get("dimension", ""))
    concepts = [str(x) for x in meta.get("related_concepts", [])]
    laws = [str(x) for x in meta.get("related_laws", [])]
    methods = [str(x) for x in meta.get("measurement_methods", [])]
    data = QUANTITY_DATA.get(title, {})
    definition = str(data.get("definition", f"{title} 是 {domain} 中需要穩定追蹤的核心物理量之一。"))
    meaning = str(data.get("meaning", f"{title} 衡量的是系統狀態裡某個能跨情境比較的結構化量。"))
    apps = [
        f"在 {serial_links(laws, '相關定律與方程')} 中作為未知量或可觀測量出現。",
        f"與 {serial_links(concepts, '鄰近概念')} 一起決定系統該用哪一種分析框架。"
    ]
    misconceptions = [
        f"只記符號與單位，卻不理解 {title} 在模型裡到底扮演什麼角色。",
        f"沒有分清 {title} 的定義量與量測值之間的差別。"
    ]
    return (
        f"# {title}\n\n"
        f"## 物理量摘要\n{summary}\n\n"
        f"## 定義\n{definition}\n\n"
        f"## 符號與單位\n- 符號: ${symbol}$\n- SI 單位: {unit}\n\n"
        f"## 維度與量綱\n${dimension}$\n\n"
        f"## 幾何或物理意義\n{meaning}\n\n"
        f"## 量測方式\n{serial_links(methods, '可透過間接推算、感測器量測或實驗校正常數得到')}。\n\n"
        f"## 出現於哪些定律\n{bullet_links(laws, '可沿著相關定律頁面回看它如何進入方程。')}\n\n"
        f"## 典型應用\n{render_bullets(apps)}\n\n"
        f"## 常見誤解\n{render_bullets(misconceptions)}\n\n"
        f"## 相關概念\n{bullet_links(concepts, f'可由 [[{domain}總覽]] 往外串連。')}\n"
    )


def build_experiment(meta: dict[str, object]) -> str:
    title = str(meta.get("title", ""))
    domain = str(meta.get("domain", ""))
    summary = str(meta.get("summary", ""))
    laws = [str(x) for x in meta.get("tested_laws", [])]
    quantities = [str(x) for x in meta.get("measured_quantities", [])]
    concepts = [str(x) for x in meta.get("related_concepts", [])]
    historical_period = str(meta.get("historical_period", ""))
    data = EXPERIMENT_DATA.get(title, {})
    observables = list(data.get("observables", pick(quantities, ["位置", "時間", "力學量或電學訊號"])))
    results = str(data.get("results", f"{title} 的理想結果應能讓 {serial_links(laws, '相關定律或模型')} 的主要預測被直接看見或定量比較。"))
    impact = str(data.get("impact", f"這個實驗在 {domain} 的價值，在於把抽象理論轉成可重複操作的觀測流程。"))
    method = [
        "先控制主要自變因與環境條件，使理論假設盡量成立。",
        f"再量測 {', '.join(observables)}，並把資料轉成能和 {serial_links(laws, '理論關係')} 比較的形式。",
        "最後估計不確定度，判斷偏差來自儀器、環境還是模型本身。"
    ]
    return (
        f"# {title}\n\n"
        f"## 實驗摘要\n{summary}\n\n"
        f"## 問題背景\n{title} 的核心任務，是把 {domain} 中看似抽象的理論主張，轉成具體可操作的觀測設計。\n\n"
        f"## 裝置與方法\n{render_numbered(method)}\n\n"
        f"## 可觀測量\n{render_bullets(observables)}\n\n"
        f"## 實驗結果\n{results}\n\n"
        f"## 支持或挑戰的定律\n{bullet_links(laws, f'主要是對 {domain} 中的核心模型做檢驗。')}\n\n"
        f"## 誤差與限制\n- 儀器解析度、校正方式與背景干擾都會影響結果。\n- 模型常有近似條件，若樣品、流場、光路或電路偏離理想化，資料解讀就要更小心。\n\n"
        f"## 歷史影響\n{impact} 它也反映了 {historical_period or '不同時代'} 物理學如何透過量測把理論與世界真正接起來。\n\n"
        f"## 相關概念\n{bullet_links(concepts, f'可回到 [[{domain}總覽]] 沿著概念鏈閱讀。')}\n"
    )


def build_tool(meta: dict[str, object]) -> str:
    title = str(meta.get("title", ""))
    summary = str(meta.get("summary", ""))
    used_in = [str(x) for x in meta.get("used_in", [])]
    prerequisites = [str(x) for x in meta.get("prerequisites", [])]
    concepts = [str(x) for x in meta.get("related_concepts", [])]
    data = TOOL_DATA.get(title, {})
    definition = str(data.get("definition", f"{title} 是把物理關係形式化時常用的數學工具。"))
    operations = list(data.get("operations", [
        f"在 {serial_links(used_in, '相關主題')} 中把文字敘述翻成可計算關係。",
        "把局部變化、方向資訊或累積效果整理成更穩定的數學形式。"
    ]))
    return (
        f"# {title}\n\n"
        f"## 工具摘要\n{summary}\n\n"
        f"## 數學定義\n{definition}\n\n"
        f"## 幾何意義\n{title} 的幾何意義，通常來自它如何把大小、方向、變化率、面積、體積或相位結構轉成可操作的數學對象。\n\n"
        f"## 為什麼物理需要它\n沒有 {title}，很多物理定律只剩口頭描述，無法穩定處理不同座標、不同近似與不同邊界條件。\n\n"
        f"## 在哪些主題中出現\n{bullet_links(used_in, '可沿著相關定律與概念頁反查它的使用位置。')}\n\n"
        f"## 典型操作\n{render_bullets(operations)}\n\n"
        f"## 常見誤解\n- 只背計算規則，不知道每一步在物理上代表什麼。\n- 忘記工具本身有使用前提，例如座標選擇、可微性、線性近似或向量方向約定。\n\n"
        f"## 相關工具\n{bullet_links(prerequisites + concepts, '可與其他數學工具頁一起交叉閱讀。')}\n"
    )


def group_by_link_kind(items: list[str]) -> tuple[list[str], list[str]]:
    laws: list[str] = []
    concepts: list[str] = []
    for item in items:
        if any(token in item for token in ["定律", "定理", "方程", "公式", "守恆", "原理"]):
            laws.append(item)
        else:
            concepts.append(item)
    return laws, concepts


def build_map(meta: dict[str, object]) -> str:
    title = str(meta.get("title", ""))
    summary = str(meta.get("summary", ""))
    domain = str(meta.get("focus_domain", ""))
    includes = [str(x) for x in meta.get("includes", [])]
    order = [str(x) for x in meta.get("recommended_order", [])]
    laws, concepts = group_by_link_kind(includes)
    major_topics = [
        f"先用 {serial_links(order, '建議起點頁面')} 建立主線，再回到其他頁面補齊支線。",
        f"{domain} 的知識網通常由 {serial_links(laws, '核心定律')} 與 {serial_links(concepts, '關鍵概念')} 交織而成。"
    ]
    prereq = ["向量", "導數", "積分"] if domain in {"力學", "電磁學", "振動與波動", "光學"} else ["導數", "積分"]
    return (
        f"# {title}\n\n"
        f"## 地圖摘要\n{summary}\n\n"
        f"## 範圍說明\n這張地圖負責把 {domain} 的主要主線、前後依賴與延伸方向收在同一頁，幫你在深入單篇筆記前先抓到整體脈絡。\n\n"
        f"## 主要主題\n{render_bullets(major_topics)}\n\n"
        f"## 建議學習順序\n{bullet_links(order, f'可先從 [[{domain}總覽]] 內最基礎的定義頁開始。')}\n\n"
        f"## 關鍵定律\n{bullet_links(laws, '可先從該領域最常用的關係式開始。')}\n\n"
        f"## 關鍵概念\n{bullet_links(concepts, '可先從核心概念頁建立語言。')}\n\n"
        f"## 先備知識\n{bullet_links(prereq, '視頁面內容補向量、微積分或熱學基礎。')}\n\n"
        f"## 延伸方向\n- 把本頁當成導航，而不是全文教材。\n- 若已熟悉主線，可沿著未讀的實驗頁、數學工具頁與進階概念頁補強理解。\n"
    )


def build_body(meta: dict[str, object]) -> str:
    note_type = str(meta.get("type", ""))
    if note_type == "law":
        return build_law(meta)
    if note_type == "quantity":
        return build_quantity(meta)
    if note_type == "experiment":
        return build_experiment(meta)
    if note_type == "mathematical_tool":
        return build_tool(meta)
    if note_type == "map":
        return build_map(meta)
    raise ValueError(f"Unsupported note type: {note_type}")


def enrich_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    raw_frontmatter, meta = parse_frontmatter(text)
    note_type = str(meta.get("type", ""))
    if note_type not in {"law", "quantity", "experiment", "mathematical_tool", "map"}:
        return False
    new_text = f"---\n{raw_frontmatter}\n---\n\n{build_body(meta)}"
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Expand non-concept pages in the physics knowledge vault.")
    parser.add_argument("--vault", required=True, help="Vault root path")
    args = parser.parse_args()

    vault = Path(args.vault).resolve()
    folders = ["00_maps", "01_laws", "03_quantities", "04_experiments", "05_mathematical_tools"]
    changed = 0
    total = 0
    for folder in folders:
        for file_path in sorted((vault / folder).glob("*.md")):
            total += 1
            if enrich_file(file_path):
                changed += 1
    print(f"Processed {total} non-concept pages; updated {changed}.")


if __name__ == "__main__":
    main()
