#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from kb_paths import resolve_vault_path


INTUITION_HEADING = "物理直覺"
HISTORY_HEADING = "歷史背景"
SECTION_RE = re.compile(r"^(##)\s+(.+)$", re.MULTILINE)
ANCHOR_KEYWORDS = ("問題背景", "裝置與方法", "核心分析", "常見誤解", "相關概念", "延伸價值")


MAP_INTUITION = {
    "力學總覽": "力學總覽的價值，不在於把牛頓定律、能量、動量和轉動全部平鋪列出來，而在於提醒你：這些頁面其實都在處理同一件事，也就是系統如何在交互作用下改變運動狀態。先抓主幹，再看支線，你才不會把整個領域讀成一堆彼此無關的公式。",
    "熱學與熱力學總覽": "熱學與熱力學總覽真正要幫你建立的，不是名詞清單，而是尺度感：哪些頁在談微觀粒子統計，哪些頁在談宏觀狀態量，哪些頁又是在處理不可逆方向與效率極限。這一層秩序抓住後，熱學就不會再像一堆溫度、熱量與熵的混戰。",
    "振動與波動總覽": "振動與波動總覽的用途，是把『局部來回變化』和『擾動如何傳播』這兩條線明確分開，再告訴你它們在哪裡重新接上。你如果一開始就混在一起讀，很容易把簡諧運動、共振、聲波、干涉全部攪成一鍋。",
    "電磁學總覽": "電磁學總覽最重要的，不是多，而是結構。這裡要看清楚的是：靜電、電路、磁場、感應、交流與電磁波並不是六個獨立章節，而是同一套場論語言在不同條件下的投影。總覽頁的工作，就是幫你把這條主線露出來。",
    "光學總覽": "光學總覽的關鍵，是幫你分辨哪些頁面還在幾何光線近似內，哪些頁面已經進入波動與干涉尺度，哪些頁面又在往近代物理過渡。只要這個分層看清楚，折射、成像、干涉與繞射就不會再像四套互不相干的技術。",
    "近代物理總覽": "近代物理總覽真正的作用，是告訴你舊直覺是怎麼一步步被證據逼到崩潰的。這裡不是在堆奇觀，而是在串連黑體輻射、光電效應、德布羅意波、波函數與相對論各自打穿了經典世界觀的哪一塊。",
    "流體力學總覽": "流體力學總覽的好處，是把壓力、流量、連續方程、伯努力與黏滯效應重新整理成同一張守恆與近似的地圖。這樣你才看得出哪些頁是在談理想化主幹，哪些頁是在談那套理想何時失效。",
    "數學工具總覽": "數學工具總覽不是附錄，而是翻譯層。它的用途，是提醒你不同章節其實共用同一批表示工具：向量處理方向，積分處理累積，複數處理相位，矩陣與算符處理耦合與狀態空間。把這張圖讀懂，很多物理頁會忽然變簡單。",
}


MAP_HISTORY = {
    "力學總覽": "這類總覽頁本身不是歷史對象，但它反映了後見之明：我們現在知道牛頓力學、能量語言、動量守恆與解析力學其實共享同一主幹，才有能力把原本分散的教材重新整理成一張較清楚的地圖。",
    "熱學與熱力學總覽": "熱學與熱力學的歷史特別曲折，因為它同時經歷了熱質說、能量觀、統計詮釋與不可逆性的重寫。總覽頁的存在，正好反映了後人已經能把這些原本橫跨不同時代的觀念放回同一條演化線上。",
    "振動與波動總覽": "波動主題的歷史不是單線發展，而是從聲學、弦振動、光學與後來的電磁理論多路匯流。總覽頁之所以有價值，正是因為今天的我們已經知道這些原本分散的問題其實共享相似結構。",
    "電磁學總覽": "電磁學的歷史像拼圖：靜電、電流、磁效應、感應與光一開始根本不是同一門學問。總覽頁的視角，其實反映的是馬克士威之後的後見之明，也就是我們終於知道這些現象都屬於同一場論骨架。",
    "光學總覽": "光學史多次改寫物理學的世界觀，從幾何光學到波動爭論，再到電磁波與量子效應。總覽頁把這些層次壓在一起，本身就在展示：光不是單一章節，而是物理史上反覆出現的理論轉折點。",
    "近代物理總覽": "近代物理總覽最能體現後見之明。當年黑體輻射、光電效應、相對論與量子波函數各自爆炸，並不是自然排列成教科書章節；是後來整套新理論逐步穩定後，我們才有辦法把這些斷裂整理成一張可讀地圖。",
    "流體力學總覽": "流體力學一直夾在理論與工程之間成長。總覽頁把理想流體、壓力場、流量與黏滯效應收成一張圖，其實反映的是這門學科歷史上如何在簡化模型與真實複雜性之間來回協商。",
    "數學工具總覽": "數學工具總覽的歷史意味很直接：今天在物理裡看起來理所當然的向量、積分、矩陣與複數，其實各自都有被懷疑、被競爭、再被吸收進物理的過程。總覽頁正好把這些被勝出的語言放進同一層翻譯框架。",
}


