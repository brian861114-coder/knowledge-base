#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from kb_paths import resolve_vault_path


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
TARGET_HEADING = "現代理論視角"
INSERT_BEFORE = "相關連結"


MODERN_PERSPECTIVES: dict[str, str] = {
    "加速度": "在現代力學裡，加速度不只是運動學描述量，更是把動力學、幾何約束與參考系選擇綁在一起的核心量。從廣義座標到廣義相對論中的測地偏離，『加速度如何被定義、由誰測得、在何種框架下寫出來』本身就已經成為理論內容的一部分。",
    "動量": "在現代理論中，動量不只是質量乘速度，而是由平移對稱性導出的守恆量。從拉格朗日與哈密頓形式，到量子力學裡作為平移生成元的動量算符，這個量的地位比經典粒子圖像更基本。",
    "壓力": "現代物理把壓力看成連續介質中應力張量的各向同性部分，而不只是容器壁上的推擠感。它同時出現在流體方程、等離子體描述、凝態系統與宇宙學有效流體模型中，是巨觀狀態與微觀自由度之間的重要橋梁。",
    "密度": "在現代理論中，密度通常被提升為場的觀點來處理，不再只是『每單位體積多少東西』。質量密度、電荷密度、機率密度與能量密度都各自對應不同守恆律與動力方程，說明密度是連續描述的基本語言。",
    "應變": "在現代材料與連續介質理論裡，應變被視為形變場的局部幾何資訊，而不只是長度改變比例。從小變形近似到有限變形理論，再到晶體缺陷與彈塑性模型，應變都是連接幾何與材料響應的核心量。",
    "折射率": "現代光學中，折射率不再只是光線偏折的方便參數，而是材料電磁響應的有效表徵。色散、吸收、負折射率、各向異性介質與超材料都說明折射率背後其實是更完整的介電函數與微觀極化機制。",
    "效率": "在現代理論視角下，效率不是單純的輸出除以輸入，而是受守恆律、不可逆性與資源限制共同約束的性能指標。從熱機到資訊處理與量子裝置，效率都要放在可達極限、耗散機制與最佳化問題中理解。",
    "李雅普諾夫指數": "現代非線性動力學把李雅普諾夫指數當成判定軌道穩定性與混沌程度的標準工具。它不只描述『會不會亂』，還把初始條件敏感性、吸引子結構與可預測性邊界量化為可比較的數值。",
    "楊氏模數": "在現代材料科學中，楊氏模數是彈性響應的低階有效參數，而不是材料本性的全部。各向異性、溫度依賴、微觀結構、頻率響應與非線性效應都會讓『一個固定模數』只在有限條件下成立。",
    "比熱": "現代理論中，比熱是最直接暴露自由度結構的熱力學量之一。從經典等分配失效到量子統計修正，再到相變附近的臨界行為，比熱往往不是附帶參數，而是用來辨識微觀機制的診斷量。",
    "泊松比": "在現代理論裡，泊松比反映的是材料內部形變耦合方式，而不只是『拉長時橫向會縮多少』。對多孔材料、複合材料、負泊松比結構與各向異性介質而言，它揭示的是微結構設計如何改寫巨觀力學響應。",
    "波印廷向量": "現代電磁理論把波印廷向量視為能流密度的標準描述，但也清楚知道它的詮釋依賴場分解與介質模型。它在天線、波導、電磁波傳輸與光學能流分析中仍然核心，但必須放在完整電磁應力能量框架裡理解。",
    "波速": "在現代理論中，波速不能只看成『波走多快』，而要區分相速度、群速度、訊號速度與前沿速度。色散介質、量子波包與相對論限制都提醒我們，不同速度概念對應不同物理問題，不能混用。",
    "波長": "現代物理中的波長同時是幾何尺度、頻譜尺度與量子尺度。從繞射與干涉，到德布羅意波長與晶格散射，波長之所以重要，是因為它決定了系統會不會對某些結構尺度敏感。",
    "流量": "現代流體與輸運理論把流量視為守恆方程在截面上的整體表現，而不是單純『每秒過多少』。它與局部速度場、壓力分布、黏滯耗散與邊界條件共同決定系統輸運能力。",
    "真空光速": "在現代理論中，真空光速不是單純的電磁波速度常數，而是時空結構本身的一部分。相對論把它放進因果結構、時空度量與場方程的核心位置，因此它的意義遠超過『光跑得很快』。",
    "角位移": "現代力學中，角位移在小轉角近似下可以當成普通變量，但在完整剛體運動裡其實涉及旋轉群的非交換結構。這也是為什麼三維轉動問題不能被天真地視為一維角度的直接延伸。",
    "角加速度": "在現代理論裡，角加速度不只是角速度的變化率，還反映旋轉自由度如何受力矩與幾何約束支配。當轉動軸改變、剛體非對稱或採用不同參考架時，角加速度的結構會比平移加速度複雜得多。",
    "角速度": "現代力學把角速度看成描述旋轉生成元的量，而不只是『每秒轉幾圈』。在剛體運動、流體渦量與群論表述中，角速度的本質都和旋轉對稱的數學結構緊密相關。",
    "角頻率": "在現代物理裡，角頻率比普通頻率更自然，因為它直接進入微分方程、相位演化與複指數表示。從量子相位因子到交流電路與場模態分析，角頻率都是把週期現象寫進理論骨架的標準參數。",
    "質量": "現代物理對質量的理解早就超過『慣性大小』。在粒子物理中它與對稱性破缺相關，在相對論裡它和能量動量關係綁定，在廣義相對論裡又不能只靠一個簡單的牛頓式直覺來理解。",
    "轉動動能": "現代力學把轉動動能視為配置空間度量與慣性結構共同決定的二次型，而不只是套用一個公式。這讓它能自然接到剛體主軸、拉格朗日量、正則動力學與連續介質轉動模式的分析。",
    "轉動慣量": "在現代理論中，轉動慣量的完整版本是慣量張量，而不是單一數字。只有在特定對稱軸或簡化情況下，它才退化成標量；一旦剛體形狀複雜，轉動慣量就直接決定轉動穩定性與主軸結構。",
    "速度": "現代物理中的速度看似基本，實際上在不同理論裡角色很不一樣。相對論限制了可達速度範圍，哈密頓力學不把速度視為最基本變量，而量子理論裡速度甚至不總是最方便的描述語言。",
    "雷諾數": "現代流體力學把雷諾數當成主導機制競爭的無因次參數，而不是單純分類標籤。它濃縮了慣性效應與黏滯效應的相對強弱，因此能預示流況穩定性、邊界層行為與湍流出現條件。",
    "電位差": "現代電磁理論裡，電位差仍然非常有用，但它的真正位置要放回標位、場與能量觀點一起看。對靜電問題它很乾淨，對時變電磁場則必須結合向量勢與完整場描述，不能把它當成萬用基本量。",
    "電偶極矩": "現代物理把電偶極矩從兩個電荷的簡單模型，推廣到分子、介質、原子躍遷與輻射耦合的統一語言。它直接控制外場耦合強度與輻射選擇規則，因此在量子與材料問題中特別重要。",
    "電動勢": "現代觀點下，電動勢不是單純『電壓來源』的別名，而是非靜電作用沿閉路驅動電荷的總效果。這讓它可以同時涵蓋化學電池、感應電場與發電機機制，並與保守電位差區分開來。",
    "電導率與電阻率": "現代材料物理把電導率與電阻率視為輸運係數，而不是固定常數。它們會隨溫度、頻率、雜質、能帶結構與微觀散射機制改變，因此真正重要的是背後的載流子動力學。",
    "電流": "在現代理論中，電流不只是導線裡有多少電荷流過，而是守恆方程中的流密度積分表現。這讓它能自然延伸到位移電流、量子機率流與場論中的守恆流觀念。",
    "電流密度": "現代電磁與輸運理論把電流密度看成局部載流狀態的基本變量。歐姆定律、連續方程、麥克斯威方程與半導體輸運模型都更自然地寫在電流密度層級，而不是只看總電流。",
    "電荷": "現代物理對電荷的理解包含守恆、量子化與規範對稱三個層次。它既是可量測的源項，又是場論裡對稱性的 Noether 荷，因此電荷的地位比『帶電或不帶電』這種日常分類深得多。",
    "電阻": "現代觀點下，電阻不是元件貼上的單一數字，而是材料、幾何、頻率與接觸條件共同決定的有效響應。當尺度縮小到介觀或奈米系統時，電阻的定義與經典直覺都會被重新檢驗。",
    "頻率": "現代物理中的頻率不只是每秒重複幾次，而是系統特徵尺度與譜結構的直接指標。從傅立葉分析、共振、量子能階到場模態，頻率都扮演辨認系統內在結構的核心角色。",
    "體應變": "現代連續介質理論把體應變視為局部體積改變的標準量，特別適合描述壓縮、膨脹與流固耦合問題。它與剪切形變分開處理，讓材料模型可以更清楚區分不同類型的形變成本。",
    "體積彈性模數": "在現代材料與流體理論裡，體積彈性模數控制的是系統對均勻壓縮的抗拒程度。它不只出現在固體，也深度影響聲速、可壓縮流動與高壓狀態方程的寫法。",
    "體積模數": "體積模數的現代理論意義在於它把宏觀可壓縮性和微觀結構穩定性連起來。無論是流體、晶體還是地球內部物質模型，體積模數都是判斷介質在壓力下如何重排的重要參數。",
    "黏度": "現代輸運理論把黏度看成動量擴散係數，而不是單純『流體有多黏』的口語描述。它連接了微觀碰撞機制、巨觀剪切耗散與湍流有效模型，因此是跨尺度輸運問題的核心量。",    
}


