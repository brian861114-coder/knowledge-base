#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from kb_paths import resolve_vault_path


TARGETS: dict[str, dict[str, object]] = {
    "薛丁格方程": {
        "frontmatter": {
            "prerequisites": ["[[德布羅意波]]", "[[複數]]", "[[偏導數]]", "[[邊界條件]]"],
            "related_laws": [],
            "related_quantities": ["[[能量]]", "[[動量]]"],
            "related_concepts": [
                "[[德布羅意波]]",
                "[[量子化]]",
                "[[本徵態]]",
                "[[機率振幅]]",
                "[[波函數]]",
                "[[可觀測量]]",
                "[[離散能階]]",
                "[[連續譜]]",
                "[[正規化]]",
                "[[邊界條件]]",
                "[[光電效應]]",
                "[[黑體輻射]]",
            ],
            "math_tools": ["[[偏導數]]", "[[複數]]", "[[矩陣]]", "[[積分]]"],
        },
        "connection_block": """## 與上下游概念的連接
薛丁格方程不是孤立公式，而是把量子橋接層整個綁起來的核心頁：

- [[德布羅意波]] 把物質的波動性拉進來
- [[波函數]] 指定這條方程真正演化的對象
- [[機率振幅]] 與 [[正規化]] 把解和可測機率接起來
- [[本徵態]] 與 [[可觀測量]] 說明量測時哪些狀態與數值可被穩定抽出
- [[邊界條件]] 決定哪些解可接受，進而逼出 [[離散能階]]
- 若系統不再是束縛態，則自然轉到 [[連續譜]]
- 往上游看，[[黑體輻射]]、[[光電效應]]、[[量子化]] 共同逼出這套語言
""",
    },
    "光電效應": {
        "frontmatter": {
            "prerequisites": ["[[電磁波]]", "[[能量]]", "[[基本電荷]]"],
            "related_laws": [],
            "related_quantities": ["[[動量]]", "[[基本電荷]]"],
            "related_concepts": [
                "[[黑體輻射]]",
                "[[德布羅意波]]",
                "[[薛丁格方程]]",
                "[[波粒二象性]]",
                "[[量子化]]",
            ],
            "math_tools": ["[[積分]]"],
        },
        "connection_block": """## 與上下游概念的連接
光電效應不是單一實驗插曲，而是量子主線的硬證據之一：

- 它和 [[黑體輻射]] 一起逼出 [[量子化]]，說明能量交換不能再假裝連續
- 它把光的粒子式能量交換釘死，因此直接支撐 [[波粒二象性]]
- 逸出電子涉及 [[基本電荷]] 這個離散基準，讓量子結構不只停在抽象能量包
- 往下游，這些觀念才會被 [[德布羅意波]] 推廣到物質，再由 [[薛丁格方程]] 寫成可計算理論
""",
    },
    "黑體輻射": {
        "frontmatter": {
            "prerequisites": ["[[熱]]", "[[電磁波]]", "[[統計物理]]", "[[熱平衡]]"],
            "related_laws": [],
            "related_quantities": ["[[能量]]"],
            "related_concepts": [
                "[[光電效應]]",
                "[[德布羅意波]]",
                "[[薛丁格方程]]",
                "[[量子化]]",
                "[[模態]]",
                "[[熱平衡]]",
            ],
            "math_tools": ["[[積分]]", "[[機率與統計]]"],
        },
        "connection_block": """## 與上下游概念的連接
黑體輻射這頁真正要接起來的是熱學、波動與量子論：

- [[熱平衡]] 指定黑體頻譜必須對應穩定的熱狀態
- 空腔中的 [[模態]] 決定可被計數的電磁振動型態
- [[統計物理]] 負責把模態和能量分布算成頻譜
- 一旦高頻端崩潰，[[量子化]] 就不再是裝飾，而是必要條件
- 這條線再往下游接到 [[光電效應]]、[[德布羅意波]]，最後接到 [[薛丁格方程]]
""",
    },
    "德布羅意波": {
        "frontmatter": {
            "prerequisites": ["[[光電效應]]", "[[動量]]", "[[波粒二象性]]"],
            "related_laws": [],
            "related_quantities": ["[[動量]]"],
            "related_concepts": [
                "[[薛丁格方程]]",
                "[[黑體輻射]]",
                "[[干涉]]",
                "[[波粒二象性]]",
                "[[波函數]]",
                "[[機率振幅]]",
                "[[量子化]]",
            ],
            "math_tools": ["[[複數]]"],
        },
        "connection_block": """## 與上下游概念的連接
德布羅意波的工作，就是把量子主線從光推到物質：

- 上游先由 [[光電效應]] 與 [[波粒二象性]] 打掉單純粒子圖像
- 德布羅意關係把 [[動量]] 直接翻成波長，因此替 [[波函數]] 語言鋪路
- 一旦進入波動描述，[[機率振幅]] 與干涉現象就不再是額外附錄
- 在束縛系統裡，波動條件會接到 [[量子化]]；在動力學上則接到 [[薛丁格方程]]
""",
    },
    "電場": {
        "frontmatter": {
            "prerequisites": ["[[電荷]]", "[[向量]]"],
            "related_laws": ["[[庫侖定律]]", "[[高斯定律]]", "[[麥克斯威方程組]]"],
            "related_quantities": ["[[電荷]]", "[[電位差]]"],
            "related_concepts": [
                "[[電位]]",
                "[[電力線]]",
                "[[場論觀點]]",
                "[[靜電平衡]]",
                "[[電容器]]",
            ],
            "math_tools": ["[[向量]]", "[[積分]]", "[[梯度]]"],
        },
        "connection_block": """## 與上下游概念的連接
電場不是單一章節名詞，而是電磁學主線真正開始工作的地方：

- 往上游，[[庫侖定律]] 給出點電荷來源，[[高斯定律]] 提供高對稱分布的快速計算
- 往下游，線積分會把場轉成 [[電位]] 與 [[電位差]]
- 在導體問題中，[[靜電平衡]] 說明何時場在內部被消去
- 到系統層次時，[[電容器]] 與平行板模型把場、位差與儲能綁成一套
- 再往更一般的描述走，就是 [[場論觀點]] 與 [[麥克斯威方程組]] 的語言
""",
        "section_start": "## 與延伸定理的連接",
        "section_end": "## 先備與延伸連結",
    },
    "電位": {
        "frontmatter": {
            "prerequisites": ["[[電場]]", "[[電荷]]", "[[積分]]"],
            "related_laws": ["[[庫侖定律]]", "[[高斯定律]]"],
            "related_quantities": ["[[電荷]]", "[[電位差]]"],
            "related_concepts": [
                "[[電位能]]",
                "[[等位面]]",
                "[[電通量]]",
                "[[電位差]]",
                "[[靜電平衡]]",
                "[[電容器]]",
            ],
            "math_tools": ["[[積分]]", "[[梯度]]"],
        },
        "connection_block": """## 與上下游概念的連接
電位這頁的角色，是把向量場語言整理成能量與位差語言：

- [[電場]] 給局部受力資訊，沿路積分後才變成 [[電位差]]
- [[等位面]] 與 [[靜電平衡]] 說明哪些區域可視為同一電位結構
- 一旦進到裝置層次，[[電容器]] 和 [[平行板電容器]] 都靠位差來定義儲能能力
- 因此電位不是電場的旁支，而是把場、能量與幾何連起來的中介頁
""",
        "section_start": "## 與延伸定理的連接",
        "section_end": "## 先備與延伸連結",
    },
    "高斯定律": {
        "frontmatter": {
            "prerequisites": ["[[電場]]", "[[電通量]]", "[[面積分]]", "[[梯度]]"],
            "related_laws": ["[[庫侖定律]]", "[[麥克斯威方程組]]"],
            "related_quantities": ["[[電荷]]"],
            "related_concepts": [
                "[[電場]]",
                "[[電通量]]",
                "[[電荷]]",
                "[[場論觀點]]",
                "[[靜電平衡]]",
                "[[電容器]]",
            ],
            "math_tools": ["[[面積分]]", "[[梯度]]", "[[散度]]"],
        },
        "connection_block": """## 與上下游概念的連接
高斯定律的價值，不只是算題省工，而是把場和來源的關係壓成結構公式：

- 它把包圍面上的場流量和內含 [[電荷]] 直接接起來
- 這種寫法本身就是 [[場論觀點]] 的代表，不再靠遠距離拉力圖像硬撐
- 在導體問題裡，[[靜電平衡]] 常和高斯面一起使用，快速推出內部無場與表面帶電
- 在模型系統裡，[[電容器]] 尤其是平行板情況，幾乎就是高斯定律的示範場
- 再往總結走，它會進入 [[麥克斯威方程組]] 成為其中一條基本方程
""",
        "insert_before": "## 先備知識",
    },
    "麥克斯威方程組": {
        "frontmatter": {
            "prerequisites": ["[[高斯定律]]", "[[法拉第定律]]", "[[電場]]", "[[磁場]]"],
            "related_laws": ["[[高斯定律]]", "[[法拉第定律]]"],
            "related_quantities": ["[[能量]]"],
            "related_concepts": [
                "[[電磁波]]",
                "[[交流電]]",
                "[[狹義相對論]]",
                "[[場論觀點]]",
                "[[局域性]]",
                "[[洛侖茲轉換]]",
            ],
            "math_tools": ["[[散度]]", "[[旋度]]", "[[向量]]", "[[偏導數]]"],
        },
        "connection_block": """## 與上下游概念的連接
麥克斯威方程組是電磁學從零碎定律升級成完整理論的收束點：

- [[高斯定律]] 和 [[法拉第定律]] 這些上游頁面，在這裡被統整成同一組場方程
- 它們不是全域口號，而是每一點都成立的局部關係，因此直接體現 [[局域性]]
- 這種寫法就是 [[場論觀點]] 的成熟版本，讓電磁波與場能傳播能被乾淨描述
- 再往近代物理延伸，電磁學的不變結構會接到 [[狹義相對論]] 與 [[洛侖茲轉換]]
""",
        "insert_before": "## 先備知識",
    },
    "拉格朗日力學": {
        "frontmatter": {
            "prerequisites": ["[[能量]]", "[[對稱性]]", "[[偏導數]]", "[[廣義座標]]", "[[作用量]]"],
            "related_laws": ["[[牛頓第二定律]]"],
            "related_quantities": ["[[能量]]"],
            "related_concepts": ["[[廣義座標]]", "[[作用量]]", "[[守恆量]]", "[[狹義相對論]]"],
            "math_tools": ["[[偏導數]]", "[[積分]]", "[[矩陣]]"],
        },
        "connection_block": """## 與上下游概念的連接
拉格朗日力學的強項，是把力學主線從力和軌跡改寫成結構語言：

- [[廣義座標]] 負責把自由度與約束整理成最有效的變數
- [[作用量]] 把整條路徑壓成可比較對象，再由駐值原理選出真實運動
- 一旦系統有對稱性，對應的 [[守恆量]] 就會自然浮出來
- 因此它不是牛頓寫法的修辭版本，而是處理多自由度、約束與相對論問題的主幹工具
""",
    },
    "統計物理": {
        "frontmatter": {
            "prerequisites": ["[[機率與統計]]", "[[熱]]", "[[熱平衡]]"],
            "related_laws": ["[[熱力學第二定律]]", "[[理想氣體方程式]]"],
            "related_quantities": ["[[能量]]", "[[壓力]]", "[[溫度]]"],
            "related_concepts": ["[[熵]]", "[[黑體輻射]]", "[[內能]]", "[[熱平衡]]", "[[量子化]]"],
            "math_tools": ["[[機率與統計]]", "[[積分]]"],
        },
        "connection_block": """## 與上下游概念的連接
統計物理在資料庫裡的真正位置，是熱學和微觀理論的翻譯器：

- [[熱平衡]] 提供分布穩定下來的舞台，沒有它很多公式根本站不住
- [[機率與統計]] 負責把微觀態數與分布算成巨觀平均
- 這才讓 [[熵]]、[[內能]]、[[熱力學第二定律]] 有可追溯的微觀來源
- 再往近代主題走，[[黑體輻射]] 會迫使統計分布接上 [[量子化]]
""",
    },
    "卡諾循環": {
        "frontmatter": {
            "prerequisites": ["[[熱力學第二定律]]", "[[等溫過程]]", "[[絕熱過程]]", "[[熱平衡]]"],
            "related_laws": ["[[熱力學第二定律]]", "[[熱力學第一定律]]"],
            "related_quantities": ["[[能量]]", "[[溫度]]"],
            "related_concepts": ["[[等溫過程]]", "[[絕熱過程]]", "[[熵]]", "[[熱平衡]]"],
            "math_tools": [],
        },
        "connection_block": """## 與上下游概念的連接
卡諾循環不是孤零零的效率公式頁，而是熱學主幹的匯流點：

- [[熱平衡]] 確保高溫與低溫熱庫可以被穩定定義
- [[等溫過程]] 與 [[絕熱過程]] 提供理想可逆循環的四段骨架
- [[熱力學第一定律]] 負責熱與功的記帳
- [[熱力學第二定律]] 與 [[熵]] 則真正給出效率上限
""",
    },
    "平行板電容器": {
        "frontmatter": {
            "prerequisites": ["[[無限平面電場]]", "[[等位面]]", "[[電位]]", "[[電容器]]"],
            "related_laws": ["[[高斯定律]]"],
            "related_quantities": ["[[電荷]]", "[[能量]]", "[[電位差]]"],
            "related_concepts": [
                "[[電位能]]",
                "[[電場能量]]",
                "[[電位]]",
                "[[電通量]]",
                "[[電容器]]",
                "[[電場]]",
                "[[電位差]]",
                "[[靜電平衡]]",
            ],
            "math_tools": ["[[積分]]"],
        },
        "connection_block": """## 與上下游概念的連接
平行板電容器就是把靜電橋接層實體化的模型：

- [[高斯定律]] 負責先求出板間近似均勻的 [[電場]]
- 沿著場積分就得到 [[電位差]]，因此場和位差不是分開兩章
- 一旦把兩板視為整體系統，這頁就直接接到 [[電容器]]
- 板面成為近似 [[等位面]]，也讓 [[靜電平衡]] 的直覺落到可算模型上
- 最後儲存的能量又回流到 [[電場能量]] 與系統層次分析
""",
    },
    "聲波": {
        "frontmatter": {
            "prerequisites": ["[[機械波]]", "[[壓力]]", "[[熱]]"],
            "related_laws": [],
            "related_quantities": ["[[壓力]]", "[[速度]]"],
            "related_concepts": ["[[駐波]]", "[[都卜勒效應]]", "[[共振]]", "[[模態]]", "[[邊界條件]]"],
            "math_tools": ["[[複數]]"],
        },
        "connection_block": """## 與上下游概念的連接
聲波是波動主線往真實介質問題展開的關鍵頁：

- 上游先由 [[機械波]] 給一般波動語言
- 一旦進入管柱、腔體或封閉空間，[[邊界條件]] 會選出可允許的 [[模態]]
- 這些模態若和外界驅動匹配，就會進一步接到 [[共振]]
- 若題目關心傳播中的頻率偏移，則轉到 [[都卜勒效應]]
""",
    },
    "共振": {
        "frontmatter": {
            "prerequisites": ["[[簡諧運動]]", "[[聲波]]", "[[模態]]"],
            "related_laws": [],
            "related_quantities": ["[[能量]]"],
            "related_concepts": ["[[駐波]]", "[[交流電]]", "[[聲波]]", "[[模態]]", "[[邊界條件]]"],
            "math_tools": ["[[複數]]", "[[矩陣]]"],
        },
        "connection_block": """## 與上下游概念的連接
共振真正要接起來的，不只是大振幅，而是系統的本徵結構：

- [[模態]] 指出系統原本偏好的振動型態
- [[邊界條件]] 決定哪些頻率與空間型態能被允許
- 在聲學情境裡，這些結構會直接表現在 [[聲波]] 與 [[駐波]] 問題
- 在其他系統中，同一套選頻邏輯也會延伸到 [[交流電]] 等主題
""",
    },
}


