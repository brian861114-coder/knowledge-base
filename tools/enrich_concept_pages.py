#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
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
    items = []
    for part in inner.split(","):
        item = strip_wikilink(part.strip())
        if item:
            items.append(item)
    return items


def parse_frontmatter(text: str) -> tuple[str, dict[str, object], str]:
    if not text.startswith("---\n"):
        return "", {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", {}, text
    raw = text[4:end]
    body = text[end + 5 :]
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
    return raw, data, body


def bullet_links(items: list[str], fallback: str) -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- [[{item}]]" for item in items)


def join_titles(items: list[str], fallback: str) -> str:
    if not items:
        return fallback
    if len(items) == 1:
        return f"[[{items[0]}]]"
    if len(items) == 2:
        return f"[[{items[0]}]] 與 [[{items[1]}]]"
    return "、".join(f"[[{item}]]" for item in items[:-1]) + f" 與 [[{items[-1]}]]"


def domain_tag(domain: str) -> str:
    mapping = {
        "力學": "受力、運動、守恆量與系統邊界",
        "電磁學": "場、源、對稱性與勢能觀點",
        "振動與波動": "相位、週期、邊界條件與疊加",
        "熱學與熱力學": "狀態量、過程、平衡與不可逆性",
        "光學": "幾何近似、波動圖像與成像條件",
        "近代物理": "模型有效範圍、量子化與對稱性",
    }
    return mapping.get(domain, "定義、模型、近似與適用條件")


@dataclass
class ConceptSpec:
    definition: str
    math: list[str]
    examples: list[str]
    misconceptions: list[str]
    advanced: str
    analysis: list[str] | None = None


SPECIAL: dict[str, ConceptSpec] = {
    "力": ConceptSpec(
        definition="力描述系統之間的交互作用如何改變物體的動量。從操作性定義來看，若一個物體的動量隨時間改變，則我們把造成該改變的外在交互作用統稱為力。這個定義把『推、拉、壓、摩擦、彈性、重力、電力』放進同一套語言中。",
        math=[
            r"在單一粒子模型中，\(\vec F_{\text{net}} = \dfrac{d\vec p}{dt}\)。當質量可視為常數時，才退化成常見的 \(\vec F_{\text{net}} = m\vec a\)。",
            r"力是向量，大小、方向、作用線與施力點都會影響結果；對剛體還必須進一步考慮轉動效應與 [[轉矩]]。",
        ],
        examples=[
            "用自由體圖拆解斜面問題，分辨重力、正向力與摩擦力各自扮演的角色。",
            "在圓周運動中，所謂『向心力』不是新種類的力，而是徑向淨力所扮演的角色名稱。",
        ],
        misconceptions=[
            "把力當成維持運動所需的『燃料』，忽略沒有淨力也能保持等速度運動。",
            "把向心力誤認為獨立作用力，而不是淨力在某方向上的分量。",
        ],
        advanced="在更高階的力學中，力不一定是最根本的描述。拉格朗日與哈密頓形式改用能量、廣義座標與作用量來組織動力學，但在可觀測層次上仍會回到與力等價的預測。",
        analysis=[
            "先明確選定系統邊界，區分內力與外力。",
            "畫出自由體圖，決定座標軸與正方向。",
            "把向量方程拆成分量，檢查是否需要轉動方程。",
        ],
    ),
    "電場": ConceptSpec(
        definition="電場把『電荷彼此作用』改寫成『空間中每一點都帶有可定義的作用狀態』。某點的電場定義為單位正試驗電荷置於該點時所受的力，因此它是位置的函數，而不是只屬於某一顆測試粒子。",
        math=[
            r"\(\vec E = \vec F/q\)，其中 \(q\) 是放在該點的試驗電荷。",
            r"對點電荷 \(Q\)，真空中 \(\vec E = \dfrac{1}{4\pi\varepsilon_0}\dfrac{Q}{r^2}\hat r\)。對連續電荷分布則需積分疊加。",
            r"若系統具有高對稱性，可改用 [[高斯定律]]：\(\oint \vec E \cdot d\vec A = Q_{\text{enc}}/\varepsilon_0\)。",
        ],
        examples=[
            "由球對稱電荷分布推得徑向電場，理解為何球殼內部電場可為零。",
            "用近似均勻電場分析平行板電容器中的電位差與帶電粒子運動。",
        ],
        misconceptions=[
            "把電場線當成真實存在的細線，而不是視覺化工具。",
            "以為只有有電荷的地方才有電場，忽略源可以在別處而場分布延伸到空間中。",
        ],
        advanced="在現代電磁學裡，電場與磁場不是彼此孤立的兩種東西，而是同一電磁場在不同參考架構與不同分量上的表現。這也是為什麼場論語言比遠距作用更有組織力。",
        analysis=[
            "先辨識源的幾何對稱性，再決定用庫侖積分或高斯定律。",
            "區分『求場』與『求試驗電荷受力』這兩個步驟。",
            "若題目涉及位能或做功，改用 [[電位]] 與 [[等位面]] 常會更簡潔。",
        ],
    ),
    "簡諧運動": ConceptSpec(
        definition="簡諧運動是小振幅線性回復系統的標準模型。其核心不是『看起來週期』，而是回復力或回復效應對平衡位置附近的位移呈線性，且方向指向平衡點。",
        math=[
            r"典型條件寫成 \(F_x = -kx\) 或 \(a_x = -\omega^2 x\)。",
            r"解為 \(x(t)=A\cos(\omega t+\phi)\) 或等價的正弦形式，其中 \(A\)、\(\omega\)、\(\phi\) 分別控制振幅、角頻率與初相位。",
            r"速度與加速度分別為 \(v(t) = -A\omega\sin(\omega t+\phi)\)、\(a(t)=-\omega^2 x(t)\)。",
        ],
        examples=[
            "彈簧振子在小振幅、線性彈性條件下是最經典的簡諧模型。",
            r"小角度單擺可在 \(\sin\theta \approx \theta\) 近似下轉成簡諧運動。",
        ],
        misconceptions=[
            "把任何週期運動都叫做簡諧運動，忽略其實需要線性回復條件。",
            "只記位移方程，不去看相位差、能量交換與模型近似的範圍。",
        ],
        advanced="簡諧運動的地位非常特殊，因為許多系統在穩定平衡點附近做泰勒展開後，一階項消失、二階項主導，最後都會近似成簡諧運動。這使它成為振動、波動、量子振子與電路振盪共同的局部模型。",
        analysis=[
            "先找平衡位置，再檢查回復效應是否可線性化。",
            "用初始條件決定振幅與初相位，而不是硬背單一標準答案。",
            r"若題目要求能量觀點，直接寫 \(E = \frac12 kA^2 = \frac12 kx^2 + \frac12 mv^2\)。",
        ],
    ),
    "能量": ConceptSpec(
        definition="能量不是一種具體物質，而是統整物理過程的狀態量與記帳語言。當模型具有適當對稱性與邊界條件時，能量守恆讓我們不用逐點追蹤每一個作用力，也能掌握系統如何演化。",
        math=[
            r"在經典力學裡，常見形式包含動能 \(K=\frac12 mv^2\) 與位能 \(U\)；封閉系統中總機械能可寫成 \(E = K + U\)。",
            r"更一般地，能量會以平移、轉動、熱、場能、化學能等不同形式出現，重點在於轉換與守恆，而不是名稱本身。",
        ],
        examples=[
            "斜面滑塊可用能量法避開逐時刻求加速度。",
            "電容器把能量儲存在電場分布中，而不是只『放在電荷上』。",
        ],
        misconceptions=[
            "把能量理解成永遠看得見的東西，忽略它常常是藉由差值、守恆與轉換來被辨識。",
            "只會套守恆式，卻不先確認是否有非保守作用或外界做功。",
        ],
        advanced="在更深層的理論裡，能量與時間平移對稱性緊密相關。從 Noether 定理的角度看，守恆不是偶然巧合，而是系統對稱結構的結果。",
    ),
    "位能": ConceptSpec(
        definition="位能是用來描述保守交互作用的標量函數。當作用力可由位置函數導出時，我們能把『沿路徑累積的做功』改寫成『只看初末狀態的能量差』。",
        math=[
            r"若力為保守力，則 \(\Delta U = -W_{\text{cons}}\)。在一維中可寫成 \(F_x = -\,dU/dx\)。",
            r"平衡點可藉由 \(dU/dx=0\) 判斷；若 \(d^2U/dx^2>0\) 則為局部穩定平衡。",
        ],
        examples=[
            "近地表重力位能 \(U = mgh\) 是均勻重力場的近似形式。",
            r"彈簧位能 \(U=\frac12 kx^2\) 直接對應線性回復力。",
        ],
        misconceptions=[
            "把位能當成物體絕對擁有的數值，而不是依賴零點選擇的描述。",
            "只記公式，不去想該公式來自什麼力模型與近似範圍。",
        ],
        advanced="位能圖像在高階物理裡極有用，因為它把穩定性、束縛態、障壁穿越與小振動近似放到同一張圖上。很多看似不同的問題都能透過勢阱與有效位能的觀點來統一理解。",
    ),
    "保守力": ConceptSpec(
        definition="保守力的關鍵特徵是做功與路徑無關，只由初末位置決定。這代表系統存在一個位能函數，使得力可以視為位能梯度的負值。",
        math=[
            r"若沿任意封閉路徑 \(\oint \vec F \cdot d\vec r = 0\)，則該力場可視為保守力。",
            r"在適當條件下，\(\vec F = -\nabla U\)。",
        ],
        examples=[
            "重力與理想彈力通常可視為保守力。",
            "動摩擦力通常不是保守力，因為做功與路徑與耗散歷程有關。",
        ],
        misconceptions=[
            "把『大小固定』誤當成保守力判準；真正的判準是做功與路徑關係。",
            "見到位能就直接套用，沒先確認是否存在耗散或非保守驅動。",
        ],
        advanced="保守力的真正力量在於把動力學問題降維成幾何問題。當你能畫出位能曲線，就能直接讀出平衡、穩定性、轉折點與可達區域。",
    ),
}


def default_definition(title: str, domain: str, summary: str) -> str:
    return (
        f"{summary} 在大學物理的語境裡，{title} 不只是名詞定義，而是用來組織 {domain} 問題的分析框架。"
        f" 真正有用的理解方式，是知道它在什麼條件下適用、能把哪些量連接起來，以及它與 {domain_tag(domain)} 之間的關係。"
    )


def default_math(title: str, domain: str, laws: list[str], quantities: list[str], tools: list[str]) -> list[str]:
    lines = [
        f"{title} 在解題時通常不會獨立出現，而會和 {join_titles(laws, f'{domain}中的核心定律')}、{join_titles(quantities, '相關狀態量')} 一起構成可計算的方程。",
    ]
    if tools:
        lines.append(f"從數學工具看，這個概念經常需要用到 {join_titles(tools, '基本代數與微積分')} 來表達方向、變化率、積累量或近似條件。")
    lines.append(f"大學程度的重點不是只會背結果，而是能把文字敘述翻成變數、方程、限制條件，再反過來解讀方程對現象的意義。")
    return lines


def default_examples(title: str, domain: str, related: list[str]) -> list[str]:
    items = [
        f"先在標準教材例題中辨識 {title} 如何決定主要變數與近似條件。",
        f"再把 {title} 與 {join_titles(related, f'{domain}中的鄰近概念')} 放在同一題裡比較，建立它的角色邊界。",
    ]
    return items


def default_misconceptions(title: str, laws: list[str], related: list[str]) -> list[str]:
    items = [
        f"把 {title} 當成一句口訣或單一公式，忽略它其實是一組判準。",
        f"沒有先檢查與 {join_titles(laws or related, '相關模型')} 的適用條件，就直接把熟悉的式子套上去。",
    ]
    return items


def default_advanced(title: str, domain: str) -> str:
    return (
        f"到了更進一步的課程，{title} 往往會被放進更抽象的 {domain} 模型中，例如連續介質、場論、變分方法或統計描述。"
        f" 這些進階形式通常不是推翻基本概念，而是讓我們更清楚看見它的有效範圍與深層結構。"
    )


def build_sections(meta: dict[str, object]) -> str:
    title = str(meta.get("title", ""))
    domain = str(meta.get("domain", ""))
    summary = str(meta.get("summary", ""))
    prerequisites = [str(x) for x in meta.get("prerequisites", [])]
    laws = [str(x) for x in meta.get("related_laws", [])]
    quantities = [str(x) for x in meta.get("related_quantities", [])]
    related = [str(x) for x in meta.get("related_concepts", [])]
    tools = [str(x) for x in meta.get("math_tools", [])]

    spec = SPECIAL.get(title)
    definition = spec.definition if spec else default_definition(title, domain, summary)
    math_lines = spec.math if spec else default_math(title, domain, laws, quantities, tools)
    examples = spec.examples if spec else default_examples(title, domain, related)
    misconceptions = spec.misconceptions if spec else default_misconceptions(title, laws, related)
    advanced = spec.advanced if spec else default_advanced(title, domain)
    analysis = spec.analysis if spec and spec.analysis else [
        f"先確認題目把 {title} 放在哪一類系統與尺度下討論。",
        f"把 {title} 與已知量、未知量、守恆式或邊界條件連接起來。",
        "最後回頭檢查結果的方向、量綱、極限情形與物理解讀是否一致。",
    ]

    sections: list[str] = []
    sections.append(f"# {title}\n")
    sections.append("## 概念摘要\n" + summary + "\n")
    sections.append("## 嚴格定義與適用邊界\n" + definition + "\n")

    math_block = "\n".join(f"- {line}" for line in math_lines)
    sections.append("## 數學表述與核心關係\n" + math_block + "\n")

    sections.append(
        "## 物理圖像\n"
        f"在 {domain} 中，{title} 最重要的功能，是把零散現象壓縮成可比較的結構。"
        f" 學習時要一直問自己三件事：它描述的是狀態、變化、還是交互作用；它依賴哪些理想化；若條件改變，這個概念會先在哪裡失效。"
        "\n"
    )

    analysis_block = "\n".join(f"- {item}" for item in analysis)
    sections.append("## 解題時的分析框架\n" + analysis_block + "\n")

    example_block = "\n".join(f"- {item}" for item in examples)
    sections.append("## 代表性情境與例子\n" + example_block + "\n")

    sections.append(
        "## 與其他主題的連結\n"
        f"作為先備知識，可先回到：\n{bullet_links(prerequisites, f'先閱讀 [[{domain}總覽]] 建立全局脈絡。')}\n\n"
        f"在定律層次上，{title} 常與以下內容一起使用：\n{bullet_links(laws, f'回到 [[{domain}總覽]] 尋找對應定律。')}\n\n"
        f"在概念層次上，最值得連讀的是：\n{bullet_links(related, f'延伸閱讀 [[{domain}總覽]] 與鄰近章節。')}\n"
    )

    misconception_block = "\n".join(f"- {item}" for item in misconceptions)
    sections.append("## 常見誤解與辨識方式\n" + misconception_block + "\n")

    sections.append(
        "## 進一步視角\n"
        + advanced
        + "\n"
    )
    return "\n".join(sections).rstrip() + "\n"


def enrich_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    raw_frontmatter, meta, _body = parse_frontmatter(text)
    if not meta or meta.get("type") != "concept":
        return False
    new_body = build_sections(meta)
    new_text = f"---\n{raw_frontmatter}\n---\n\n{new_body}"
    if text == new_text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Rewrite concept notes with richer university-level content.")
    parser.add_argument("--vault", required=True, help="Vault root path")
    args = parser.parse_args()

    concept_dir = Path(args.vault).resolve() / "02_concepts"
    changed = 0
    total = 0
    for file_path in sorted(concept_dir.glob("*.md")):
        total += 1
        if enrich_file(file_path):
            changed += 1
    print(f"Processed {total} concept pages; updated {changed}.")


if __name__ == "__main__":
    main()
