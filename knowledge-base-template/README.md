# Knowledge Base Template

通用知識庫架構模板，基於 [physics knowledge_map](https://github.com/brian861114-coder/knowledge-base) 的開發經驗萃取而來。

## 核心理念

```
Obsidian Vault (Markdown 筆記)
  → YAML Schema 驅動（定義 type/domain/section 結構）
  → Python 腳本自動化（豐富/匯出/驗證）
  → JSON 匯出（graph.json + note_details.json）
  → 前端原型（圖譜探索 + 全文閱讀模式）
  → GitHub Pages 部署（自動化 deploy）
```

**Source of Truth 分離原則：**
- **Vault** = 內容（筆記、公式、連結）
- **Repo** = 工具鏈（腳本、前端、schema、匯出資料）

---

## 目錄結構

```
knowledge-base-template/
├── README.md                          # 本文件
├── schema/                            # 可配置的知識庫定義
│   ├── note_types.yaml                # 筆記類型定義（6 種預設）
│   ├── domains.yaml                   # 兩層領域分類（taxonomy + domain）
│   └── sections.yaml                  # 每種 type 的標準 section 結構
├── tools/                             # 工具腳本
│   ├── kb_config.py                   # 共用配置載入器 + helper 函數
│   ├── export_graph.py                # 匯出圖譜 JSON（含 frontmatter 關係 + wikilinks）
│   ├── export_note_details.py         # 匯出筆記詳情 JSON（sections, previews）
│   ├── validate.py                    # 驗證 vault + 匯出檔案一致性
│   └── run_exports.py                 # 一鍵匯出 + 驗證
├── prototype/                         # 前端原型（圖譜探索 + 閱讀模式）
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── standalone_html_app/               # 可離線使用的本機版（無需伺服器）
│   └── README.md
├── scripts/
│   └── deploy.sh                      # GitHub Pages 部署腳本
├── docs/                              # 架構文件
│   ├── NEW_TOPIC_GUIDE.md             # 如何建立新知識庫（完整教學）
│   ├── CONTENT_WORKFLOW.md            # 內容工作流程與品質標準
│   └── FRONTEND_CUSTOMIZATION.md      # 前端客製化指南
└── .knowledge-base.local.example.json # 本地配置範例
```

---

## 快速開始

### 建立新知識庫

1. **複製本模板資料夾**
   ```bash
   cp -r knowledge-base-template/ your-new-kb/
   cd your-new-kb/
   ```

2. **修改 `schema/` 下的 YAML 檔案**
   - `note_types.yaml`：定義你的筆記類型（預設 6 種：map/law/concept/quantity/experiment/mathematical_tool）
   - `domains.yaml`：定義你的分類（兩層：taxonomy_domain + domain）
   - `sections.yaml`：定義每種 type 的強制與選用 section

3. **建立 Obsidian Vault 資料夾結構**
   ```
   your-vault/
   ├── 00_maps/
   ├── 01_laws/
   ├── 02_concepts/
   ├── 03_quantities/
   ├── 04_experiments/
   └── 05_mathematical_tools/
   ```

4. **撰寫筆記**，使用標準 frontmatter：
   ```yaml
   ---
   title: 你的筆記標題
   type: concept          # 對應 note_types.yaml 中的 id
   domain: 力學            # 對應 domains.yaml 中的 id
   taxonomy_domain: mechanics  # 第一層分類（選用，用於前端 toggle）
   tags: [標籤1, 標籤2]
   prerequisites:
     - "[[先備知識]]"
   related_concepts:
     - "[[相關概念]]"
   ---
   ```

5. **匯出並啟動前端**
   ```bash
   # 一鍵匯出 + 驗證
   python tools/run_exports.py --vault /path/to/vault --out-dir ./docs

   # 啟動本機伺服器
   python -m http.server 4173
   # 訪問 http://127.0.0.1:4173/prototype/
   ```

6. **(選用) 部署到 GitHub Pages**
   ```bash
   bash scripts/deploy.sh "feat: initial knowledge base"
   ```

---

## Schema 配置說明

### note_types.yaml

定義知識庫支援的筆記類型。每個 type 對應 Vault 中的一個子資料夾。

```yaml
types:
  - id: concept
    label: 概念
    folder: "02_concepts"
    color: "#648356"
    description: "核心概念與定義"

  - id: map
    label: 導覽頁
    folder: "00_maps"
    color: "#ae5a31"
    description: "領域總覽、知識地圖入口"
```

### domains.yaml

支援**兩層分類系統**（taxonomy + domain），對應前端的 filterMode toggle。

```yaml
# 第一層：taxonomy_domain（用於總覽 toggle 切換）
taxonomy_domains:
  - id: mechanics
    label: 力學
    color: "#648356"
    description: "從運動、力、能量與動量開始"

# 第二層：domain（更細的分類）
domains:
  - id: 力學
    label: 力學
    taxonomy: mechanics
    description: "從運動學到動力學的經典力學體系。"
```

### sections.yaml

定義每種 type 的標準 section 結構。這是可擴充性的核心。

```yaml
section_schemas:
  concept:
    required:
      - heading: "物理直覺"
        description: "用直覺語言解釋為什麼需要這個概念"
        anchor: true
      - heading: "定義"
        description: "正式定義與數學表述"
      - heading: "歷史背景"
        description: "概念的發展脈絡"
        anchor: true
    optional:
      - heading: "常見誤解"
      - heading: "相關概念"
      - heading: "延伸閱讀"
```

`anchor: true` 的 section 在 enrich 腳本中用於定位插入位置。

---

## 資料流架構

```
┌──────────────────┐     export_graph.py      ┌──────────────┐
│                  │ ────────────────────────→ │  graph.json  │
│  Obsidian Vault  │                           │  (nodes +    │
│  (Markdown +     │     export_note_details   │   edges)     │
│   frontmatter)   │ ────────────────────────→ │              │
│                  │                           │note_details  │
│                  │                           │  .json       │
└──────────────────┘                           └──────┬───────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │  前端 prototype  │
                                              │  (graph + reader)│
                                              │                  │
                                              │  GitHub Pages    │
                                              └──────────────────┘
```

---

## 與 physics 版本的對應關係

| 面向 | physics 版本 | 模板版本 |
|------|-------------|---------|
| 筆記類型 | 6 種（硬編碼） | YAML 配置 |
| 領域 | 雙層（taxonomy + domain） | YAML 配置 |
| Section 結構 | 依賴具體腳本 | 統一 schema.yaml |
| 匯出腳本 | `tools/export_*.py` + `obsidian-knowledge-map-demo/scripts/` | 統一在 `tools/` 下 |
| 前端 | 綁定 `physics_graph.json` | 可配置 `graph.json` / `note_details.json` |
| 驗證 | `validate_knowledge_base.py`（物理專用） | `validate.py`（schema-driven） |
| 離線版 | `standalone_html_app/` | 包含在模板中 |
| 部署 | `scripts/deploy.sh` | 包含在模板中 |

---

## 擴充指南

### 新增筆記類型

1. 在 `schema/note_types.yaml` 新增 type 定義（id, label, folder, color）
2. 在 `schema/sections.yaml` 新增對應的 section schema
3. 在 Vault 中建立對應資料夾
4. 在 `prototype/app.js` 中的 `typeLabel` 物件新增對應標籤
5. 在 `prototype/styles.css` 中的 `:root` 新增 `--type-{id}` 色彩變數
6. 重新匯出

### 新增領域

1. 在 `schema/domains.yaml` 的 `taxonomy_domains` 或 `domains` 區塊新增
2. 在 Vault 的對應筆記 frontmatter 中設定 `domain` / `taxonomy_domain` 欄位
3. 在 `prototype/app.js` 的 `domainDescriptions` 或 `taxonomyDescriptions` 物件新增描述
4. 重新匯出

### 自訂前端

1. 修改 `prototype/index.html` 中的標題與品牌文案
2. 修改 `prototype/app.js` 中的 `domainDescriptions` / `taxonomyDescriptions` / `domainColorPalette` / `taxonomyColorPalette`
3. 修改 `prototype/styles.css` 中的色彩變數（`:root` 區塊）

---

## 技術需求

- Python 3.11+
- 無額外依賴（純標準庫；需要 `pyyaml` 來解析 schema YAML，但內建手動 parser fallback）
- Obsidian（用於內容編輯）
- 現代瀏覽器（用於前端原型）
- Git + GitHub Pages（用於部署，選用）

---

## 參考專案

- [physics knowledge-base](https://github.com/brian861114-coder/knowledge-base) — 319 筆節點、7301 條邊的物理知識圖譜，本模板的實作參考