EXPERIMENT_INTUITION = {
    "低摩擦滑車實驗": "低摩擦滑車實驗的重點，不是讓器材看起來很專業，而是盡量把摩擦這個討厭的干擾壓低，逼近牛頓力學裡那些理想條件。它的價值在於讓你看見：理論不是天然在世界上裸奔，而是要靠設計裝置把雜訊壓下去，規律才會浮出來。",
    "兩滑車碰撞實驗": "兩滑車碰撞實驗真正有教育性的地方，是它讓動量守恆從一句定律變成可量測帳本。你會直接看到：碰撞再亂，總交換還是得對上，差別只在能量有沒有流到形變、聲音或熱裡去。",
    "天平": "天平的物理意義，不只是秤重，而是把『平衡』這個概念做成肉眼可見的判準。當兩邊條件對上時，系統不再偏轉，這件事其實把力矩、重力與比較標準全部壓在同一個裝置裡。",
    "密立根油滴實驗": "密立根油滴實驗最狠的地方，是它把電子電荷量子化這件事拉到可反覆量測的層次。你不是只聽說電荷有基本單位，而是會被迫看見：那些數值真的成串落在同一個基本步長上。",
    "小車軌道實驗": "小車軌道實驗的用途，是把抽象的受力與加速度關係壓成可追蹤的位移與時間資料。真正的學習點不在跑出一條直線，而在於你會看見哪裡是理想近似、哪裡開始被摩擦、傾斜或測量誤差拖走。",
    "打點計時器": "打點計時器看起來很土，但它直接把連續運動切成可量測的時間片。這讓速度、加速度與位移不再只靠目測，而能從一串離散點跡重新建回動力學敘述。",
    "扭秤實驗": "扭秤實驗的物理直覺在於：極小的力不是不存在，而是需要極高靈敏度的機械回應才能被放大。你會清楚感受到，弱作用力的量測從來不是『看不到就算了』，而是設計一套讓微小扭轉可積累、可放大的裝置。",
    "法拉第冰桶實驗": "法拉第冰桶實驗最值得注意的是，它把電荷守恆與感應這種看不見的場效應，變成可檢出的電量重新分配。也就是說，你不是在看神奇效果，而是在看導體如何被場條件逼著重新排布電荷。",
    "滑軌能量轉換實驗": "滑軌能量轉換實驗的價值，在於它讓能量守恆從抽象總帳變成不同帳戶間的真實轉帳：位能、動能、摩擦損耗與測量誤差會同時上桌。你很難再把守恆當口號，因為每一筆落差都得解釋。",
    "運動感測器": "運動感測器的重要性，不是高科技，而是它讓運動學從稀疏點跡升級成連續資料流。這使得瞬時速度、加速度和模型擬合不再只能靠手算差分，而能更直接地看出理論何時貼合、何時脫軌。",
}


