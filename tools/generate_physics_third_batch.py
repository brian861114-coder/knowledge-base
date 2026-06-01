#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def wl(items: list[str]) -> list[str]:
    return [f"[[{item}]]" for item in items]


def yaml_list(items: list[str]) -> str:
    if not items:
        return "[]"
    return "[" + ", ".join(f'"{item}"' for item in wl(items)) + "]"


def build_concept(page: dict) -> str:
    title = page["title"]
    summary = page["summary"]
    domain = page["domain"]
    prerequisites = page.get("prerequisites", [])
    laws = page.get("related_laws", [])
    quantities = page.get("related_quantities", [])
    related = page.get("related_concepts", [])
    tools = page.get("math_tools", [])
    examples = page.get("examples", [])
    misconception = page.get("misconception", f"容易把「{title}」只當成名詞記憶，而忽略它在解題時的判準與限制。")
    modern = page.get("modern", f"在更進一步的 {domain} 內容中，{title} 會和更抽象的模型與更精細的近似一起出現。")
    laws_text = "\n".join(f"- [[{name}]]" for name in laws) if laws else f"- [[{domain}總覽]]"
    examples_text = "\n".join(f"- {item}" for item in examples) if examples else f"- 在 {domain} 問題中辨識 {title} 如何影響現象與推理。"
    prereq_text = "\n".join(f"- [[{name}]]" for name in prerequisites) if prerequisites else "- 先讀相關總覽頁即可建立基本位置感。"
    related_text = "\n".join(f"- [[{name}]]" for name in related) if related else f"- [[{domain}總覽]]"
    return f"""---
type: concept
title: {title}
domain: {domain}
summary: {summary}
prerequisites: {yaml_list(prerequisites)}
related_laws: {yaml_list(laws)}
related_quantities: {yaml_list(quantities)}
related_concepts: {yaml_list(related)}
math_tools: {yaml_list(tools)}
tags: [physics, {page.get("tag", domain)}]
updated: 2026-05-31
---

# {title}

## 概念摘要
{summary}

## 基本定義
{page.get("definition", f"{title} 是 {domain} 中反覆出現的核心概念，用來組織觀察、建模與解題。")}

## 物理意義
{page.get("meaning", f"理解 {title} 可以幫助我們判斷系統中哪些量重要、哪些變化值得追蹤，以及不同章節之間如何互相連結。")}

## 直觀理解
{page.get("intuition", f"學習 {title} 時，最有用的方式通常不是背誦一句話，而是把它放回典型情境中，看它如何限制運動、能量或場的分布。")}

## 歷史背景
{page.get("history", f"{title} 的成熟來自經典物理長期累積的實驗與理論整理，後來也成為更進階理論的基礎語言。")}

## 代表性定律
{laws_text}

## 典型例子
{examples_text}

## 常見誤解
- {misconception}

## 先備知識
{prereq_text}

## 相關概念
{related_text}

## 現代理論視角
{modern}
"""


def build_law(page: dict) -> str:
    title = page["title"]
    summary = page["summary"]
    domain = page["domain"]
    prerequisites = page.get("prerequisites", [])
    related_concepts = page.get("related_concepts", [])
    related_quantities = page.get("related_quantities", [])
    related_laws = page.get("related_laws", [])
    experiments = page.get("experiments", [])
    math_tools = page.get("math_tools", [])
    derived = page.get("derived_results", [])
    modern_connections = page.get("modern_connections", [])
    prereq_text = "\n".join(f"- [[{name}]]" for name in prerequisites) if prerequisites else "- 先讀本領域總覽頁與基礎概念頁。"
    related_text = "\n".join(f"- [[{name}]]" for name in related_concepts) if related_concepts else f"- [[{domain}總覽]]"
    derived_text = "\n".join(f"- [[{name}]]" for name in derived) if derived else f"- 用來串接更進一步的 {domain} 模型。"
    return f"""---
type: law
title: {title}
domain: {domain}
summary: {summary}
applicability: {page.get("applicability", f"適用於典型的 {domain} 問題；真正使用前仍要先檢查近似條件與系統邊界。")}
prerequisites: {yaml_list(prerequisites)}
related_concepts: {yaml_list(related_concepts)}
related_quantities: {yaml_list(related_quantities)}
related_laws: {yaml_list(related_laws)}
experiments: {yaml_list(experiments)}
math_tools: {yaml_list(math_tools)}
derived_results: {yaml_list(derived)}
modern_connections: {yaml_list(modern_connections)}
tags: [physics, {page.get("tag", domain)}, law]
updated: 2026-05-31
---

# {title}

## 定律摘要
{summary}

## 適用條件
{page.get("conditions", f"使用 {title} 時，必須先確認題目所處的尺度、對稱性、近似條件與相互作用模型都在它的有效範圍內。")}

## 數學表述
{page.get("math", f"{title} 常以定性敘述和方程形式並用；在解題時要把文字條件翻成可運算的數學關係。")}

## 物理直覺
{page.get("intuition", f"{title} 的價值不只在公式，而在於它指出哪些量會彼此耦合、哪些變化可以直接由整體約束得到。")}

## 歷史背景
{page.get("history", f"{title} 是 {domain} 發展過程中的關鍵整理，使原本零散的現象能放進同一個推理框架。")}

## 實驗驗證
{page.get("verification", f"{title} 可以透過典型教學實驗、精密量測或與理論預測的系統比對來建立可信度。")}

## 推導
{page.get("derivation", f"實際推導 {title} 時，通常會結合幾何、守恆觀點、微積分或對稱性分析。")}

## 典型應用
{page.get("applications", f"- 在 {domain} 題目中建立主要方程\n- 用來估算量級、方向或穩定條件\n- 作為更進一步理論的起點")}

## 常見誤解
- {page.get("misconception", f"最常見的錯誤是把 {title} 當成任何情況都可直接套用的萬用公式，而沒有先檢查適用條件。")}

## 先備知識
{prereq_text}

## 相關概念
{related_text}

## 衍生結果
{derived_text}

## 現代理論視角
{page.get("modern", f"在更現代的理論框架中，{title} 往往可以被看成更一般結構的低能近似、特殊情況或對稱性結果。")}
"""


