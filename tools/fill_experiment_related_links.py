#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from apply_weak_model_response import apply_response_to_text, load_schema, make_rename_map, parse_frontmatter
from kb_paths import repo_root, resolve_vault_path


RELATED_LINK_SECTIONS: dict[str, list[tuple[str, str, list[str]]]] = {
    "功能定理驗證實驗": [
        ("相關概念", "這個實驗把做功、位移與動能變化接成同一條分析鏈。", ["功", "位移", "動能"]),
        ("相關定律", "量測結果最後要回到功能定理本身。", ["功能定理"]),
        ("相關物理量", "實驗中真正被比對的是受力、速度與能量變化。", ["力", "速度", "動能"]),
    ],
    "反射定律驗證實驗": [
        ("相關概念", "核心是用法線作基準比較入射與反射的幾何關係。", ["光線模型", "入射角", "反射角"]),
        ("相關定律", "整個量測直接對應到反射定律。", ["反射定律"]),
    ],
    "天平": [
        ("相關概念", "天平把平衡條件轉成質量比較，並常用於密度估算。", ["平衡", "密度"]),
        ("相關物理量", "最直接被量到的量是質量。", ["質量"]),
    ],
    "安培力實驗": [
        ("相關概念", "載流導線、磁場與電流方向是這個實驗的三個核心對象。", ["磁場", "電流", "電磁鐵"]),
        ("相關定律", "量測通常以安培定律與磁場中的受力分析來理解。", ["安培定律"]),
    ],
    "打點計時器": [
        ("相關概念", "它把連續運動拆成等時間間隔的離散點列。", ["位移", "速度", "加速度"]),
        ("相關定律", "常見用途是配合牛頓第二定律做運動分析。", ["牛頓第二定律"]),
        ("相關物理量", "點距資料最常被轉成速度與加速度。", ["速度", "加速度"]),
    ],
    "文丘里管實驗": [
        ("相關概念", "截面縮放、流速變化與壓力下降是文丘里效應的核心。", ["流速", "壓力", "理想流體近似"]),
        ("相關定律", "實驗通常同時對照伯努力方程與連續方程。", ["伯努力方程", "連續方程"]),
    ],
    "氣墊軌道碰撞實驗": [
        ("相關概念", "它把碰撞問題簡化到幾乎一維且低摩擦的情形。", ["碰撞", "碰撞分析", "動量"]),
        ("相關定律", "最主要的驗證對象是動量守恆。", ["動量守恆"]),
    ],
    "相空間軌跡模擬": [
        ("相關概念", "這個模擬用相空間圖像觀察軌道、固定點與長時間行為。", ["相空間", "相圖", "吸引子"]),
        ("相關主題", "它常被用來理解非線性系統與混沌行為。", ["混沌", "初始條件敏感性"]),
    ],
    "赫茲電磁波實驗": [
        ("相關概念", "火花放電、振盪電路與電磁波傳播共同構成這個實驗。", ["電磁波", "LC電路", "電場", "磁場"]),
        ("相關定律", "它是 Maxwell 電磁理論的重要實驗支撐。", ["馬克士威方程組"]),
    ],
    "轉動慣量量測實驗": [
        ("相關概念", "週期、扭轉回復與剛體轉動是量測轉動慣量的核心背景。", ["轉動慣量", "角速度", "簡諧運動"]),
        ("相關物理量", "最終要反推出的是轉動慣量與角頻率。", ["轉動慣量", "角頻率"]),
    ],
    "運動感測器": [
        ("相關概念", "感測器把位置資料連續化，方便重建速度與加速度。", ["簡諧運動", "速度", "加速度"]),
        ("相關定律", "它常被用來重新驗證牛頓第一與第二定律。", ["牛頓第一定律", "牛頓第二定律"]),
        ("相關物理量", "直接輸出的通常是位移、速度與加速度。", ["位移", "速度", "加速度"]),
    ],
    "電導率量測實驗": [
        ("相關概念", "材料對電流的傳輸能力，會反映在電導率與電流密度關係上。", ["電導率", "電流密度", "電場"]),
        ("相關定律", "量測解讀通常要回到歐姆定律。", ["歐姆定律"]),
    ],
    "電路驗證實驗": [
        ("相關概念", "節點電流與迴路電壓平衡是電路分析的基本結構。", ["電路", "電流", "電壓"]),
        ("相關定律", "實驗直接對照兩條 Kirchhoff 規則。", ["基爾霍夫電壓定律", "基爾霍夫電流定律"]),
    ],
    "靜電場模擬實驗": [
        ("相關概念", "導電紙模擬最適合拿來看電位分布與場線幾何。", ["電場", "電位", "等位面", "靜電平衡"]),
        ("相關定律", "其圖像解讀通常建立在高斯定律與位勢觀念上。", ["高斯定律"]),
    ],
}


def load_title_index(vault: Path) -> set[str]:
    titles: set[str] = set()
    for path in vault.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        frontmatter, _body = parse_frontmatter(text)
        titles.add(str(frontmatter.get("title", path.stem)).strip())
    return titles


def render_related_links(groups: list[tuple[str, str, list[str]]]) -> str:
    chunks: list[str] = []
    for heading, sentence, links in groups:
        chunks.append(f"### {heading}")
        chunks.append(sentence)
        chunks.append("")
        for link in links:
            chunks.append(f"- [[{link}]]")
        chunks.append("")
    return "\n".join(chunks).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill grouped related-link sections for experiment notes.")
    parser.add_argument("--vault", help="Override vault path")
    parser.add_argument("--schema-dir", help="Schema directory. Defaults to repo_root()/schema")
    parser.add_argument("--write", action="store_true", help="Write changes back to the vault")
    args = parser.parse_args()

    repo = repo_root()
    vault = resolve_vault_path(args.vault)
    schema_dir = Path(args.schema_dir).resolve() if args.schema_dir else repo / "schema"
    schema = load_schema(schema_dir)
    title_index = load_title_index(vault)

    missing_targets: list[str] = []
    for title, groups in RELATED_LINK_SECTIONS.items():
        for _heading, _sentence, links in groups:
            for link in links:
                if link not in title_index:
                    missing_targets.append(f"{title} -> {link}")
    if missing_targets:
        raise SystemExit("Missing wikilink targets:\n- " + "\n- ".join(missing_targets))

    changed = 0
    for title, groups in RELATED_LINK_SECTIONS.items():
        note_path = vault / "04_experiments" / f"{title}.md"
        text = note_path.read_text(encoding="utf-8")
        frontmatter, _body = parse_frontmatter(text)
        note_type = str(frontmatter.get("type", "")).strip()
        rename_map = make_rename_map(schema["renames"]["rename_rules"].get(note_type, []))
        updated_text, _matched = apply_response_to_text(
            text,
            note_type=note_type,
            target_section="相關連結",
            replacement_body=render_related_links(groups),
            rename_map=rename_map,
        )
        if updated_text != text:
            changed += 1
            if args.write:
                note_path.write_text(updated_text, encoding="utf-8")

    print("Experiment related-links fill summary")
    print(f"- vault: {vault}")
    print(f"- notes configured: {len(RELATED_LINK_SECTIONS)}")
    print(f"- changed: {changed}")
    print(f"- write: {args.write}")


if __name__ == "__main__":
    main()
