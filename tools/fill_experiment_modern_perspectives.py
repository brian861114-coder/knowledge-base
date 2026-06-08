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
    "低摩擦滑車實驗": "在現代實驗物理與教學中，低摩擦滑車實驗的重要性不在於器材本身，而在於它提供了接近理想受力條件的受控平台。它對今日的意義，是把感測器、擬合與誤差分析整合進經典力學驗證流程，讓模型與資料之間的落差可以被量化而不是被忽略。",
    "兩滑車碰撞實驗": "現代視角下，兩滑車碰撞實驗是研究守恆律、碰撞模型與資料反演的簡化平台。它不只驗證動量守恆，也讓人比較彈性碰撞、非彈性碰撞與耗散機制如何在真實數據中留下痕跡。",
    "功能定理驗證實驗": "在現代教學與實驗分析裡，功能定理驗證實驗的價值在於把力學方程與能量語言直接對照。它提醒我們，能量方法不是牛頓方程的替代品，而是另一種在複雜系統中更穩定、更容易整合多種作用的描述框架。",
    "反射定律驗證實驗": "現代光學把反射定律視為波動光學、幾何光學與邊界條件的一致結果，而不只是光線作圖規則。這種驗證實驗今天仍有意義，因為它是更複雜光學系統校準與界面控制的基本起點。",
    "天平": "在現代實驗體系中，天平早已不只是古典量測工具，而是精密校準、標準傳遞與不確定度控制的一部分。它的現代理論意義在於把質量比較、平衡條件與儀器靈敏度放進同一套測量科學框架裡理解。",
    "安培力實驗": "現代電磁學裡，安培力實驗不只是導線受力示範，而是電流、磁場與機械效應耦合的直接展示。它對今日裝置物理的價值，延伸到馬達、磁致致動與電磁控制系統的基本工作原理。",
    "密立根油滴實驗": "在現代理論脈絡下，密立根油滴實驗最重要的地位，是把電荷量子化做成可重複的精密量測事實。雖然今天有更高精度的方法，但這個實驗仍然是理解基本常數、量子離散性與測量推論之間關係的經典範例。",
    "小車軌道實驗": "現代教學實驗中，小車軌道實驗是把運動模型、參數估計與誤差分析整合起來的基礎平台。它的現代價值不只在驗證公式，而在訓練如何從時間序列資料反推出合理的動力學模型。",
    "打點計時器": "從現代理論視角看，打點計時器代表的是離散取樣如何近似連續運動。它雖然是傳統工具，但正好能讓人理解今日數位感測與資料處理仍然面對的同一個核心問題：如何從有限解析度重建真實動態。",
    "扭秤實驗": "現代實驗物理仍然高度重視扭秤方法，因為它能把極微弱相互作用轉換成可積累的角位移訊號。從測量萬有引力常數到搜尋新力，扭秤一直是高靈敏弱訊號實驗的經典架構。",
    "文丘里管實驗": "現代流體工程把文丘里管實驗放在連續方程、壓力分布與流量量測的交界點上理解。它今天的意義不只是驗證伯努力方程，而是展示理想流假設如何在工程量測中被近似使用與修正。",
    "氣墊軌道碰撞實驗": "在現代實驗設計裡，氣墊軌道碰撞實驗提供了比一般滑車更接近低耗散條件的碰撞平台。它對理論的價值在於能更乾淨地分離守恆效應與非理想耗散效應，適合做精細的模型比較。",
    "法拉第冰桶實驗": "現代電磁理論會把法拉第冰桶實驗看成導體邊界條件與電荷重分布的經典驗證。它的持久價值在於：即使在更複雜的靜電屏蔽與電容系統中，核心觀念仍然是同一套場與邊界的邏輯。",
    "滑軌能量轉換實驗": "現代觀點下，滑軌能量轉換實驗是耗散、守恆與儀器誤差同場競爭的案例。它提醒我們，所謂『能量守恆驗證』實際上常常是在辨認哪些能量通道被納入模型、哪些被儀器與近似吃掉。",
    "相空間軌跡模擬": "在現代動力系統理論中，相空間軌跡模擬的地位比單純位置時間圖更基本。它直接展示穩定點、極限環、分岔與混沌結構，因此是把運動方程轉譯成幾何結構的關鍵工具。",
    "赫茲電磁波實驗": "現代理論會把赫茲電磁波實驗視為馬克士威方程組最具歷史重量的驗證之一。它的現代意義不只在證明電磁波存在，更在於打開無線通訊、波導、天線與整個電磁工程體系的實驗基礎。",
    "轉動慣量量測實驗": "在現代力學與工程中，轉動慣量量測實驗的價值在於把抽象的慣性結構轉成可標定的系統參數。這對剛體動力學、機械設計、控制系統與機器人建模都非常關鍵。",
    "運動感測器": "現代運動感測器的理論意義，在於它把運動學從手工讀值推進到連續資料擷取與即時建模。它不是單純方便，而是改變了我們分析速度、加速度與模型殘差的解析度。",
    "雙狹縫實驗": "在現代理論中，雙狹縫實驗的地位遠超過波動干涉示範，因為它同時碰到相干性、路徑資訊與量子測量問題。它之所以經典，是因為經典波動與量子機率振幅都能在這裡留下不可忽視的結構。",
    "電導率量測實驗": "現代材料與元件物理把電導率量測視為辨識載流機制的基本入口。它不只是量一個數，而是連到材料純度、散射機制、溫度依賴與微結構如何控制宏觀輸運。",
    "電路驗證實驗": "在現代理論與工程實作中，電路驗證實驗的作用是檢查理想電路模型在真實元件上的適用範圍。它讓歐姆定律、基爾霍夫定律與等效模型從紙面規則變成可校準、可修正的工程語言。",
    "靜電場模擬實驗": "現代靜電場模擬實驗的價值在於把邊界條件、等位面與場線分布視覺化。它今天仍然重要，因為即使有數值模擬，實際觀察場形狀如何受幾何控制，仍是建立電磁直覺與驗證模型的重要方式。",
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
    parser = argparse.ArgumentParser(description="Fill missing 現代理論視角 sections for experiment notes.")
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
    experiment_dir = vault / "04_experiments"
    for path in sorted(experiment_dir.glob("*.md")):
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
