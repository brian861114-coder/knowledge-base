# Knowledge Base Template

通用知識庫架構模板，基於 physics knowledge_map 的經驗萃取而來。

## 核心理念

```
Obsidian Vault (Markdown 筆記)
  → YAML Schema 驅動（定義 type/domain/section 結構）
  → Python 腳本自動化（生成/豐富/匯出/驗證）
  → JSON 匯出（graph + note_details）
  → 前端原型（圖譜探索 + 全文閱讀）
```

**Source of Truth 分離原則**：
- **Vault** = 內容（筆記、公式、連結）
- **Repo** = 工具鏈（腳本、前端、schema、匯出資料）

---

## 目錄結構

```
knowledge-base-template/
├── README.md                          # 本文件
├── schema/                            # 可配置的知識庫定義
│   ├── note_types.yaml                # 筆記類型定義
│   ├── domains.yaml                   # 領域定義
│   └── sections.yaml                  # 每種 type 的標準 section 結構
├── tools/                             # 工具腳本
│   ├── kb_config.py                   # 共用配置載入器
│   ├── generate_notes.py              # 從 YAML 配置批量生成筆記
│   ├── enrich_notes.py                # 豐富現有筆記內容
│   ├── export_note_details.py         # 匯出筆記詳情 JSON
│   ├── export_graph.py                # 匯出圖譜 JSON
│   ├── validate.py                    # 驗證知識庫完整性
│   └── run_exports.py                 # 一鍵匯出 + 驗證
├── prototype/                         # 前端原型（從 physics 版本複製）
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── docs/                              # 架構文件
│   ├── NEW_TOPIC_GUIDE.md             # 如何建立新知識庫
│   ├── CONTENT_WORKFLOW.md            # 內容工作流程
│   └── FRONTEND_CUSTOMIZATION.md      # 前端客製化指南
└── .knowledge-base.local.example.json # 本地配置範例
```

---

## 快速開始

### 建立新知識庫

1. 複製本模板資料夾
2. 修改 `schema/` 下的三個 YAML 檔案（定義你的筆記類型、領域、section 結構）
3. 建立 Obsidian Vault 資料夾結構
4. 執行 `python tools/generate_notes.py --vault <vault_path>` 生成初始筆記
5. 在 Obsidian 中編輯、擴充內容
6. 執行 `python tools/run_exports.py --vault <vault_path>` 匯出 JSON
7. 啟動原型：`python -m http.server <port>` 後訪問 `/prototype/`

### 在現有知識庫上工作

```bash
# 匯出
python tools/run_exports.py --vault /path/to/vault

# 驗證
python tools/validate.py --vault /path/to/vault

# 生成新筆記批次
python tools/generate_notes.py --vault /path/to/vault --batch batch_name
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
  - id: law
    label: 定律
    folder: "01_laws"
    color: "#315f98"
    description: "物理定律、化學反應式等"
```

### domains.yaml

定義知識領域分類。

```yaml
domains:
  - id: mechanics
    label: 力學
    description: "從運動、力、能量與動量開始"
  - id: electromagnetism
    label: 電磁學
    description: "從電荷與電場出發"
```

### sections.yaml

定義每種 type 的標準 section 結構。這是可擴充性的核心。

```yaml
section_schemas:
  concept:
    required:
      - heading: "物理直覺"
        description: "用直覺語言解釋為什麼需要這個概念"
      - heading: "定義"
        description: "正式定義與數學表述"
      - heading: "歷史背景"
        description: "概念的發展脈絡"
    optional:
      - heading: "常見誤解"
      - heading: "相關概念"
      - heading: "延伸閱讀"
```

---

## 與 physics 版本的差異

| 面向 | physics 版本 | 模板版本 |
|------|-------------|---------|
| 筆記類型 | 6 種硬編碼 | YAML 配置 |
| 領域 | 9 個硬編碼 | YAML 配置 |
| Section 結構 | 每個腳本各自定義 | 統一 schema.yaml |
| 生成腳本 | 每批一個獨立檔案 | 單一腳本 + YAML batch 配置 |
| 前端 | 綁定 physics_*.json | 可配置資料來源 |
| 驗證 | 硬編碼物理 schema | 從 schema.yaml 讀取 |

---

## 擴充指南

### 新增筆記類型

1. 在 `schema/note_types.yaml` 新增 type 定義
2. 在 `schema/sections.yaml` 新增對應的 section schema
3. 在 Vault 中建立對應資料夾
4. 重新匯出

### 新增領域

1. 在 `schema/domains.yaml` 新增 domain
2. 在 Vault 的對應筆記 frontmatter 中設定 `domain` 欄位
3. 重新匯出

### 自訂前端

1. 修改 `prototype/index.html` 中的標題與品牌文案
2. 修改 `prototype/app.js` 中的 `domainDescriptions` 物件
3. 修改 `prototype/styles.css` 中的色彩變數（`:root` 區塊）

---

## 技術需求

- Python 3.11+
- 無額外依賴（純標準庫）
- Obsidian（用於內容編輯）
- 現代瀏覽器（用於前端原型）
