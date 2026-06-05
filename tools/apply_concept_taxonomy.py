#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from kb_paths import resolve_vault_path


DOMAIN_TITLES: dict[str, list[str]] = {
    "foundations": [
        "參考系",
        "慣性",
        "慣性參考系",
        "非慣性參考系",
        "伽利略變換",
        "洛侖茲轉換",
        "時間",
        "位移",
        "力",
        "功",
        "能量",
        "動能",
        "位能",
        "場",
        "場論觀點",
        "相互作用",
        "對稱性",
        "守恆律",
        "守恆量",
        "平衡",
        "穩定平衡",
        "不穩定平衡",
        "穩態",
        "暫態",
        "邊界條件",
    ],
    "mechanics": [
        "中心力",
        "圓周運動",
        "張力",
        "摩擦力",
        "重力",
        "推進",
        "質心",
        "剛體",
        "定軸轉動運動學",
        "滾動",
        "滾動運動",
        "衝量",
        "角動量",
        "角衝量",
        "角動量與碰撞",
        "軌道角動量",
        "轉矩",
        "進動",
        "章動",
        "陀螺",
        "碰撞",
        "碰撞分析",
        "機械平衡",
        "靜力平衡",
        "有效位能",
        "保守力",
        "非保守力",
        "耗散",
        "彈性",
        "勢能井",
        "自由體圖",
    ],
    "waves_optics": [
        "簡諧運動",
        "阻尼振動",
        "受迫振動",
        "共振",
        "模態",
        "正常模態",
        "機械波",
        "聲波",
        "相位",
        "相干性",
        "駐波",
        "都卜勒效應",
        "干涉",
        "繞射",
        "單縫繞射",
        "雙縫干涉",
        "薄膜干涉",
        "偏振",
        "反射",
        "折射",
        "全反射",
        "惠更斯原理",
        "光線模型",
        "解析度",
        "顯微鏡",
        "散射",
    ],
    "electromagnetism": [
        "直流電路",
        "交流電",
        "RC電路",
        "RL電路",
        "RLC電路",
        "串聯電路",
        "並聯電路",
        "節點分析",
        "迴路分析",
        "內電阻",
        "電容器",
        "平行板電容器",
        "變壓器",
        "自感",
        "互感",
        "位移電流",
        "位移電流修正",
        "電介質",
        "介電常數",
        "導體",
        "屏蔽效應",
        "電位",
        "電位能",
        "電力線",
        "電場",
        "電場能",
        "電場能量",
        "電通量",
        "通量",
        "環流",
        "磁力",
        "磁場",
        "均勻帶電球殼電場",
        "無限平面電場",
        "等位面",
        "鏡像法",
        "電磁場能量流",
        "電磁波",
        "電磁波傳播",
        "靜電平衡",
    ],
    "thermo_fluids": [
        "溫度",
        "內能",
        "熱",
        "熱傳導",
        "熱平衡",
        "熱機",
        "熱膨脹",
        "潛熱",
        "熵",
        "可逆過程",
        "不可逆過程",
        "等溫過程",
        "絕熱過程",
        "卡諾循環",
        "理想氣體",
        "分子運動論",
        "統計物理",
        "理想流體近似",
        "文氏管",
        "層流",
        "紊流",
        "黏滯力",
    ],
    "modern_physics": [
        "光電效應",
        "德布羅意波",
        "波函數",
        "波粒二象性",
        "機率振幅",
        "正規化",
        "可觀測量",
        "期望值",
        "本徵態",
        "算符",
        "穿隧",
        "薛丁格方程",
        "量子化",
        "離散能階",
        "連續譜",
        "黑體輻射",
        "狹義相對論",
        "局域性",
    ],
    "analytical_dynamics": [
        "廣義座標",
        "約束",
        "自由度",
        "拉格朗日力學",
        "作用量",
        "哈密頓量",
        "相空間",
        "泊松括號",
        "正則變換",
        "非線性系統",
        "混沌",
        "初始條件敏感性",
        "吸引子",
        "相圖",
        "龐加萊截面",
        "分岔",
    ],
}

INTRO_TITLES = {
    "時間",
    "位移",
    "力",
    "功",
    "能量",
    "動能",
    "位能",
    "溫度",
    "電場",
    "磁場",
    "機械波",
    "聲波",
    "圓周運動",
}

BRIDGE_TITLES = {
    "參考系",
    "場",
    "場論觀點",
    "對稱性",
    "守恆律",
    "守恆量",
    "通量",
    "環流",
    "相互作用",
    "邊界條件",
}

ADVANCED_TITLES = {
    *DOMAIN_TITLES["modern_physics"],
    *DOMAIN_TITLES["analytical_dynamics"],
}

