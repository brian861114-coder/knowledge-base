#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from kb_config import parse_frontmatter

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent
VAULT = ROOT / "vault"

RELATION_FIELDS = {
    "prerequisites",
    "related_concepts",
    "related_quantities",
    "related_laws",
    "experiments",
    "math_tools",
    "derived_results",
    "modern_connections",
    "tested_laws",
    "measured_quantities",
    "measurement_methods",
    "used_in",
    "includes",
    "recommended_order",
}

LINK_RE = re.compile(r"\[\[([^\]|#]+)(#[^\]|]+)?(?:\|([^\]]+))?\]\]")
FIELD_RE = re.compile(r"^([A-Za-z_]+):\s*(.*)$")

# Manual overrides for titles that were left as question marks or need cleaner wording.
TITLE_OVERRIDES = {
    "Advanced Functional and Data-Driven Materials Map": "先進功能與資料驅動材料圖",
    "Amorphous Structure": "非晶結構",
    "Biomaterials and Surface Response Map": "生醫材料與表面響應圖",
    "Carrier Mobility": "載子遷移率",
    "Characterization Methods Overview": "表徵方法總覽",
    "Characterization and Failure Analysis Map": "表徵與失效分析圖",
    "Corrosion Resistance": "耐蝕性",
    "Creep Resistance": "抗蠕變性",
    "Crystal Defects": "晶體缺陷",
    "Crystal Structure": "晶體結構",
    "Defects Interfaces and Microstructure Map": "缺陷、介面與微觀組織圖",
    "Dielectric Response": "介電響應",
    "Differential Scanning Calorimetry": "差示掃描量熱",
    "Dislocations": "差排",
    "Ductility and Plastic Flow": "延性與塑性流動",
    "Elastic Modulus and Stiffness": "彈性模數與剛性",
    "Electrical Properties": "電性",
    "Electronic Magnetic and Optical Properties Map": "電子、磁性與光學性質圖",
    "Electron Backscatter Diffraction": "電子背向散射繞射",
    "Energy-Dispersive Spectroscopy": "能量散射 X 光譜",
    "Environmental Assisted Cracking": "環境輔助開裂",
    "Environmental and Chemical Degradation Map": "環境與化學劣化圖",
    "Fatigue Resistance": "抗疲勞性",
    "Fracture and Crack Propagation Map": "斷裂與裂紋擴展圖",
    "Fracture Toughness": "斷裂韌性",
    "Glass Transition and Thermal Transitions": "玻璃轉移與熱轉變",
    "Hardness Testing": "硬度試驗",
    "Impact Testing": "衝擊試驗",
    "Ionic Conductivity": "離子導電率",
    "Magnetic Response": "磁性響應",
    "Materials Failure Overview": "材料失效總覽",
    "Materials Properties Overview": "材料性質總覽",
    "Materials Science Overview": "材料科學總覽",
    "Mechanical Properties": "機械性質",
    "Mechanical Properties Map": "機械性質圖",
    "Mechanical Testing": "機械試驗",
    "Mechanical and Environmental Testing Map": "機械與環境測試圖",
    "Microstructure": "微觀組織",
    "Microscopy Diffraction and Spectroscopy Map": "顯微、繞射與光譜圖",
    "Optical Properties": "光學性質",
    "Phase Fraction and Morphology": "相分率與形貌",
    "Planar Defects and Twins": "平面缺陷與雙晶",
    "Point Defects": "點缺陷",
    "Processing and Structural Evolution Map": "製程與結構演化圖",
    "Recovery Recrystallization and Grain Growth": "回復、再結晶與晶粒成長",
    "Residual Stress": "殘餘應力",
    "Raman Spectroscopy": "拉曼光譜",
    "Scanning Electron Microscopy": "掃描式電子顯微鏡",
    "Semiconductor and Thin-Film Device Map": "半導體與薄膜元件圖",
    "Solidification Transformation and Heat-Treatment Map": "凝固、相變與熱處理圖",
    "Strength and Yield Behavior": "強度與降伏行為",
    "Structure Processing Properties Performance Map": "結構、製程、性質與性能圖",
    "Structure and Length Scales Map": "結構與尺度圖",
    "Tensile Testing": "拉伸試驗",
    "Texture and Anisotropy": "紋理與各向異性",
    "Thermal Expansion": "熱膨脹",
    "Thermal Properties": "熱性質",
    "Thermal and Surface Analysis Map": "熱分析與表面分析圖",
    "Thermal and Transport Properties Map": "熱與傳輸性質圖",
    "Thermoelectric Transport Tradeoffs": "熱電傳輸權衡",
    "Thermogravimetric Analysis": "熱重分析",
    "Transmission Electron Microscopy": "穿透式電子顯微鏡",
    "Unit Cell and Crystal Symmetry": "單位晶胞與晶體對稱性",
    "Wear Resistance": "耐磨性",
    "X-ray Diffraction": "X 光繞射",
    "X-ray Photoelectron Spectroscopy": "X 光光電子能譜",
}