EXPERIMENT_HISTORY = {
    "低摩擦滑車實驗": "這類實驗的歷史背景，和近代力學教育如何把理想模型逼近真實世界有關。隨著機械設計與量測工具成熟，物理學家與教師才有能力把摩擦壓低到足以近似牛頓理想條件，讓定律真正被乾淨驗證。",
    "兩滑車碰撞實驗": "碰撞實驗長期是動量守恆語言站穩的核心場域之一。從早期機械研究到現代教學裝置，人們一直利用這類系統來分辨：哪些總量會保住，哪些則會被內部耗散重新分配。",
    "天平": "天平是最古老、最有代表性的物理裝置之一。從阿基米德到近代實驗科學，它一直在訓練人們用平衡條件而非主觀感覺來比較量的大小，也因此是力學與量測文化共同的起點。",
    "密立根油滴實驗": "密立根油滴實驗在二十世紀初非常關鍵，因為它讓基本電荷不再只是理論猜測，而成為可量測常數。它和湯姆生的電子發現、後來的量子論一起，鞏固了電荷離散化的世界圖像。",
    "小車軌道實驗": "滑車與軌道類實驗的歷史角色，在於它們替牛頓力學提供了可重複、可量測、可教學化的驗證平台。很多原本只在理論裡寫得漂亮的關係，都是靠這類裝置才真正變成可觀察結構。",
    "打點計時器": "打點計時器屬於運動量測技術逐步成熟的一部分。它的重要性不在高精度，而在於它讓經典運動學第一次能被大量學生與實驗室用相對廉價方式具體重建。",
    "扭秤實驗": "扭秤實驗在物理史上地位很高，因為它讓極小作用力第一次可以被系統性量測。從庫侖定律到萬有引力常數測量，扭秤都扮演了把微弱作用拉進定量科學的關鍵角色。",
    "法拉第冰桶實驗": "法拉第冰桶實驗的重要性，在於它把導體內部感應與電荷重新分配變成可觀測事實。這類實驗幫助十九世紀電學從神祕現象走向明確的導體與場結構理解。",
    "滑軌能量轉換實驗": "這類能量轉換實驗的歷史背景，和十九世紀能量觀成熟密切相關。當物理學從活力爭論走向統一能量帳本後，各種機械裝置便成了驗證與教學能量守恆的天然舞台。",
    "運動感測器": "運動感測器代表的是較晚近的實驗技術轉折：物理教學與研究不再只能依賴人工讀數與稀疏點跡，而能即時取得連續運動資料。這改變的不是定律本身，而是我們接近與檢驗它們的解析度。",
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
        heading = match.group(2).strip()
        if any(keyword in heading for keyword in ANCHOR_KEYWORDS):
            return match.start()
    return len(body)


def ensure_sections(body: str, intuition: str, history: str) -> tuple[str, bool]:
    has_intuition = f"## {INTUITION_HEADING}" in body
    has_history = f"## {HISTORY_HEADING}" in body
    if has_intuition and has_history:
        return body, False

    blocks: list[str] = []
    if not has_intuition:
        blocks.append(f"## {INTUITION_HEADING}\n{intuition}\n")
    if not has_history:
        blocks.append(f"## {HISTORY_HEADING}\n{history}\n")
    insertion = "\n".join(blocks).strip() + "\n\n"
    offset = find_insert_offset(body)
    updated = body[:offset].rstrip() + "\n\n" + insertion + body[offset:].lstrip()
    return updated, True


def process_file(path: Path, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    raw_frontmatter, body = parse_frontmatter(text)
    has_intuition = f"## {INTUITION_HEADING}" in body
    has_history = f"## {HISTORY_HEADING}" in body
    if has_intuition and has_history:
        return False
    frontmatter = parse_frontmatter_data(raw_frontmatter)
    title = frontmatter.get("title", path.stem).strip() or path.stem
    folder = path.parent.name

    if folder == "00_maps":
        intuition = MAP_INTUITION[title]
        history = MAP_HISTORY[title]
    elif folder == "04_experiments":
        intuition = EXPERIMENT_INTUITION[title]
        history = EXPERIMENT_HISTORY[title]
    else:
        return False

    new_body, changed = ensure_sections(body, intuition, history)
    if not changed:
        return False
    if dry_run:
        return True

    final = f"---\n{raw_frontmatter}\n---\n{new_body}" if raw_frontmatter else new_body
    path.write_text(final, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill missing standard sections for remaining map and experiment notes.")
    parser.add_argument("--vault", help="Override vault path")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--relative-path", help="Process only one note relative to vault root")
    args = parser.parse_args()

    vault = resolve_vault_path(args.vault)
    changed = 0
    matched = 0
    if args.relative_path:
        path = vault / args.relative_path
        matched = 1
        if process_file(path, args.dry_run):
            changed = 1
        print(f"matched={matched}")
        print(f"changed={changed}")
        print(f"dry_run={args.dry_run}")
        return

    for folder in ("00_maps", "04_experiments"):
        folder_path = vault / folder
        if not folder_path.exists():
            continue
        for path in sorted(folder_path.glob("*.md")):
            matched += 1
            if process_file(path, args.dry_run):
                changed += 1
    print(f"matched={matched}")
    print(f"changed={changed}")
    print(f"dry_run={args.dry_run}")


if __name__ == "__main__":
    main()