BATCHES = {
    "batch1": ["薛丁格方程", "光電效應", "黑體輻射", "德布羅意波", "電場", "電位", "高斯定律", "麥克斯威方程組"],
    "batch2": ["拉格朗日力學", "統計物理", "卡諾循環", "平行板電容器", "聲波", "共振"],
    "all": list(TARGETS.keys()),
}


def format_list(items: list[str]) -> str:
    return "[" + ", ".join(f'"{item}"' for item in items) + "]"


def replace_frontmatter_value(text: str, key: str, items: list[str]) -> str:
    pattern = rf"(?m)^{re.escape(key)}: .*$"
    replacement = f"{key}: {format_list(items)}"
    new_text, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise ValueError(f"Could not update frontmatter field {key}")
    return new_text


def replace_section(text: str, start_heading: str, end_heading: str, block: str) -> str:
    pattern = re.compile(
        rf"(?s){re.escape(start_heading)}\n.*?(?=\n{re.escape(end_heading)}\n)",
    )
    new_text, count = pattern.subn(block.rstrip(), text, count=1)
    if count != 1:
        # Section not found — insert before end_heading instead
        marker = f"\n{end_heading}\n"
        if marker in text:
            return text.replace(marker, "\n" + block.rstrip() + "\n\n" + end_heading + "\n", 1)
        # Last resort: append before closing
        return text.rstrip() + "\n\n" + block.rstrip() + "\n"
    return new_text


