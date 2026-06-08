#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from apply_weak_model_response import apply_response_to_text, load_schema, make_rename_map, parse_frontmatter
from kb_paths import repo_root, resolve_vault_path


HISTORY_FIXES: dict[str, str] = {
    "偏微分方程": "偏微分方程作為物理語言，是在 Jean le Rond d'Alembert、Joseph Fourier 與 Pierre-Simon Laplace 的工作中逐步成形的。d'Alembert 用它描述振動弦，Fourier 在熱傳導研究中系統化了這類方程，而 Laplace 與 Maxwell 又把它推進到位勢論與電磁學，讓場的局部演化能被統一書寫。",
    "反射": "反射定律的幾何形式在 Euclid 與 Hero of Alexandria 的光學傳統中已經出現，之後又被 Ibn al-Haytham 與 Pierre de Fermat 放進更成熟的視覺與最短時間框架。現代教材中的反射概念，基本上就是把這條古典幾何規則重新安放到波動與電磁理論裡。",
    "低摩擦滑車實驗": "這類低摩擦滑車實驗是近代教學對 Galileo Galilei 與 Isaac Newton 力學問題的實驗化簡版本。Newton 在 1687 年建立運動定律之後，教學裝置逐步朝「盡量減少摩擦、把受力情形做乾淨」的方向發展，滑車與直線軌道正是這條脈絡下的標準器材。",
    "兩滑車碰撞實驗": "兩滑車碰撞實驗的歷史背景直接連到 Christiaan Huygens 對碰撞規律的分析，以及 Isaac Newton 在 1687 年之後對動量框架的系統化。現代教學只是把 17 世紀的碰撞問題搬到低摩擦軌道上，讓守恆律更容易被量測與比較。",
    "功能定理驗證實驗": "功能定理的教學實驗背景來自 19 世紀把牛頓力學改寫成能量語言的努力。Gaspard-Gustave Coriolis 在 1829 年明確整理了做功概念，而後續工程力學把「合力做功等於動能變化」變成標準計算工具，今天的驗證實驗就是這條歷史線的教學版。",
    "反射定律驗證實驗": "反射定律驗證實驗是在重演一條歷史極長的光學規則：從 Euclid、Hero of Alexandria 到 Ibn al-Haytham，都曾把入射與反射的角度關係當成核心問題。現代實驗課做的事，其實就是把這條古典規則用量角器、光源與鏡面重新變成可操作的量測程序。",
    "天平": "天平是最古老的量測工具之一，而近代實驗室中的精密天平則在 Antoine Lavoisier 那一代獲得方法論上的核心地位。18 世紀化學之所以能從質性描述走向守恆定量，很大一部分就靠這類稱量儀器把『質量差多少』變成可重複的實驗事實。",
    "安培力實驗": "安培力實驗的歷史背景集中在 1820 年前後的電磁學爆發期。Hans Christian Oersted 先顯示電流與磁作用有關，André-Marie Ampère 隨後建立電流力學框架，Michael Faraday 又在 1821 年做出電磁旋轉裝置，這些工作共同鋪出今天教材中的安培力實驗。",
    "密立根油滴實驗": "密立根油滴實驗由 Robert Millikan 在 1909 至 1911 年間完成，目的就是量出基本電荷並驗證電荷量子化。它之所以成為經典，不只是因為數值量得漂亮，而是因為它把『電荷不是連續流體』這件事變成了可直接比對的量測結果。",
    "小車軌道實驗": "小車軌道實驗屬於近代教學對 Galileo Galilei 慣性問題與 Isaac Newton 運動定律的標準化重演。把車體放上近似一維的軌道，是為了把受力與運動關係做乾淨，讓 1687 年之後的力學框架能在教學現場被直接檢驗。",
    "打點計時器": "打點計時器的教學意義，可以看成是把 Galileo Galilei 對時間量測的困難，換成 20 世紀電學儀器的自動記錄版本。早期運動學實驗一直卡在『怎麼可靠量到短時間』，而這類等時打點裝置就是把那個問題工程化之後的答案。",
    "扭秤實驗": "扭秤在物理史上最著名的用途來自 Charles-Augustin de Coulomb 與 Henry Cavendish。Coulomb 在 1785 年用扭秤研究電力定律，Cavendish 在 1798 年則用相關裝置量測萬有引力尺度；今天教材中的扭秤實驗，承接的正是這條『用微小扭轉換取微小力』的歷史方法。",
    "文丘里管實驗": "文丘里管以 Giovanni Battista Venturi 命名，他在 1797 年分析了流體通過縮窄管道時速度與壓力的變化。現代實驗課把這個裝置留下來，不是因為它外形特殊，而是因為它把 Bernoulli 式的流動關係變成一個可以直接讀壓差的教學場景。",
    "氣墊軌道碰撞實驗": "氣墊軌道碰撞實驗是 20 世紀教學器材對 Christiaan Huygens 碰撞研究與 Isaac Newton 動量框架的工程化版本。利用氣墊減少摩擦，目的就是把碰撞前後的守恆關係做得更接近理想條件，方便直接測量與比較。",
    "法拉第冰桶實驗": "法拉第冰桶實驗與 Michael Faraday 在 1840 年代的靜電研究直接相關。Faraday 用這類設計說明導體內部與表面的電荷分布特性，並把『電荷只留在外表面』這件事做成極具說服力的演示，後來成為電學教學中的經典實驗。",
    "滑軌能量轉換實驗": "滑軌能量轉換實驗的背景來自 19 世紀能量概念的成熟。從 James Prescott Joule 的等效工作，到工程力學把動能、位能與耗散整理成統一帳本，這類實驗的目的就是把抽象的能量守恆改寫成可見的速度變化與高度變化。",
    "相空間軌跡模擬": "相空間軌跡的歷史背景主要連到 Henri Poincaré 在 19 世紀末對動力系統幾何結構的重寫。Poincaré 不再只問解出一條軌道，而是問整個相空間如何分區、哪些軌道靠近哪些集合；今天的相空間模擬正是這套視角的教學延伸。",
    "赫茲電磁波實驗": "Heinrich Hertz 在 1887 至 1888 年間用火花間隙實驗明確產生並偵測到電磁波，直接支持了 James Clerk Maxwell 的理論預測。這個實驗的重要性在於它把方程組中的波動解，變成了實驗室裡真的能發射、反射與接收的對象。",
    "轉動慣量量測實驗": "轉動慣量量測實驗承接的是 Leonhard Euler 以降的剛體轉動理論。當 18 世紀力學開始把平移與轉動分開處理之後，『質量如何分布』便成了決定角加速度的核心量；現代量測實驗的任務，就是把這個理論量從幾何與時間資料中反推出來。",
    "運動感測器": "運動感測器是 20 世紀電子量測技術進入教學實驗的產物，但它處理的仍然是 Galileo Galilei 與 Isaac Newton 留下的老問題：位置、速度與時間如何被更準確地記錄。超音波或紅外線感測只是把原本人工讀表的步驟，自動化成高頻取樣的資料流。",
    "雙狹縫實驗": "雙狹縫實驗的歷史核心來自 Thomas Young 在 1801 年對光干涉的展示。它之所以重要，是因為 Young 用條紋結構逼迫當時的光學界承認波動圖像的解釋力；後來在量子論中，同一實驗又被重新解讀為概率振幅與相位疊加的代表案例。",
    "電導率量測實驗": "電導率量測實驗的歷史背景連到 Georg Ohm、Michael Faraday 與 Friedrich Kohlrausch 這條線。Ohm 奠定了導電關係的基本框架，Faraday 把電與化學結合起來，而 Kohlrausch 在 19 世紀進一步把溶液導電做成精密量測問題，讓電導率成為可比較的物性量。",
    "電路驗證實驗": "電路驗證實驗的理論背景主要來自 Georg Ohm 在 1827 年提出的關係式，以及 Gustav Kirchhoff 在 1845 年整理出的節點與迴路規則。現代教學實驗做的事，就是把這兩套規則放到實際元件上，檢查理想公式和真實量測能對到什麼程度。",
    "靜電場模擬實驗": "靜電場模擬實驗的歷史背景可追到 Michael Faraday 在 1830 至 1840 年代推進的場線觀念。Faraday 把原本容易被理解成超距作用的電現象，改寫成空間中每一點都有方向結構的場；模擬實驗就是讓這種場的幾何形狀變得可視化。",
    "三角函數": "三角函數的歷史來源很早，從 Hipparchus 到 Claudius Ptolemy 的天文與幾何計算，都在處理角度與弦長的系統關係。到了近代，Leonhard Euler 把它們放進解析函數與複數框架，三角函數才從表格工具升級成現代數學與物理的標準語言。",
    "偏導數": "偏導數是在 Gottfried Wilhelm Leibniz 與 Leonhard Euler 所開展的微積分語言中逐漸成熟的。當研究對象從單一變數函數擴展到多變數場之後，就必須區分『只改一個方向、其他先固定』的變化率，而偏導數正是這種局部比較的標準工具。",
    "內積": "內積的現代用途建立在 René Descartes 的座標幾何與 Josiah Willard Gibbs 的向量分析傳統上。它之所以重要，不只是因為能算角度，而是因為它把投影、正交與功的計算壓成統一代數形式，成為物理中最常用的幾何運算之一。",
    "向量": "向量作為現代物理語言，主要在 William Rowan Hamilton、Josiah Willard Gibbs 與 Oliver Heaviside 的工作中定型。Hamilton 的四元數提供了早期方向量代數，Gibbs 和 Heaviside 則把更適合物理計算的向量形式抽出來，變成今天教材的標準記號。",
    "外積": "外積是 19 世紀向量分析成熟後留下來的核心運算，與 Josiah Willard Gibbs、Oliver Heaviside 的記號整理密切相關。它被保留下來，是因為面積、力矩與磁力這些物理量都需要一種能同時編碼大小與方向垂直性的運算。",
    "導數": "導數作為現代概念，出自 Isaac Newton 與 Gottfried Wilhelm Leibniz 各自建立的微積分框架。Newton 關心運動與瞬時變化率，Leibniz 則把微分寫成可操作的符號語言；後來的物理學幾乎整個建立在這種『局部變化如何被量化』的能力上。",
    "散度": "散度的歷史背景連到 Carl Friedrich Gauss 的通量觀點，以及後來場論與流體力學的發展。它之所以成為標準工具，是因為它能把『某點附近像源頭還是匯點』這件事寫成局部數量，並與整體通量透過高斯定理連起來。",
    "旋度": "旋度作為局部旋轉強度的工具，與 George Stokes、William Thomson 以及 James Clerk Maxwell 的數學物理傳統密切相關。它把原本只能憑流線圖描述的環流現象，壓縮成每一點都可定義的局部量，對流體與電磁學都極關鍵。",
    "梯度": "梯度概念是在多變數微積分與解析力學中逐步成熟的，與 Joseph-Louis Lagrange、William Rowan Hamilton 一系的工作有關。它的重要性在於：一旦你知道標量場在各方向的變化率，就能把『最陡上升方向』與力、通量、穩定性分析直接接起來。",
    "機率與統計": "機率與統計的近代基礎可追到 Blaise Pascal 與 Pierre de Fermat 的通信，之後又由 Pierre-Simon Laplace 與 Carl Friedrich Gauss 大幅推進。它之所以進入物理核心，不只是為了處理誤差，更是因為大量自由度系統根本只能以分布與平均來理解。",
    "矩陣": "矩陣在 19 世紀由 Arthur Cayley 與 James Joseph Sylvester 系統化成獨立對象。它原本是處理線性方程與變換的工具，但很快就變成多自由度系統、正交變換與量子力學算符語言的核心骨架。",
    "積分": "積分與導數一樣，屬於 Newton 與 Leibniz 建立的微積分革命的一部分，之後又由 Augustin-Louis Cauchy 與 Bernhard Riemann 進一步嚴格化。物理裡之所以離不開積分，是因為總量、累積效應與連續分布幾乎都要靠它來組裝。",
    "複數": "複數最早在解代數方程時被迫登場，Gerolamo Cardano 與 Rafael Bombelli 都是關鍵人物；到 Leonhard Euler 與 Carl Friedrich Gauss 之後，它才真正變成穩固的數學語言。物理學後來大量使用複數，正是因為它能把振盪、相位與線性算子壓進同一個計算框架。",
    "面積分": "面積分的歷史背景主要與 Carl Friedrich Gauss 的通量觀點以及 George Stokes 的積分定理傳統相連。它之所以重要，是因為很多物理量不是沿線累積，而是穿過一整個面流出或流入；沒有面積分，場論中的守恆律就很難寫成精確公式。",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_targets(audit_json: Path) -> list[str]:
    audit = load_json(audit_json)
    return [item["message"].split(":", 1)[0] for item in audit.get("issues", []) if item.get("category") == "history_not_concrete"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill concrete history sections for notes flagged by history_not_concrete.")
    parser.add_argument("--vault", help="Override vault path")
    parser.add_argument("--audit-json", default="tmp/audit_results_after_final_banned_cleanup.json", help="Audit JSON path")
    parser.add_argument("--schema-dir", help="Schema directory. Defaults to repo_root()/schema")
    parser.add_argument("--write", action="store_true", help="Write changes back to the vault")
    args = parser.parse_args()

    repo = repo_root()
    vault = resolve_vault_path(args.vault)
    schema_dir = Path(args.schema_dir).resolve() if args.schema_dir else repo / "schema"
    audit_json = (repo / args.audit_json).resolve()
    schema = load_schema(schema_dir)

    changed = 0
    missing: list[str] = []

    for rel in collect_targets(audit_json):
        note_path = (vault / rel).resolve()
        text = note_path.read_text(encoding="utf-8")
        frontmatter, _body = parse_frontmatter(text)
        title = str(frontmatter.get("title", note_path.stem)).strip()
        replacement = HISTORY_FIXES.get(title)
        if not replacement:
            missing.append(title)
            continue
        note_type = str(frontmatter.get("type", "")).strip()
        rename_map = make_rename_map(schema["renames"]["rename_rules"].get(note_type, []))
        updated_text, _matched = apply_response_to_text(
            text,
            note_type=note_type,
            target_section="歷史背景",
            replacement_body=replacement,
            rename_map=rename_map,
        )
        if updated_text != text:
            changed += 1
            if args.write:
                note_path.write_text(updated_text, encoding="utf-8")

    if missing:
        raise SystemExit(f"Missing history fixes for: {', '.join(missing)}")

    print("History concreteness fill summary")
    print(f"- audit json: {audit_json}")
    print(f"- vault: {vault}")
    print(f"- changed: {changed}")
    print(f"- write: {args.write}")


if __name__ == "__main__":
    main()
