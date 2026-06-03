#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from kb_paths import resolve_vault_path


SECTION_RE = re.compile(r"^(##)\s+(.+)$", re.MULTILINE)
INTUITION_HEADING = "物理直覺"
HISTORY_HEADING = "歷史背景"
ANCHOR_KEYWORDS = ("常見誤解", "相關連結", "相關概念", "延伸閱讀", "相關頁面", "問題", "練習")


@dataclass
class NoteContext:
    path: Path
    relative_path: Path
    title: str
    note_type: str
    domain: str
    summary: str
    frontmatter: dict[str, object]


def parse_frontmatter(text: str) -> tuple[str, str]:
    text = text.lstrip("\ufeff")
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 5 :]


def parse_frontmatter_data(raw: str) -> dict[str, object]:
    data: dict[str, object] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            items = [part.strip().strip("'\"") for part in value[1:-1].split(",") if part.strip()]
            data[key] = items
        else:
            data[key] = value.strip("'\"")
    return data


def choose(title: str, options: list[str]) -> str:
    if not options:
        return ""
    seed = sum(ord(ch) for ch in title)
    return options[seed % len(options)]


def clean_links(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        text = str(item).strip()
        if text.startswith("[[") and text.endswith("]]"):
            text = text[2:-2]
        text = text.split("|", 1)[0].strip()
        if text:
            result.append(text)
    return result


def infer_domain(note_type: str, title: str, relative_path: Path, frontmatter: dict[str, object]) -> str:
    domain = str(frontmatter.get("domain", "")).strip()
    if domain:
        return domain
    if note_type == "map":
        title_map = {
            "力學總覽": "力學",
            "熱學與熱力學總覽": "熱學與熱力學",
            "振動與波動總覽": "振動與波動",
            "電磁學總覽": "電磁學",
            "光學總覽": "光學",
            "近代物理總覽": "近代物理",
            "流體力學總覽": "流體力學",
            "數學工具總覽": "數學工具",
            "力學知識地圖": "力學",
            "熱學與熱力學知識地圖": "熱學與熱力學",
            "振動與波動知識地圖": "振動與波動",
            "電磁學知識地圖": "電磁學",
            "光學知識地圖": "光學",
            "近代物理知識地圖": "近代物理",
            "流體力學知識地圖": "流體力學",
            "數學工具知識地圖": "數學工具",
        }
        return title_map.get(title, "未分類")
    if relative_path.parts:
        folder = relative_path.parts[0]
        folder_map = {
            "00_maps": "未分類",
            "01_laws": "力學",
            "02_concepts": "未分類",
            "03_quantities": "未分類",
            "04_experiments": "實驗",
            "04_maps": "未分類",
            "05_mathematical_tools": "數學工具",
            "06_experiments": "實驗",
        }
        return folder_map.get(folder, folder)
    return "未分類"


def relation_clause(ctx: NoteContext) -> str:
    pool = []
    pool.extend(clean_links(ctx.frontmatter.get("prerequisites", [])))
    pool.extend(clean_links(ctx.frontmatter.get("related_concepts", [])))
    pool.extend(clean_links(ctx.frontmatter.get("related_quantities", [])))
    pool = [item for item in pool if item and item != ctx.title]
    deduped: list[str] = []
    seen: set[str] = set()
    for item in pool:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    if not deduped:
        return ""
    if len(deduped) == 1:
        return f"把它和 [[{deduped[0]}]] 一起看，直覺會立刻清楚很多。"
    return f"它真正的手感，通常要連同 [[{deduped[0]}]] 和 [[{deduped[1]}]] 一起看才會穩。"


def domain_clause(domain: str) -> str:
    clauses = {
        "力學": "在力學裡，關鍵不是把公式背下來，而是先分清楚系統在交換什麼、約束在哪裡。",
        "熱學與熱力學": "在熱學裡，最容易失真的是把微觀雜亂錯看成宏觀無規律；其實恰好相反，宏觀量正是從大量粒子的統計穩定性冒出來的。",
        "振動與波動": "在波動主題裡，真正要抓的是局部擾動如何靠耦合把影響傳出去，而不是只盯著單一位置上下晃動。",
        "電磁學": "在電磁學裡，很多困惑都來自把場誤看成遠距離神秘作用；一旦改成『空間每一點都有狀態』，整體會順得多。",
        "光學": "在光學裡，幾何圖像和波動圖像都是真的，只是各自抓住不同尺度下最有用的近似。",
        "流體力學": "在流體問題裡，直覺的核心通常不是某一顆粒子怎麼跑，而是流線、壓差與守恆怎麼共同鎖住整體行為。",
        "近代物理": "在近代物理裡，直覺常常必須先放棄經典日常圖像，再建立一套新的可操作理解。",
        "數學工具": "這個主題的價值不在於形式漂亮，而在於它讓原本難以追蹤的物理關係變得可計算、可比較。",
        "未分類": "這個主題最值得先抓住的是它在整張圖裡扮演什麼角色，而不是急著把每個術語都逐字翻成公式。",
    }
    return clauses.get(domain, clauses["未分類"])


def intuition_for_law(ctx: NoteContext) -> str:
    lead = choose(
        ctx.title,
        [
            f"{ctx.title} 的重點不是宣告一條權威規則，而是把系統在什麼條件下會出現什麼回應說清楚。",
            f"讀 {ctx.title} 時，最有用的問題不是『公式怎麼寫』，而是『什麼量在推動、什麼量在回應』。",
            f"{ctx.title} 真正提供的是因果骨架：哪些條件一旦成立，哪些現象就會跟著發生。",
        ],
    )
    summary_line = f"這頁談的是：{ctx.summary}" if ctx.summary else ""
    return " ".join(part for part in [lead, domain_clause(ctx.domain), summary_line, relation_clause(ctx)] if part)


def intuition_for_quantity(ctx: NoteContext) -> str:
    lead = choose(
        ctx.title,
        [
            f"{ctx.title} 不是單位表上的一格名稱，而是拿來描述某種可比較、可累積、可轉換的物理特徵。",
            f"把 {ctx.title} 當成『量測世界的一把尺』會比把它當成孤立名詞更準確。",
            f"{ctx.title} 的存在價值，在於它讓原本只憑感覺描述的差異，變成能夠精確比較的量。",
        ],
    )
    return " ".join(part for part in [lead, domain_clause(ctx.domain), relation_clause(ctx)] if part)


def intuition_for_concept(ctx: NoteContext) -> str:
    lead = choose(
        ctx.title,
        [
            f"{ctx.title} 這類概念的價值，在於它替一堆分散現象提供共同語言。",
            f"{ctx.title} 不是為了命名而命名；它是在壓縮經驗，把多個看似不相干的例子收斂成同一種結構。",
            f"真正理解 {ctx.title}，通常代表你已經不再只會描述現象，而是開始看見現象背後的組織方式。",
        ],
    )
    return " ".join(part for part in [lead, domain_clause(ctx.domain), relation_clause(ctx)] if part)


def intuition_for_map(ctx: NoteContext) -> str:
    return " ".join(
        [
            f"{ctx.title} 不只是索引頁，它更像是閱讀順序與概念骨架的壓縮圖。",
            "看這類頁面時，不要把每個節點都視為同等重要；先抓主幹，再看哪些頁面是支撐概念、哪些頁面是應用延伸。",
            "如果局部內容看起來太碎，回到這張地圖重新定位，通常比在單頁裡硬啃更有效。",
        ]
    )


def intuition_for_experiment(ctx: NoteContext) -> str:
    return " ".join(
        [
            f"{ctx.title} 的意義不只是『做出某個結果』，而是把抽象概念壓到儀器、操作、誤差與觀察之中。",
            "實驗最有教育性的部分，往往不是結論本身，而是你會被迫面對哪些量能控制、哪些量只能估計、哪些偏差其實來自模型假設。",
        ]
    )


def intuition_for_math_tool(ctx: NoteContext) -> str:
    return " ".join(
        [
            f"{ctx.title} 的角色比較像翻譯器：它把物理系統的關係翻成可以推演的形式。",
            "如果只把它當作計算技巧，價值會被低估；真正重要的是它讓你看見哪些變化是局部的、哪些約束是整體的。",
        ]
    )


def intuition_text(ctx: NoteContext) -> str:
    if ctx.note_type == "law":
        return intuition_for_law(ctx)
    if ctx.note_type == "quantity":
        return intuition_for_quantity(ctx)
    if ctx.note_type == "concept":
        return intuition_for_concept(ctx)
    if ctx.note_type == "map":
        return intuition_for_map(ctx)
    if ctx.note_type == "experiment":
        return intuition_for_experiment(ctx)
    if ctx.note_type == "mathematical_tool":
        return intuition_for_math_tool(ctx)
    return " ".join(
        [
            f"{ctx.title} 最值得先抓的，不是零碎細節，而是它在整張知識圖裡究竟用來解什麼問題。",
            relation_clause(ctx),
        ]
    ).strip()


HISTORY_BY_NEEDLE: list[tuple[tuple[str, ...], str]] = [
    (("牛頓",), "這條線索直接連到十七世紀的經典力學建構。牛頓的關鍵不是單獨寫下一個公式，而是把天上與地上的運動納入同一套數學框架，讓規律不再只是局部經驗，而成為可普遍外推的理論結構。"),
    (("虎克",), "這個主題和十七世紀對材料伸縮的系統研究有直接關係。虎克代表的不是一句口訣，而是工程世界第一次穩定地把『形變』和『回應』對應起來。"),
    (("歐姆",), "十九世紀電學成熟的關鍵之一，就是把電流、電壓與導體回應的關係穩定量化。歐姆的重要性不在命名，而在於他把原本零散的電路經驗整理成可重複檢驗的比例規律。"),
    (("庫侖",), "庫侖扭秤實驗讓電力不再只是『會吸會斥』的現象描述，而是可測量、可比較的反平方律。這種轉變非常關鍵，因為它把電學正式推向定量科學。"),
    (("高斯",), "高斯定律的歷史價值，在於它把局部場與整體包圍量之間的關係說清楚。這種『由對稱性與積分結構提煉規律』的做法，是十九世紀數學化物理的一個高峰。"),
    (("法拉第",), "法拉第的貢獻不是把數學寫得最漂亮，而是用極強的物理想像力把『場線』『感應』這些後來被數學完整化的觀念先建立起來。沒有這一步，後來的電磁理論很難成形。"),
    (("楞次",), "楞次定律的重要性，在於它替感應現象加入方向性判準。這不只是記號規則，而是能量與因果一致性的表現。"),
    (("安培",), "十九世紀電流與磁作用的系統整理，大幅推動了場論視角的形成。安培這條線索代表的是：磁效應不再只是磁鐵特例，而成為電流分布的普遍後果。"),
    (("馬克士威",), "馬克士威把法拉第的物理圖像、安培與高斯的數學結構統整成一套閉合方程。這不只是整合既有結果，更是首次顯示光本身可以被理解為電磁波。"),
    (("卡諾",), "卡諾的歷史位置非常高，因為他在熱仍被誤認為某種流體的年代，就已經把熱機效率問題抽象成循環與可逆性的結構問題。這一步直接鋪向後來的熱力學第二定律。"),
    (("阿基米德",), "阿基米德代表的不是古代逸聞，而是早期靜力學與流體思想的成熟：浮力、平衡與幾何推理可以用同一套理性方法處理。"),
    (("惠更斯",), "惠更斯的重要性在於他提供了波前觀點，讓反射、折射與後來的波動光學不再只是零碎技巧，而成為同一種幾何－波動圖像的不同投影。"),
]


def history_override(title: str) -> str | None:
    for needles, text in HISTORY_BY_NEEDLE:
        if all(needle in title for needle in needles):
            return text
    return None


def generic_history(ctx: NoteContext) -> str:
    type_line = {
        "law": "這類頁面通常對應到物理學從現象整理走向理論定律的關鍵階段：人們不再只記錄『會發生什麼』，而是追問『在什麼條件下必然這樣發生』。",
        "quantity": "這類量的歷史價值，通常來自量測技術與理論需求一起成熟。只有在可以穩定定義、比較與重現之後，一個量才真正成為物理語言的一部分。",
        "concept": "這類概念往往不是某一天突然發明出來，而是在不同問題累積到一定程度後，被理論整理成一個可反覆使用的框架。",
        "map": "知識地圖這種頁面本身當然不是歷史對象，但它反映的是後見之明：我們已經知道哪些主題彼此糾纏，才有能力把它們重新編排成一條較清楚的閱讀主線。",
        "experiment": "實驗頁面的歷史核心，幾乎都在於『如何把概念落到可操作裝置』。很多理論之所以站穩，靠的不是一句漂亮解釋，而是可重複的觀測安排。",
        "mathematical_tool": "數學工具進入物理，通常不是因為形式優雅，而是因為舊語言已經撐不住新問題的複雜度。工具一旦成熟，物理學能處理的系統種類就會明顯擴張。",
    }.get(ctx.note_type, "這個主題背後通常都有一段從零散經驗、定性圖像到抽象結構的收斂過程。")

    domain_line = {
        "力學": "就歷史脈絡來說，力學是最早被系統數學化的領域之一，因此很多今天看似理所當然的說法，其實都是在天文、工程與日常運動問題長期拉扯下才穩定下來的。",
        "熱學與熱力學": "熱學史特別有意思，因為它清楚展示了物理學如何從感官直覺走向統計與能量觀：熱不再被視為神秘流體，而是和微觀運動、功與可逆性纏在一起。",
        "振動與波動": "波動理論的成熟，來自聲學、弦振動、光學乃至電磁現象的交互逼迫。它不是單一領域內部自然長出的理論，而是多條現象線索最後匯流。",
        "電磁學": "電磁學的歷史非常像拼圖：靜電、電流、磁效應、感應一開始各自分散，直到十九世紀才逐漸被收斂成統一場論。",
        "光學": "光學史之所以重要，在於它多次迫使物理學改變世界觀：從幾何光線，到波動爭論，再到電磁波與量子問題，幾乎每次轉向都牽動整個理論格局。",
        "流體力學": "流體問題一直夾在純理論與工程需求之間，因此它的歷史不只是公式累積，也包含航運、管流、壓力測量與各種實作壓力帶來的逼迫。",
        "近代物理": "近代物理的歷史背景常常帶有斷裂感，因為舊直覺不是被微調，而是被證據一步步逼到必須重建。",
        "數學工具": "數學工具的歷史背景通常不屬於單一物理章節，但它們一旦被吸收進物理，就會重塑整個領域的推理方式。",
        "未分類": "這個主題即使不是教科書中最醒目的章節，也通常處在某條重要理論鏈的中介位置。很多真正有用的理解，往往就是在這些中介頁長出來的。",
    }.get(ctx.domain, "它所在的主題線，反映的是物理學如何一步步把現象壓縮成結構。")

    return " ".join([domain_line, type_line])


def history_text(ctx: NoteContext) -> str:
    return history_override(ctx.title) or generic_history(ctx)


def find_insert_offset(body: str) -> int:
    for match in SECTION_RE.finditer(body):
        heading = match.group(2).strip()
        if any(keyword in heading for keyword in ANCHOR_KEYWORDS):
            return match.start()
    return len(body)


def ensure_sections(body: str, intuition: str, history: str) -> tuple[str, bool]:
    has_intuition = bool(re.search(rf"^##\s+{re.escape(INTUITION_HEADING)}\s*$", body, re.MULTILINE))
    has_history = bool(re.search(rf"^##\s+{re.escape(HISTORY_HEADING)}\s*$", body, re.MULTILINE))
    if has_intuition and has_history:
        return body, False

    sections: list[str] = []
    if not has_intuition:
        sections.append(f"## {INTUITION_HEADING}\n{intuition.strip()}\n")
    if not has_history:
        sections.append(f"## {HISTORY_HEADING}\n{history.strip()}\n")
    block = "\n".join(sections).strip() + "\n\n"
    offset = find_insert_offset(body)
    updated = body[:offset].rstrip() + "\n\n" + block + body[offset:].lstrip()
    return updated, True


def build_context(note_path: Path, vault: Path) -> tuple[NoteContext, str, str]:
    text = note_path.read_text(encoding="utf-8")
    raw_frontmatter, body = parse_frontmatter(text)
    frontmatter = parse_frontmatter_data(raw_frontmatter)
    title = str(frontmatter.get("title", note_path.stem)).strip() or note_path.stem
    note_type = str(frontmatter.get("type", "note")).strip() or "note"
    summary = str(frontmatter.get("summary", "")).strip()
    relative_path = note_path.relative_to(vault)
    domain = infer_domain(note_type, title, relative_path, frontmatter)
    ctx = NoteContext(
        path=note_path,
        relative_path=relative_path,
        title=title,
        note_type=note_type,
        domain=domain,
        summary=summary,
        frontmatter=frontmatter,
    )
    return ctx, raw_frontmatter, body


def should_include(relative_path: Path, folders: list[str]) -> bool:
    if not folders:
        return True
    if not relative_path.parts:
        return False
    return relative_path.parts[0] in folders


def process_file(note_path: Path, vault: Path, dry_run: bool) -> bool:
    ctx, raw_frontmatter, body = build_context(note_path, vault)
    intuition = intuition_text(ctx)
    history = history_text(ctx)
    new_body, changed = ensure_sections(body, intuition, history)
    if not changed:
        return False
    if dry_run:
        return True

    if raw_frontmatter:
        new_text = f"---\n{raw_frontmatter}\n---\n{new_body}"
    else:
        new_text = new_body
    note_path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich notes with physical intuition and historical background sections.")
    parser.add_argument("--vault", help="Override vault path")
    parser.add_argument("--folders", nargs="*", default=[], help="Restrict processing to top-level vault folders like 01_laws")
    parser.add_argument("--limit", type=int, default=0, help="Only process the first N matching notes")
    parser.add_argument("--dry-run", action="store_true", help="Report how many notes would change without writing")
    args = parser.parse_args()

    vault = resolve_vault_path(args.vault)
    matched = 0
    changed = 0
    for note_path in sorted(vault.rglob("*.md")):
        relative_path = note_path.relative_to(vault)
        if not should_include(relative_path, args.folders):
            continue
        matched += 1
        if process_file(note_path, vault, args.dry_run):
            changed += 1
        if args.limit and matched >= args.limit:
            break

    print(f"matched={matched}")
    print(f"changed={changed}")
    print(f"dry_run={args.dry_run}")


if __name__ == "__main__":
    main()