def build_quantity(page: dict) -> str:
    title = page["title"]
    summary = page["summary"]
    domain = page["domain"]
    related_concepts = page.get("related_concepts", [])
    related_laws = page.get("related_laws", [])
    methods = page.get("measurement_methods", [])
    related_text = "\n".join(f"- [[{name}]]" for name in related_concepts) if related_concepts else f"- [[{domain}總覽]]"
    return f"""---
type: quantity
title: {title}
symbol: {page.get("symbol", "")}
unit: {page.get("unit", "")}
dimension: {page.get("dimension", "")}
domain: {domain}
summary: {summary}
related_concepts: {yaml_list(related_concepts)}
related_laws: {yaml_list(related_laws)}
measurement_methods: {yaml_list(methods)}
tags: [physics, {page.get("tag", domain)}, quantity]
updated: 2026-05-31
---

# {title}

## 物理量摘要
{summary}

## 定義
{page.get("definition", f"{title} 是 {domain} 中常用來描述系統狀態、變化趨勢或交互作用強度的物理量。")}

## 符號與單位
- 符號：{page.get("symbol", "依情境而定")}
- SI 單位：{page.get("unit", "視定義而定")}

## 維度與量綱
{page.get("dimension", "需配合具體定義與方程關係理解。")}

## 幾何或物理意義
{page.get("meaning", f"理解 {title} 的關鍵，是知道它如何把現象中的『多少』轉成可比較、可代入方程的量。")}

## 量測方式
{page.get("measurement", f"{title} 通常可藉由直接量測、間接推算，或透過相關儀器把其他可測量量轉換得到。")}

## 出現於哪些定律
{page.get("laws_text", ''.join(f'- [[{name}]]\\n' for name in related_laws).rstrip() or f'- [[{domain}總覽]]')}

## 典型應用
{page.get("applications", f"- 建立 {domain} 題目的狀態描述\n- 與其他物理量形成可計算的定律或守恆式")}

## 常見誤解
- {page.get("misconception", f"容易只記住 {title} 的單位，卻忽略它在圖像、方程與實驗中的實際意義。")}

## 相關概念
{related_text}
"""


def build_math(page: dict) -> str:
    title = page["title"]
    summary = page["summary"]
    used_in = page.get("used_in", [])
    prerequisites = page.get("prerequisites", [])
    related = page.get("related_concepts", [])
    used_text = "\n".join(f"- [[{name}]]" for name in used_in) if used_in else "- 在多個物理章節中反覆出現。"
    related_text = "\n".join(f"- [[{name}]]" for name in related) if related else "- 與其他數學工具搭配使用。"
    return f"""---
type: mathematical_tool
title: {title}
summary: {summary}
used_in: {yaml_list(used_in)}
prerequisites: {yaml_list(prerequisites)}
related_concepts: {yaml_list(related)}
tags: [physics, mathematics]
updated: 2026-05-31
---

# {title}

## 工具摘要
{summary}

## 數學定義
{page.get("definition", f"{title} 是把物理問題轉成可計算形式的重要工具，能把關係、變化或結構表達得更清楚。")}

## 幾何意義
{page.get("geometric", f"學 {title} 時，除了符號操作，也要理解它在幾何圖像、方向關係或空間變化上的意義。")}

## 為什麼物理需要它
{page.get("why", f"許多物理概念只有放進 {title} 的語言後，才容易看出哪些量守恆、哪些方向重要、哪些近似可行。")}

## 在哪些主題中出現
{used_text}

## 典型操作
{page.get("operations", f"- 先辨認已知量與未知量之間的結構\n- 再用 {title} 把它們寫成更適合運算或推理的形式")}

## 常見誤解
- {page.get("misconception", f"只背誦 {title} 的公式形式，而沒有把它和物理情境綁在一起。")}

## 相關工具
{related_text}
"""


def build_experiment(page: dict) -> str:
    title = page["title"]
    summary = page["summary"]
    domain = page["domain"]
    tested_laws = page.get("tested_laws", [])
    measured = page.get("measured_quantities", [])
    related = page.get("related_concepts", [])
    related_text = "\n".join(f"- [[{name}]]" for name in related) if related else f"- 與 {domain} 的核心概念一起理解。"
    return f"""---
type: experiment
title: {title}
summary: {summary}
domain: {domain}
tested_laws: {yaml_list(tested_laws)}
measured_quantities: {yaml_list(measured)}
related_concepts: {yaml_list(related)}
historical_period: {page.get("historical_period", "classical")}
tags: [physics, experiment, {page.get("tag", domain)}]
updated: 2026-05-31
---

# {title}

## 實驗摘要
{summary}

## 問題背景
{page.get("background", f"{title} 用來把抽象的 {domain} 定律或量測需求，轉成可操作、可比較的實驗流程。")}

## 裝置與方法
{page.get("setup", f"實際裝置會依教學或研究目的調整，但核心都在於控制主要變因、量測關鍵訊號，並排除明顯系統誤差。")}

## 可觀測量
{page.get("observables", f"{title} 通常會量到位置、時間、電訊號、光強、力學量或其他能反映理論預測的可觀測量。")}

## 實驗結果
{page.get("results", f"理想情況下，{title} 的結果應與對應定律或模型的主要預測一致，並能提供量值估計或現象辨識。")}

## 支持或挑戰的定律
{page.get("supported", ''.join(f'- [[{name}]]\\n' for name in tested_laws).rstrip() or f'- [[{domain}總覽]]')}

## 誤差與限制
{page.get("errors", f"{title} 的判讀常受儀器靈敏度、校正方式、環境干擾與理論近似影響。")}

## 歷史影響
{page.get("history", f"{title} 在物理教育或學科發展中，都扮演了把理論落地成可檢驗結果的重要角色。")}

## 相關概念
{related_text}
"""


