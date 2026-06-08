#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from kb_paths import resolve_vault_path


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
TARGET_HEADING = "推導"
INSERT_BEFORE = "幾何意義"


DERIVATIONS: dict[str, str] = {
    "δ函數": "δ函數可以從『把面積固定在 1、寬度趨近 0、高度趨近無限大』的函數列極限來理解，例如高斯函數列或矩形脈衝列。真正被保留下來的不是點值，而是它在積分中抽取函數局部值的分佈性質，這也是它在場論與訊號分析中有意義的原因。",
    "三角函數": "三角函數可以先由直角三角形定義出發，再推廣到單位圓參數化，最後進入複指數形式 $e^{i\\theta}=\\cos\\theta+i\\sin\\theta$。這條推導路徑把幾何比例、旋轉運動與週期解統一起來，說明它們不是零散公式，而是同一套結構的不同面向。",
    "偏導數": "偏導數是從多變量函數中，固定其他變量不動，只觀察單一方向微小改變所得到的局部變化率。這個定義把一維導數自然推廣到高維空間，也為梯度、散度與旋度等後續工具提供了最底層的局部線性近似。",
    "傅立葉分析": "傅立葉分析的核心推導是把足夠好的函數展開為一組正交基底的線性組合。對週期函數，這組基底是正弦與餘弦；進一步在複指數表示下，頻率分量的投影係數便可由內積直接求出，從而把時間或空間結構轉成頻譜結構。",
    "內積": "內積可由歐氏空間中的長度與夾角關係反推出來，要求它同時滿足雙線性、對稱性與正定性。這使得『長度』與『正交』不再依賴圖像直觀，而能被推廣到抽象向量空間與函數空間中。",
    "向量": "向量最初可由位移與平行四邊形法則出發，逐步抽象成同時具有大小、方向且可線性相加的對象。這個抽象化步驟讓向量不再侷限於幾何箭頭，而能統一描述速度、力、場與態空間元素。",
    "向量微積分總論": "向量微積分是把偏導數與向量場結合後得到的一整套局部分析語言。從純量場的梯度，到向量場的散度與旋度，再到面積分與體積分，它的推導脈絡其實就是局部變化如何累積成整體守恆與環流結構。",
    "外積": "外積可由『找出同時垂直於兩向量且大小等於平行四邊形面積』這個需求導出。利用基底展開與行列式形式，外積成為三維空間中同時編碼方向性與面積量測的工具，也因此在力矩與角動量中自然出現。",
    "導數": "導數是由割線斜率在兩點逼近同一點時的極限得到的局部變化率。這個極限觀點把『變化快慢』嚴格化，也讓線性近似、微分方程與最值問題都能以同一套語言處理。",
    "張量": "張量可從標量、向量與線性映射的推廣來理解，核心要求是它在座標變換下仍保有一致的多線性結構。這意味著張量不是『很多數字排成表格』而已，而是能獨立於特定座標系描述物理關係的幾何對象。",
    "微分方程": "微分方程是把未知函數與它的導數放在同一條關係式裡，藉此直接描述系統如何演化。它的推導基礎來自局部變化率與守恆律：一旦知道變化規則，便能藉積分或邊界條件重建整體解。",
    "指數函數": "指數函數可以從『函數等於自身導數』這個性質導出，也可以從複利或連續增長極限建立。這使它成為描述線性成長、衰減、波動複表示與統計權重的自然工具，而不只是計算上的方便函數。",
    "散度": "散度可由一個極小體積邊界上的淨通量除以體積，在體積趨近零時的極限定義得到。這個推導把『某點附近是不是在往外湧出』變成精確的局部量，也因此和守恆方程與源項描述直接相連。",
    "旋度": "旋度可由單位面積上的環流在面積趨近零時的極限導出，量化向量場局部的旋轉傾向。這使得『繞圈感』不再只是圖像直覺，而能成為分析流體渦旋與電磁感應的可計算量。",
    "梯度": "梯度由偏導數組成，推導上來自多變量函數的一階線性近似。它之所以重要，是因為它不只給出各方向變化率，還指出函數增加最快的方向，並把純量場的局部結構轉成向量形式。",
    "機率與統計": "機率與統計的推導核心，是從樣本空間與事件機率出發，再用期望值、變異數與分佈函數去刻畫大量隨機結果的整體規律。這套結構讓單次不可預測的現象，仍能在集合層次形成穩定可檢驗的模型。",
    "泰勒展開": "泰勒展開來自反覆匹配函數在某點的各階導數，將原函數用多項式局部逼近。它的意義不只在計算，而在於把複雜函數分解成各階局部資訊，讓近似、擾動與線性化分析有了統一出發點。",
    "矩陣": "矩陣可以從線性方程組的係數表，進一步抽象成線性映射在某組基底下的表示。這個推導把代數計算、空間變換與本徵問題收進同一個框架，因此在物理中幾乎無處不在。",
    "積分": "積分可由黎曼和極限導出，也就是把區間切成很多小段、各段貢獻加總，再令切分無限細。這個推導把面積、累積量與反微分之間的關係統一起來，也讓局部變化能回推出整體結果。",
    "線性代數總覽": "線性代數的推導主軸，是從向量加法與純量乘法出發，逐步建立基底、維度、線性映射、矩陣表示與本徵結構。它之所以成為物理核心語言，正是因為大量理論都可被重寫成線性空間中的結構問題。",
    "群論基礎": "群論由一組元素及其封閉運算出發，要求滿足結合律、單位元與反元素。這套極簡公理之所以強大，是因為它能把對稱操作抽象化，讓旋轉、平移、置換與規範變換都納入同一理論框架。",
    "自然對數": "自然對數可定義為 \u222b_1^x 1/t dt，也可視為指數函數的反函數。這條推導使它天然滿足加法轉乘法、微分簡潔等性質，因此在連續成長、熵、配分函數與尺度分析中極為自然。",
    "複數": "複數由引入 $i^2=-1$ 來封閉多項式方程的解空間，接著又能被解釋為平面上的點與旋轉縮放操作。這使它不只是代數補丁，而是描述振動、相位與量子振幅的基本語言。",
    "變分法": "變分法的推導從『在所有可能路徑中找出使某個泛函極值的那條路徑』出發。對作用量做微小變化並要求一階變分為零，就得到歐拉-拉格朗日方程，這也是現代理論物理大量方程的共同來源。",
    "面積分": "面積分是把曲面切成無數微小面元，對每個面元上的場量做加總，再取極限得到的。對純量場它累積面上分布量，對向量場則累積穿越曲面的通量，因此是局部場與整體幾何邊界之間的標準橋樑。",
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


def ensure_derivation_section(body: str, content: str) -> tuple[str, bool]:
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
    content = DERIVATIONS.get(title)
    if not content:
        return False
    new_body, changed = ensure_derivation_section(body, content)
    if not changed:
        return False
    if dry_run:
        return True
    final = f"---\n{raw_frontmatter}\n---\n{new_body}" if raw_frontmatter else new_body
    path.write_text(final, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill missing 推導 sections for mathematical tool notes.")
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
    tool_dir = vault / "05_mathematical_tools"
    for path in sorted(tool_dir.glob("*.md")):
        title = path.stem
        if title not in DERIVATIONS:
            continue
        matched += 1
        if process_file(path, args.dry_run):
            changed += 1
    print(f"matched={matched}")
    print(f"changed={changed}")
    print(f"dry_run={args.dry_run}")


if __name__ == "__main__":
    main()