CLUSTER_OVERRIDES = {
    "時間": "motion",
    "位移": "motion",
    "參考系": "motion",
    "慣性": "motion",
    "慣性參考系": "motion",
    "非慣性參考系": "motion",
    "伽利略變換": "motion",
    "洛侖茲轉換": "motion",
    "力": "force",
    "張力": "force",
    "摩擦力": "force",
    "重力": "force",
    "磁力": "force",
    "相互作用": "force",
    "保守力": "force",
    "非保守力": "force",
    "功": "energy",
    "能量": "energy",
    "動能": "energy",
    "位能": "energy",
    "內能": "energy",
    "熱": "energy",
    "熱機": "energy",
    "潛熱": "energy",
    "熵": "energy",
    "耗散": "energy",
    "場": "field",
    "場論觀點": "field",
    "電場": "field",
    "磁場": "field",
    "電力線": "field",
    "電通量": "field",
    "通量": "field",
    "環流": "field",
    "電磁場能量流": "field",
    "電磁波": "field",
    "電磁波傳播": "field",
    "對稱性": "symmetry",
    "守恆律": "symmetry",
    "守恆量": "symmetry",
    "平衡": "state",
    "穩定平衡": "state",
    "不穩定平衡": "state",
    "穩態": "state",
    "暫態": "state",
    "機械平衡": "state",
    "靜力平衡": "state",
    "熱平衡": "state",
    "可逆過程": "state",
    "不可逆過程": "state",
    "等溫過程": "state",
    "絕熱過程": "state",
    "簡諧運動": "oscillation",
    "阻尼振動": "oscillation",
    "受迫振動": "oscillation",
    "共振": "oscillation",
    "模態": "oscillation",
    "正常模態": "oscillation",
    "相位": "oscillation",
    "相干性": "oscillation",
    "駐波": "oscillation",
    "機械波": "oscillation",
    "聲波": "oscillation",
    "都卜勒效應": "oscillation",
    "干涉": "oscillation",
    "繞射": "oscillation",
    "單縫繞射": "oscillation",
    "雙縫干涉": "oscillation",
    "薄膜干涉": "oscillation",
    "偏振": "oscillation",
    "反射": "oscillation",
    "折射": "oscillation",
    "全反射": "oscillation",
    "惠更斯原理": "oscillation",
    "理想流體近似": "flow",
    "文氏管": "flow",
    "層流": "flow",
    "紊流": "flow",
    "黏滯力": "flow",
    "彈性": "material",
    "導體": "material",
    "電介質": "material",
    "介電常數": "material",
    "廣義座標": "formalism",
    "約束": "formalism",
    "自由度": "formalism",
    "拉格朗日力學": "formalism",
    "作用量": "formalism",
    "哈密頓量": "formalism",
    "相空間": "formalism",
    "泊松括號": "formalism",
    "正則變換": "formalism",
    "波函數": "formalism",
    "機率振幅": "formalism",
    "正規化": "formalism",
    "可觀測量": "formalism",
    "本徵態": "formalism",
    "算符": "formalism",
    "薛丁格方程": "formalism",
    "非線性系統": "nonlinear",
    "混沌": "nonlinear",
    "初始條件敏感性": "nonlinear",
    "吸引子": "nonlinear",
    "相圖": "nonlinear",
    "龐加萊截面": "nonlinear",
    "分岔": "nonlinear",
}

DOMAIN_DEFAULT_CLUSTER = {
    "foundations": "state",
    "mechanics": "motion",
    "waves_optics": "oscillation",
    "electromagnetism": "field",
    "thermo_fluids": "flow",
    "modern_physics": "formalism",
    "analytical_dynamics": "formalism",
}

TITLE_TO_DOMAIN: dict[str, str] = {}
for domain_name, titles in DOMAIN_TITLES.items():
    for title in titles:
        if title in TITLE_TO_DOMAIN:
            raise ValueError(f"duplicate taxonomy assignment for {title}")
        TITLE_TO_DOMAIN[title] = domain_name


def classify(title: str) -> tuple[str, str, str]:
    taxonomy_domain = TITLE_TO_DOMAIN[title]
    cluster = CLUSTER_OVERRIDES.get(title, DOMAIN_DEFAULT_CLUSTER[taxonomy_domain])
    if title in INTRO_TITLES:
        level = "intro"
    elif title in BRIDGE_TITLES:
        level = "bridge"
    elif title in ADVANCED_TITLES:
        level = "advanced"
    else:
        level = "core"
    return taxonomy_domain, cluster, level


def upsert_frontmatter(text: str, taxonomy_domain: str, cluster: str, level: str) -> str:
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter start")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing frontmatter end")

    frontmatter = text[4:end].splitlines()
    body = text[end + 5 :]

    replacements = {
        "taxonomy_domain": taxonomy_domain,
        "cluster": cluster,
        "level": level,
    }

    seen: set[str] = set()
    updated: list[str] = []
    inserted = False

    for line in frontmatter:
        if ":" in line:
            key = line.split(":", 1)[0].strip()
            if key in replacements:
                updated.append(f"{key}: {replacements[key]}")
                seen.add(key)
                continue
            updated.append(line)
            if key == "domain" and not inserted:
                for add_key in ("taxonomy_domain", "cluster", "level"):
                    if add_key not in seen:
                        updated.append(f"{add_key}: {replacements[add_key]}")
                        seen.add(add_key)
                inserted = True
        else:
            updated.append(line)

    if not inserted:
        for add_key in ("taxonomy_domain", "cluster", "level"):
            if add_key not in seen:
                updated.append(f"{add_key}: {replacements[add_key]}")
                seen.add(add_key)

    return "---\n" + "\n".join(updated) + "\n---\n" + body


def main() -> None:
    vault = resolve_vault_path()
    concept_dir = vault / "02_concepts"
    files = sorted(concept_dir.rglob("*.md"))

    missing = [path.stem for path in files if path.stem not in TITLE_TO_DOMAIN]
    if missing:
        raise ValueError(f"missing taxonomy assignments: {', '.join(missing)}")

    for path in files:
        taxonomy_domain, cluster, level = classify(path.stem)
        text = path.read_text(encoding="utf-8")
        updated = upsert_frontmatter(text, taxonomy_domain, cluster, level)
        path.write_text(updated, encoding="utf-8")

    print(f"updated={len(files)} concepts")


if __name__ == "__main__":
    main()