def build_page(page: dict) -> str:
    builders = {
        "concept": build_concept,
        "law": build_law,
        "quantity": build_quantity,
        "mathematical_tool": build_math,
        "experiment": build_experiment,
    }
    return builders[page["type"]](page).strip() + "\n"


PAGES = [
    {"title": "功", "type": "concept", "domain": "力學", "summary": "功描述力沿位移方向轉移能量的效果，是把受力分析和能量觀點接起來的橋梁。", "prerequisites": ["力", "位移"], "related_laws": ["功能定理"], "related_concepts": ["動能", "能量"], "math_tools": ["內積"]},
    {"title": "簡諧運動", "type": "concept", "domain": "振動與波動", "summary": "簡諧運動是回復力與位移成正比且方向相反時出現的理想週期運動。", "prerequisites": ["位移", "導數", "三角函數"], "related_laws": ["虎克定律"], "related_concepts": ["共振", "駐波", "圓周運動"], "math_tools": ["導數", "三角函數"]},
    {"title": "壓力", "type": "quantity", "domain": "流體力學", "summary": "壓力表示單位面積上承受的正向作用力，是流體靜力學與熱學中的基本物理量。", "symbol": "p", "unit": "Pa", "dimension": "M L^-1 T^-2", "related_concepts": ["密度", "流量"], "related_laws": ["連續方程", "阿基米德原理"], "measurement_methods": ["文氏管", "天平"]},
    {"title": "慣性", "type": "concept", "domain": "力學", "summary": "慣性描述物體維持原本運動狀態的傾向，是理解牛頓第一定律的核心。", "prerequisites": ["牛頓第一定律"], "related_laws": ["牛頓第一定律"], "related_concepts": ["慣性參考系", "質量"]},
    {"title": "位能", "type": "concept", "domain": "力學", "summary": "位能是由位置或構型決定的能量描述，讓保守力問題能用能量差來處理。", "prerequisites": ["保守力", "功"], "related_laws": ["機械能守恆"], "related_concepts": ["動能", "勢能井", "穩定平衡"], "math_tools": ["積分"]},
    {"title": "內能", "type": "concept", "domain": "熱學與熱力學", "summary": "內能是系統微觀自由度所攜帶的總能量，是熱力學第一定律中的中心量。", "prerequisites": ["熱", "能量"], "related_laws": ["熱力學第一定律"], "related_concepts": ["熵", "理想氣體方程式"]},
    {"title": "密度", "type": "quantity", "domain": "流體力學", "summary": "密度表示單位體積所含的質量，是浮力、壓力與流動分析的重要起點。", "symbol": "ρ", "unit": "kg/m^3", "dimension": "M L^-3", "related_concepts": ["壓力", "阿基米德原理"], "related_laws": ["連續方程"], "measurement_methods": ["天平"]},
    {"title": "狹義相對論", "type": "concept", "domain": "近代物理", "summary": "狹義相對論重寫了高速運動下的時間、空間與動量能量關係。", "prerequisites": ["光電效應"], "related_laws": ["質能等價"], "related_concepts": ["質能等價", "對稱性"]},
    {"title": "面積分", "type": "mathematical_tool", "domain": "數學工具", "summary": "面積分把向量場或純量場在曲面上的累積效果寫成可計算形式。", "used_in": ["高斯定律", "電通量", "壓力"], "prerequisites": ["積分", "向量"], "related_concepts": ["電通量", "壓力"]},
    {"title": "動能", "type": "concept", "domain": "力學", "summary": "動能衡量物體因運動而具有的能量，直接連到速度大小與受力做功。", "prerequisites": ["速度", "功"], "related_laws": ["功能定理", "機械能守恆"], "related_concepts": ["位能", "能量"]},
    {"title": "熱力學第零定律", "type": "law", "domain": "熱學與熱力學", "summary": "若兩個系統各自都與第三個系統熱平衡，則彼此也熱平衡，這使溫度成為可定義量。", "prerequisites": ["溫度"], "related_concepts": ["熱", "內能"], "related_laws": ["熱力學第一定律"], "derived_results": ["溫度"]},
    {"title": "保守力", "type": "concept", "domain": "力學", "summary": "保守力的做功只與初末位置有關，因此可用位能函數來描述。", "prerequisites": ["功", "位移"], "related_laws": ["機械能守恆"], "related_concepts": ["位能", "穩定平衡"], "math_tools": ["積分"]},
    {"title": "機率與統計", "type": "mathematical_tool", "domain": "數學工具", "summary": "機率與統計提供處理大量微觀自由度、誤差分布與平均行為的語言。", "used_in": ["熱力學第零定律", "熱力學第二定律", "統計物理"], "prerequisites": [], "related_concepts": ["熵", "統計物理"]},
    {"title": "熱", "type": "concept", "domain": "熱學與熱力學", "summary": "熱是由溫差驅動的能量傳遞，而不是系統內部儲存的一種物質。", "prerequisites": ["溫度"], "related_laws": ["熱力學第一定律"], "related_concepts": ["內能", "熵"]},
    {"title": "熵", "type": "concept", "domain": "熱學與熱力學", "summary": "熵衡量系統可達微觀狀態的豐富程度，也是描述不可逆性的核心量。", "prerequisites": ["熱", "內能"], "related_laws": ["熱力學第二定律"], "related_concepts": ["統計物理", "卡諾循環"]},
    {"title": "慣性參考系", "type": "concept", "domain": "力學", "summary": "慣性參考系是牛頓定律以最簡單形式成立的參考架構。", "prerequisites": ["慣性", "牛頓第一定律"], "related_laws": ["牛頓第一定律", "牛頓第二定律"], "related_concepts": ["狹義相對論"]},
    {"title": "萬有引力定律", "type": "law", "domain": "力學", "summary": "萬有引力定律描述任意兩個質量之間彼此吸引，且力的大小與距離平方成反比。", "prerequisites": ["質量", "力", "位移"], "related_concepts": ["圓周運動", "位能"], "related_quantities": ["質量"], "related_laws": ["牛頓第二定律"], "math_tools": ["向量"], "derived_results": ["牛頓萬有引力定律"]},
    {"title": "角動量", "type": "concept", "domain": "力學", "summary": "角動量描述系統相對某一基準點的轉動狀態，是旋轉運動中的守恆量。", "prerequisites": ["動量", "轉矩"], "related_laws": ["動量守恆"], "related_concepts": ["圓周運動", "質心"], "math_tools": ["外積"]},
    {"title": "質心", "type": "concept", "domain": "力學", "summary": "質心是把多體系統整體平移運動濃縮成一個等效位置的工具。", "prerequisites": ["質量", "位移"], "related_laws": ["動量守恆"], "related_concepts": ["碰撞分析"]},
    {"title": "連續方程", "type": "law", "domain": "流體力學", "summary": "連續方程表達質量守恆在流體中的形式，指出穩定流動中流量如何沿管線分配。", "prerequisites": ["密度", "流量"], "related_concepts": ["壓力", "文氏管"], "related_quantities": ["流量", "密度"], "related_laws": ["伯努力方程"], "derived_results": ["文氏管"]},
    {"title": "麥克斯威方程組", "type": "law", "domain": "電磁學", "summary": "麥克斯威方程組把電場、磁場、電荷與電流的關係整合成現代電磁學的核心結構。", "prerequisites": ["高斯定律", "法拉第定律", "磁場"], "related_concepts": ["電磁波", "交流電"], "related_laws": ["高斯定律", "法拉第定律"], "math_tools": ["散度", "旋度"], "modern_connections": ["狹義相對論"]},
    {"title": "位移", "type": "concept", "domain": "力學", "summary": "位移描述物體位置的改變量，關心的是初末狀態之間的向量差，而不是走過的路長。", "prerequisites": ["向量"], "related_laws": ["牛頓第一定律", "功能定理"], "related_concepts": ["速度", "功"]},
    {"title": "時間", "type": "concept", "domain": "力學", "summary": "時間是描述事件先後與變化過程的基本參數，幾乎所有運動與演化問題都要依賴它。", "prerequisites": [], "related_laws": ["牛頓第一定律", "動量定理"], "related_concepts": ["位移", "速度", "簡諧運動"]},
    {"title": "光線模型", "type": "concept", "domain": "光學", "summary": "光線模型用幾何方式近似光的傳播，適合處理反射、折射與成像問題。", "prerequisites": ["反射定律", "折射定律"], "related_laws": ["薄透鏡公式"], "related_concepts": ["全反射", "顯微鏡"]},
    {"title": "光電效應", "type": "concept", "domain": "近代物理", "summary": "光電效應顯示光的能量以量子化方式與物質交換，是量子論的重要起點。", "prerequisites": ["電位"], "related_laws": ["質能等價"], "related_concepts": ["黑體輻射", "德布羅意波"]},
    {"title": "全反射", "type": "concept", "domain": "光學", "summary": "當光從高折射率介質射向低折射率介質且入射角大於臨界角時，會發生全反射。", "prerequisites": ["折射定律"], "related_laws": ["反射定律"], "related_concepts": ["光線模型", "顯微鏡"]},
    {"title": "動量定理", "type": "law", "domain": "力學", "summary": "動量定理指出合外力對時間的累積效果等於動量的改變。", "prerequisites": ["動量", "衝量"], "related_concepts": ["碰撞分析"], "related_quantities": ["動量"], "related_laws": ["牛頓第二定律"], "math_tools": ["積分"], "derived_results": ["衝量"]},
    {"title": "勢能井", "type": "concept", "domain": "力學", "summary": "勢能井用圖像化方式描述粒子被局限在某個位形附近的狀態。", "prerequisites": ["位能", "穩定平衡"], "related_laws": ["機械能守恆"], "related_concepts": ["簡諧運動"]},
    {"title": "均勻帶電球殼電場", "type": "concept", "domain": "電磁學", "summary": "均勻帶電球殼的內外電場分布是高斯定律在球對稱系統中的經典例子。", "prerequisites": ["高斯定律", "電場"], "related_laws": ["高斯定律"], "related_concepts": ["無限平面電場"]},
    {"title": "散度", "type": "mathematical_tool", "domain": "數學工具", "summary": "散度衡量向量場在局部看起來像源還是匯，是場論語言中的重要運算。", "used_in": ["高斯定律", "麥克斯威方程組"], "prerequisites": ["偏導數", "向量"], "related_concepts": ["電場", "電力線"]},
    {"title": "文氏管", "type": "concept", "domain": "流體力學", "summary": "文氏管利用截面改變引起的流速與壓力差，常用來量測流量。", "prerequisites": ["流量", "壓力"], "related_laws": ["連續方程", "伯努力方程"], "related_concepts": ["流量"]},
    {"title": "旋度", "type": "mathematical_tool", "domain": "數學工具", "summary": "旋度衡量向量場在局部的環流傾向，是理解磁場與感應現象的重要工具。", "used_in": ["法拉第定律", "麥克斯威方程組"], "prerequisites": ["偏導數", "向量"], "related_concepts": ["磁場", "電磁波"]},
    {"title": "法拉第定律", "type": "law", "domain": "電磁學", "summary": "法拉第定律指出磁通量隨時間改變會感生電動勢。", "prerequisites": ["磁場", "面積分"], "related_concepts": ["電磁波", "交流電"], "related_laws": ["麥克斯威方程組"], "math_tools": ["面積分", "旋度"], "derived_results": ["交流電"]},
    {"title": "流量", "type": "quantity", "domain": "流體力學", "summary": "流量表示流體在單位時間內穿過某個截面的體積或質量。", "symbol": "Q", "unit": "m^3/s", "dimension": "L^3 T^-1", "related_concepts": ["壓力", "文氏管"], "related_laws": ["連續方程", "伯努力方程"], "measurement_methods": ["文氏管"]},
    {"title": "無限平面電場", "type": "concept", "domain": "電磁學", "summary": "無限平面電場是高斯定律在平面對稱下的標準範例，常用來近似平行板系統。", "prerequisites": ["高斯定律", "電場"], "related_laws": ["高斯定律"], "related_concepts": ["平行板電容器", "等位面"]},
    {"title": "熱傳導", "type": "concept", "domain": "熱學與熱力學", "summary": "熱傳導描述熱量因溫度梯度而在物質內部傳遞的過程。", "prerequisites": ["熱", "溫度"], "related_laws": ["熱力學第二定律"], "related_concepts": ["等溫過程", "絕熱過程"], "math_tools": ["梯度"]},
    {"title": "熱力學第二定律", "type": "law", "domain": "熱學與熱力學", "summary": "熱力學第二定律指出自然過程存在方向性，孤立系統的熵不會自發減少。", "prerequisites": ["熱", "熵"], "related_concepts": ["卡諾循環", "統計物理"], "related_laws": ["熱力學第一定律"], "derived_results": ["等溫過程", "絕熱過程"]},
    {"title": "牛頓萬有引力定律", "type": "law", "domain": "力學", "summary": "牛頓萬有引力定律是萬有引力在經典力學語境中的標準表述。", "prerequisites": ["萬有引力定律", "質量"], "related_concepts": ["圓周運動", "位能"], "related_quantities": ["質量"], "related_laws": ["萬有引力定律"], "derived_results": ["火箭方程"]},
    {"title": "相互作用", "type": "concept", "domain": "力學", "summary": "相互作用強調物理系統中的效應來自對象彼此之間的關係，而不是單方面施加。", "prerequisites": ["力"], "related_laws": ["牛頓第三定律"], "related_concepts": ["場論觀點", "磁力"]},
    {"title": "碰撞分析", "type": "concept", "domain": "力學", "summary": "碰撞分析透過動量、能量與接觸時間尺度來理解多體瞬時交互作用。", "prerequisites": ["動量", "衝量"], "related_laws": ["動量定理", "動量守恆"], "related_concepts": ["質心"]},
    {"title": "磁力", "type": "concept", "domain": "電磁學", "summary": "磁力描述帶電粒子或電流在磁場中受到的力，方向關係比大小公式更關鍵。", "prerequisites": ["磁場", "向量"], "related_laws": ["麥克斯威方程組"], "related_concepts": ["電磁波"], "math_tools": ["外積"]},
    {"title": "穩定平衡", "type": "concept", "domain": "力學", "summary": "穩定平衡指系統受小擾動後傾向回到原平衡位置的狀態。", "prerequisites": ["位能"], "related_laws": ["機械能守恆"], "related_concepts": ["勢能井", "簡諧運動"]},
    {"title": "等位面", "type": "concept", "domain": "電磁學", "summary": "等位面由電位相同的點組成，沿著表面移動電荷不需額外做功。", "prerequisites": ["電位"], "related_laws": ["高斯定律"], "related_concepts": ["電位能", "電力線"], "math_tools": ["梯度"]},
    {"title": "聲波", "type": "concept", "domain": "振動與波動", "summary": "聲波是介質中的機械縱波，反映壓力與密度擾動的傳播。", "prerequisites": ["機械波", "壓力"], "related_concepts": ["駐波", "都卜勒效應"]},
    {"title": "能量", "type": "concept", "domain": "力學", "summary": "能量是統整不同物理過程的一般量，讓變化、轉換與守恆能放在同一框架下分析。", "prerequisites": ["功"], "related_laws": ["功能定理", "機械能守恆", "熱力學第一定律"], "related_concepts": ["動能", "位能", "內能"]},
    {"title": "薄透鏡公式", "type": "law", "domain": "光學", "summary": "薄透鏡公式把物距、像距與焦距連成簡潔關係，是幾何光學成像分析的核心。", "prerequisites": ["光線模型", "折射定律"], "related_concepts": ["顯微鏡"], "related_laws": ["折射定律"]},
    {"title": "轉矩", "type": "concept", "domain": "力學", "summary": "轉矩衡量力使物體繞某點或某軸旋轉的能力。", "prerequisites": ["力", "位移"], "related_laws": ["牛頓第二定律"], "related_concepts": ["角動量", "圓周運動"], "math_tools": ["外積"]},
    {"title": "運動感測器", "type": "experiment", "domain": "力學", "summary": "運動感測器可連續量測位置、速度或加速度，是現代教學實驗中常見的量測工具。", "tested_laws": ["牛頓第一定律", "牛頓第二定律"], "measured_quantities": ["速度", "加速度"], "related_concepts": ["簡諧運動"]},
    {"title": "雙狹縫實驗", "type": "experiment", "domain": "光學", "summary": "雙狹縫實驗透過干涉條紋直接展示波動性，是波動光學與量子入門的關鍵實驗。", "tested_laws": ["折射定律"], "related_concepts": ["干涉", "惠更斯原理", "光電效應"]},
    {"title": "電位能", "type": "concept", "domain": "電磁學", "summary": "電位能描述電荷在電場中因位置不同而具有的能量。", "prerequisites": ["電位", "電荷"], "related_laws": ["庫侖定律"], "related_concepts": ["等位面", "電場能量"]},
    {"title": "電力線", "type": "concept", "domain": "電磁學", "summary": "電力線是幫助視覺化電場方向與強弱分布的圖像工具。", "prerequisites": ["電場"], "related_laws": ["高斯定律"], "related_concepts": ["等位面", "散度"]},
    {"title": "電磁波", "type": "concept", "domain": "電磁學", "summary": "電磁波是電場與磁場彼此耦合、自我維持並向外傳播的波動。", "prerequisites": ["麥克斯威方程組", "法拉第定律"], "related_laws": ["麥克斯威方程組"], "related_concepts": ["交流電", "偏振", "光線模型"]},
    {"title": "駐波", "type": "concept", "domain": "振動與波動", "summary": "駐波是兩列相反方向同頻率波疊加後形成的節點與腹點固定圖樣。", "prerequisites": ["簡諧運動", "聲波"], "related_concepts": ["干涉", "共振"]},
    {"title": "黑體輻射", "type": "concept", "domain": "近代物理", "summary": "黑體輻射問題揭示了經典理論的失效，促成量子論的誕生。", "prerequisites": ["熱", "電磁波"], "related_concepts": ["光電效應", "統計物理"]},
    {"title": "交流電", "type": "concept", "domain": "電磁學", "summary": "交流電是電流與電壓隨時間週期變化的電路描述。", "prerequisites": ["歐姆定律", "三角函數"], "related_laws": ["法拉第定律"], "related_concepts": ["電磁波", "共振"], "math_tools": ["複數"]},
    {"title": "低摩擦滑車實驗", "type": "experiment", "domain": "力學", "summary": "低摩擦滑車實驗用來近似無摩擦條件，方便觀察慣性與合力造成的加速度。", "tested_laws": ["牛頓第一定律", "牛頓第二定律"], "measured_quantities": ["速度", "加速度"], "related_concepts": ["慣性"]},
    {"title": "偏振", "type": "concept", "domain": "光學", "summary": "偏振描述橫波振動方向的選擇性，是區分波動模型細節的重要現象。", "prerequisites": ["電磁波"], "related_concepts": ["干涉", "顯微鏡"]},
    {"title": "兩滑車碰撞實驗", "type": "experiment", "domain": "力學", "summary": "兩滑車碰撞實驗常用來比較碰撞前後的動量與能量，建立碰撞分析直覺。", "tested_laws": ["動量守恆", "動量定理"], "measured_quantities": ["動量"], "related_concepts": ["碰撞分析"]},
    {"title": "卡諾循環", "type": "concept", "domain": "熱學與熱力學", "summary": "卡諾循環是理想可逆熱機模型，用來界定熱機效率的上限。", "prerequisites": ["熱力學第二定律"], "related_laws": ["熱力學第二定律"], "related_concepts": ["等溫過程", "絕熱過程", "熵"]},
    {"title": "反射定律", "type": "law", "domain": "光學", "summary": "反射定律指出入射角等於反射角，且入射線、反射線與法線共平面。", "prerequisites": ["光線模型"], "related_concepts": ["全反射"], "related_laws": ["折射定律"]},
    {"title": "圓周運動", "type": "concept", "domain": "力學", "summary": "圓周運動把速度方向持續改變的運動濃縮成徑向與切向分析。", "prerequisites": ["速度", "加速度"], "related_laws": ["牛頓第二定律", "萬有引力定律"], "related_concepts": ["轉矩", "角動量"]},
    {"title": "場論觀點", "type": "concept", "domain": "電磁學", "summary": "場論觀點把相互作用改寫成場在空間中的分布與演化，而不只看遠距離瞬時作用。", "prerequisites": ["電場", "磁場"], "related_laws": ["麥克斯威方程組"], "related_concepts": ["相互作用", "電磁波"]},
    {"title": "天平", "type": "experiment", "domain": "力學", "summary": "天平是最基本的質量量測工具，也常作為密度與材料性質估計的起點。", "tested_laws": ["牛頓第一定律"], "measured_quantities": ["質量"], "related_concepts": ["密度"]},
    {"title": "密立根油滴實驗", "type": "experiment", "domain": "電磁學", "summary": "密立根油滴實驗量測電子電荷量值，並展示電荷量子化。", "tested_laws": ["庫侖定律"], "measured_quantities": ["電荷"], "related_concepts": ["電位"]},
    {"title": "對稱性", "type": "concept", "domain": "近代物理", "summary": "對稱性幫助我們看出哪些量守恆、哪些方程形式自然成立，是現代理論的深層結構。", "prerequisites": ["向量"], "related_laws": ["質能等價"], "related_concepts": ["拉格朗日力學", "場論觀點"]},
    {"title": "小車軌道實驗", "type": "experiment", "domain": "力學", "summary": "小車軌道實驗可用來觀察位置、速度、加速度與能量之間的關係。", "tested_laws": ["功能定理", "牛頓第二定律"], "measured_quantities": ["速度", "加速度"], "related_concepts": ["位移"]},
    {"title": "干涉", "type": "concept", "domain": "振動與波動", "summary": "干涉是多列波重疊時振幅依相位關係增強或減弱的現象。", "prerequisites": ["聲波", "簡諧運動"], "related_concepts": ["駐波", "雙狹縫實驗"]},
    {"title": "平衡", "type": "concept", "domain": "力學", "summary": "平衡表示系統在整體受力或受力矩上達成互相抵消，因此狀態不再改變。", "prerequisites": ["力"], "related_laws": ["牛頓第一定律"], "related_concepts": ["穩定平衡"]},
    {"title": "德布羅意波", "type": "concept", "domain": "近代物理", "summary": "德布羅意波把粒子的動量與波長連結起來，將波粒二象性推廣到物質。", "prerequisites": ["光電效應"], "related_concepts": ["薛丁格方程", "黑體輻射"]},
    {"title": "惠更斯原理", "type": "concept", "domain": "光學", "summary": "惠更斯原理把波前演化想成每個點都發出次級波，是理解反射、折射與繞射的重要圖像。", "prerequisites": ["機械波"], "related_laws": ["反射定律", "折射定律"], "related_concepts": ["干涉", "雙狹縫實驗"]},
    {"title": "打點計時器", "type": "experiment", "domain": "力學", "summary": "打點計時器把運動轉成離散時間記錄，方便從點距估算速度與加速度。", "tested_laws": ["牛頓第二定律"], "measured_quantities": ["速度", "加速度"], "related_concepts": ["位移"]},
    {"title": "扭秤實驗", "type": "experiment", "domain": "力學", "summary": "扭秤實驗可用來量測極小作用力，是研究萬有引力與靜電力的重要工具。", "tested_laws": ["萬有引力定律"], "measured_quantities": ["質量"], "related_concepts": ["萬有引力定律"]},
    {"title": "拉格朗日力學", "type": "concept", "domain": "力學", "summary": "拉格朗日力學用能量差與變分原理改寫經典力學，特別適合多自由度系統。", "prerequisites": ["能量", "對稱性"], "related_concepts": ["場論觀點", "狹義相對論"]},
    {"title": "推進", "type": "concept", "domain": "力學", "summary": "推進研究系統如何藉由噴射、相互作用或外力交換動量來改變運動狀態。", "prerequisites": ["動量", "牛頓第三定律"], "related_laws": ["火箭方程"], "related_concepts": ["相互作用"]},
    {"title": "歐姆定律", "type": "law", "domain": "電磁學", "summary": "歐姆定律描述導體在一定條件下電壓、電流與電阻之間的比例關係。", "prerequisites": ["電位"], "related_concepts": ["交流電"], "related_laws": ["法拉第定律"]},
    {"title": "法拉第冰桶實驗", "type": "experiment", "domain": "電磁學", "summary": "法拉第冰桶實驗展示電荷如何重新分布在導體表面，強化對高斯定律與導體靜電平衡的理解。", "tested_laws": ["高斯定律"], "measured_quantities": ["電荷"], "related_concepts": ["電力線", "等位面"]},
    {"title": "滑軌能量轉換實驗", "type": "experiment", "domain": "力學", "summary": "滑軌能量轉換實驗用來觀察位能和動能之間的轉換，並估計非保守效應。", "tested_laws": ["機械能守恆"], "measured_quantities": ["速度"], "related_concepts": ["位能", "動能"]},
    {"title": "火箭方程", "type": "law", "domain": "力學", "summary": "火箭方程描述變質量系統藉由噴出質量獲得速度變化的關係。", "prerequisites": ["動量", "推進"], "related_concepts": ["牛頓萬有引力定律"], "related_laws": ["動量定理"], "derived_results": ["推進"]},
    {"title": "理想氣體方程式", "type": "law", "domain": "熱學與熱力學", "summary": "理想氣體方程式把壓力、體積、溫度與粒子數連結起來，是熱學建模的經典起點。", "prerequisites": ["壓力", "熱力學第零定律"], "related_concepts": ["內能", "等溫過程", "絕熱過程"], "related_quantities": ["壓力"], "related_laws": ["熱力學第一定律"]},
    {"title": "矩陣", "type": "mathematical_tool", "domain": "數學工具", "summary": "矩陣能把多變量線性關係與狀態轉換寫成緊湊形式，在現代物理特別重要。", "used_in": ["薛丁格方程", "狹義相對論"], "prerequisites": ["向量"], "related_concepts": ["對稱性"]},
    {"title": "磁場", "type": "concept", "domain": "電磁學", "summary": "磁場描述磁作用在空間中的分布，常與電流、移動電荷和感應現象一起出現。", "prerequisites": ["向量"], "related_laws": ["法拉第定律", "麥克斯威方程組"], "related_concepts": ["磁力", "電磁波"]},
    {"title": "等溫過程", "type": "concept", "domain": "熱學與熱力學", "summary": "等溫過程指系統在溫度保持不變下進行的熱力學變化。", "prerequisites": ["理想氣體方程式"], "related_laws": ["熱力學第一定律"], "related_concepts": ["卡諾循環", "絕熱過程"]},
    {"title": "絕熱過程", "type": "concept", "domain": "熱學與熱力學", "summary": "絕熱過程指系統與外界幾乎沒有熱交換時進行的變化。", "prerequisites": ["理想氣體方程式"], "related_laws": ["熱力學第一定律"], "related_concepts": ["卡諾循環", "等溫過程"]},
    {"title": "統計物理", "type": "concept", "domain": "熱學與熱力學", "summary": "統計物理從大量微觀粒子的機率分布出發，解釋巨觀熱力學量與不可逆現象。", "prerequisites": ["機率與統計"], "related_laws": ["熱力學第二定律"], "related_concepts": ["熵", "黑體輻射"]},
    {"title": "薛丁格方程", "type": "concept", "domain": "近代物理", "summary": "薛丁格方程是非相對論量子力學中描述波函數演化的核心方程。", "prerequisites": ["德布羅意波", "矩陣", "複數"], "related_concepts": ["光電效應", "黑體輻射"]},
    {"title": "虎克定律", "type": "law", "domain": "力學", "summary": "虎克定律指出彈性位移小時，回復力與位移大小成正比且方向相反。", "prerequisites": ["力", "位移"], "related_concepts": ["簡諧運動", "位能"], "related_laws": ["牛頓第二定律"], "derived_results": ["簡諧運動"]},
    {"title": "衝量", "type": "concept", "domain": "力學", "summary": "衝量是力在一段時間內的累積效果，直接對應動量改變。", "prerequisites": ["動量", "時間"], "related_laws": ["動量定理"], "related_concepts": ["碰撞分析"]},
    {"title": "質能等價", "type": "law", "domain": "近代物理", "summary": "質能等價指出質量與能量可以互換，並由 E = mc^2 連結。", "prerequisites": ["狹義相對論"], "related_concepts": ["黑體輻射"], "related_laws": ["狹義相對論"]},
    {"title": "都卜勒效應", "type": "concept", "domain": "振動與波動", "summary": "都卜勒效應描述波源與觀察者相對運動時所測得頻率的改變。", "prerequisites": ["聲波", "速度"], "related_concepts": ["電磁波"]},
    {"title": "阿基米德原理", "type": "law", "domain": "流體力學", "summary": "阿基米德原理指出浸入流體中的物體會受到大小等於所排開流體重量的浮力。", "prerequisites": ["密度", "壓力"], "related_concepts": ["平衡"], "related_quantities": ["密度"], "related_laws": ["連續方程"]},
    {"title": "顯微鏡", "type": "concept", "domain": "光學", "summary": "顯微鏡透過多個光學元件放大成像，是幾何光學與波動極限並存的典型裝置。", "prerequisites": ["薄透鏡公式", "光線模型"], "related_concepts": ["全反射", "偏振"]},
    {"title": "平行板電容器", "type": "concept", "domain": "電磁學", "summary": "平行板電容器是研究均勻電場、等位面與電容量的標準模型。", "prerequisites": ["無限平面電場", "等位面"], "related_concepts": ["電位能", "電場能量"]},
    {"title": "電場能量", "type": "concept", "domain": "電磁學", "summary": "電場能量把儲存在電場分布中的能量視為場本身的性質，而不只附著在粒子上。", "prerequisites": ["電位能", "平行板電容器"], "related_concepts": ["電磁波", "能量"]},
    {"title": "共振", "type": "concept", "domain": "振動與波動", "summary": "共振發生在外加驅動頻率接近系統固有頻率時，使振幅大幅放大的現象。", "prerequisites": ["簡諧運動"], "related_concepts": ["駐波", "交流電"]},
]