def insert_section_before(text: str, before_heading: str, block: str) -> str:
    marker = f"\n{before_heading}\n"
    if marker not in text:
        raise ValueError(f"Could not insert before {before_heading}")
    return text.replace(marker, "\n" + block.rstrip() + "\n\n" + before_heading + "\n", 1)


def update_note(note_path: Path, config: dict[str, object]) -> None:
    text = note_path.read_text(encoding="utf-8")
    for key, items in config["frontmatter"].items():
        text = replace_frontmatter_value(text, key, items)
    if "insert_before" in config:
        text = insert_section_before(text, str(config["insert_before"]), str(config["connection_block"]))
    else:
        start_heading = str(config.get("section_start", "## 與上下游概念的連接"))
        end_heading = str(config.get("section_end", "## 先備與延伸連結"))
        text = replace_section(text, start_heading, end_heading, str(config["connection_block"]))
    note_path.write_text(text + ("\n" if not text.endswith("\n") else ""), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Integrate bridge-layer links into core knowledge-base pages.")
    parser.add_argument("--vault", help="Knowledge-base vault path. Falls back to KB_VAULT_PATH or .knowledge-base.local.json")
    parser.add_argument("--batch", choices=sorted(BATCHES), default="all")
    args = parser.parse_args()

    vault = resolve_vault_path(args.vault)
    for title in BATCHES[args.batch]:
        note_path = next(vault.rglob(f"{title}.md"))
        update_note(note_path, TARGETS[title])
        print(f"updated {note_path}")


if __name__ == "__main__":
    main()