def parse_frontmatter(text: str) -> tuple[str, str]:
    text = text.lstrip("\ufeff")
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 5 :]


def parse_frontmatter_data(raw: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data


def find_insert_offset(body: str) -> int:
    for match in SECTION_RE.finditer(body):
        if match.group(1).strip() == INSERT_BEFORE:
            return match.start()
    return len(body)


def ensure_modern_section(body: str, content: str) -> tuple[str, bool]:
    if f"## {TARGET_HEADING}" in body:
        return body, False
    offset = find_insert_offset(body)
    block = f"## {TARGET_HEADING}\n{content}\n\n"
    updated = body[:offset].rstrip() + "\n\n" + block + body[offset:].lstrip()
    return updated, True


def process_file(path: Path, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    raw_frontmatter, body = parse_frontmatter(text)
    frontmatter = parse_frontmatter_data(raw_frontmatter)
    title = frontmatter.get("title", "").strip() or path.stem
    content = MODERN_PERSPECTIVES.get(title)
    if not content:
        return False
    new_body, changed = ensure_modern_section(body, content)
    if not changed:
        return False
    if dry_run:
        return True
    final = f"---\n{raw_frontmatter}\n---\n{new_body}" if raw_frontmatter else new_body
    path.write_text(final, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill missing 現代理論視角 sections for quantity notes.")
    parser.add_argument("--vault", help="Override vault path")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--relative-path", help="Process only one note relative to the vault root")
    args = parser.parse_args()

    vault = resolve_vault_path(args.vault)
    if args.relative_path:
        changed = process_file(vault / args.relative_path, args.dry_run)
        print(f"changed={1 if changed else 0}")
        return

    changed = 0
    matched = 0
    quantity_dir = vault / "03_quantities"
    for path in sorted(quantity_dir.glob("*.md")):
        title = path.stem
        if title not in MODERN_PERSPECTIVES:
            continue
        matched += 1
        if process_file(path, args.dry_run):
            changed += 1
    print(f"matched={matched}")
    print(f"changed={changed}")
    print(f"dry_run={args.dry_run}")


if __name__ == "__main__":
    main()