MAP_UPDATES = [
    {"path": "00_maps/力學總覽.md", "marker": "## 第三批擴充節點", "links": ["功", "動能", "位能", "保守力", "萬有引力定律", "角動量", "轉矩", "圓周運動", "碰撞分析"]},
    {"path": "00_maps/振動與波動總覽.md", "marker": "## 第三批擴充節點", "links": ["簡諧運動", "共振", "駐波", "聲波", "干涉", "都卜勒效應"]},
    {"path": "00_maps/電磁學總覽.md", "marker": "## 第三批擴充節點", "links": ["等位面", "電位能", "平行板電容器", "電場能量", "麥克斯威方程組", "法拉第定律", "電磁波", "磁場"]},
    {"path": "00_maps/熱學與熱力學總覽.md", "marker": "## 第三批擴充節點", "links": ["熱", "內能", "熵", "熱力學第零定律", "熱力學第二定律", "理想氣體方程式", "卡諾循環", "等溫過程", "絕熱過程", "統計物理"]},
    {"path": "00_maps/流體力學總覽.md", "marker": "## 第三批擴充節點", "links": ["密度", "壓力", "流量", "連續方程", "阿基米德原理", "文氏管"]},
    {"path": "00_maps/光學總覽.md", "marker": "## 第三批擴充節點", "links": ["反射定律", "全反射", "惠更斯原理", "干涉", "偏振", "薄透鏡公式", "顯微鏡"]},
    {"path": "00_maps/近代物理總覽.md", "marker": "## 第三批擴充節點", "links": ["狹義相對論", "黑體輻射", "光電效應", "德布羅意波", "薛丁格方程", "質能等價"]},
    {"path": "00_maps/數學工具總覽.md", "marker": "## 第三批擴充節點", "links": ["面積分", "散度", "旋度", "矩陣", "機率與統計"]},
]