HEADING_REPLACEMENTS = {
    "## Why it matters": "## 為什麼這很重要",
    "## Why this map exists": "## 為什麼需要這張圖",
    "## Definition": "## 定義",
    "## Map structure": "## 地圖結構",
    "## What controls it": "## 影響因素",
    "## Core idea": "## 核心概念",
    "## How to read this map": "## 如何閱讀這張圖",
    "## How it is measured": "## 如何量測",
    "## Typical failure logic": "## 典型失效邏輯",
    "## Common tradeoffs": "## 常見權衡",
    "## Where it shows up": "## 常見出現場景",
    "## Processing implications": "## 製程上的意涵",
    "## Design implications": "## 設計上的意涵",
    "## Interpretation pitfalls": "## 判讀陷阱",
    "## Practical reading": "## 實務判讀",
    "## What this note covers": "## 本頁涵蓋內容",
}


def load_current_titles() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for path in sorted(VAULT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        raw_fm, _ = parse_frontmatter(text)
        for line in raw_fm.splitlines():
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip()
                if title and "?" not in title:
                    mapping[path.stem] = title
                break
    mapping.update(TITLE_OVERRIDES)
    return mapping


def parse_frontmatter_lines(raw: str) -> list[tuple[str | None, str, str | None]]:
    parsed: list[tuple[str | None, str, str | None]] = []
    for line in raw.splitlines():
        match = FIELD_RE.match(line)
        if match:
            key, value = match.groups()
            parsed.append((key, line, value))
        else:
            parsed.append((None, line, None))
    return parsed


def extract_relation_targets(value: str) -> list[str]:
    targets = []
    for match in LINK_RE.finditer(value):
        target = match.group(1).strip().strip("[]")
        if target:
            targets.append(target)
    return targets


def build_relation_value(targets: list[str], title_map: dict[str, str]) -> str:
    if not targets:
        return "[]"
    items = []
    for target in targets:
        alias = title_map.get(target, target)
        items.append(f"[[{target}|{alias}]]")
    return "[" + ", ".join(items) + "]"


def rewrite_body_links(body: str, title_map: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        anchor = match.group(2) or ""
        alias = title_map.get(target) or match.group(3) or target
        return f"[[{target}{anchor}|{alias}]]"

    for source, target in HEADING_REPLACEMENTS.items():
        body = body.replace(source, target)
    return LINK_RE.sub(repl, body)


def main() -> None:
    title_map = load_current_titles()

    for path in sorted(VAULT.rglob("*.md")):
        current_text = path.read_text(encoding="utf-8")
        # Read the original English source from git using the file currently on disk as the body source of truth.
        # We rebuild frontmatter from the pre-translation version and keep the translated body.
        import subprocess

        rel_git_path = path.relative_to(REPO_ROOT).as_posix()
        head_text = subprocess.check_output(
            ["git", "show", f"HEAD:{rel_git_path}"],
            cwd=REPO_ROOT,
            text=True,
            encoding="utf-8",
        )

        current_fm, current_body = parse_frontmatter(current_text)
        head_fm, _ = parse_frontmatter(head_text)

        current_values: dict[str, str] = {}
        for key, _, value in parse_frontmatter_lines(current_fm):
            if key is not None and value is not None:
                current_values[key] = value

        new_lines: list[str] = []
        for key, original_line, value in parse_frontmatter_lines(head_fm):
            if key is None:
                new_lines.append(original_line)
                continue
            if key == "title":
                new_lines.append(f"title: {title_map.get(path.stem, current_values.get('title', path.stem))}")
                continue
            if key == "summary":
                new_lines.append(f"summary: {current_values.get('summary', value or '')}")
                continue
            if key in RELATION_FIELDS:
                targets = extract_relation_targets(value or "")
                new_lines.append(f"{key}: {build_relation_value(targets, title_map)}")
                continue
            new_lines.append(f"{key}: {current_values.get(key, value or '')}")

        rewritten_body = rewrite_body_links(current_body, title_map)
        new_text = "---\n" + "\n".join(new_lines) + "\n---\n" + rewritten_body.lstrip("\n")
        path.write_text(new_text, encoding="utf-8")


if __name__ == "__main__":
    main()