def output_path(vault: Path, page: dict) -> Path:
    folder = {
        "law": "01_laws",
        "concept": "02_concepts",
        "quantity": "03_quantities",
        "experiment": "04_experiments",
        "mathematical_tool": "05_mathematical_tools",
    }[page["type"]]
    return vault / folder / f"{page['title']}.md"


def write_pages(vault: Path, force: bool) -> tuple[int, int]:
    created = 0
    skipped = 0
    for page in PAGES:
        path = output_path(vault, page)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not force:
            skipped += 1
            continue
        path.write_text(build_page(page), encoding="utf-8")
        created += 1
    return created, skipped


def ensure_map_update(vault: Path, update: dict) -> bool:
    path = vault / update["path"]
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if update["marker"] in text:
        return False
    bullets = "\n".join(f"- [[{item}]]" for item in update["links"])
    addition = f"\n\n{update['marker']}\n{bullets}\n"
    path.write_text(text.rstrip() + addition, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the third batch of physics encyclopedia notes.")
    parser.add_argument("--vault", required=True, help="Vault root path")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files if they already exist")
    args = parser.parse_args()

    vault = Path(args.vault).resolve()
    created, skipped = write_pages(vault, args.force)
    updated_maps = sum(1 for item in MAP_UPDATES if ensure_map_update(vault, item))
    print(f"Created {created} notes, skipped {skipped} existing notes, updated {updated_maps} map pages.")


if __name__ == "__main__":
    main()
