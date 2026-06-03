# 建立新知識庫完整指南

## 步驟一：規劃你的知識庫

在開始之前，先回答這幾個問題：

1. **主題是什麼？** （例如：有機化學、機器學習、經濟學原理）
2. **需要哪些筆記類型？** （概念、定律/定理、實驗/案例、數學工具、導覽頁）
3. **需要哪些領域分類？** （例如：有機化學 → 烷烴、烯烴、芳香烴、官能團…）
4. **每種 type 的標準 section 結構是什麼？**

## 步驟二：複製模板

```bash
cp -r knowledge-base-template/ my-new-knowledge-base/
cd my-new-knowledge-base/
```

## 步驟三：修改 Schema

### schema/note_types.yaml

根據你的主題調整筆記類型。例如「有機化學」：

```yaml
types:
  - id: reaction
    label: 反應
    folder: "01_reactions"
    color: "#c0392b"
    description: "化學反應式、機制、條件"

  - id: compound
    label: 化合物
    folder: "02_compounds"
    color: "#27ae60"
    description: "化合物的結構、性質、用途"

  - id: concept
    label: 概念
    folder: "03_concepts"
    color: "#2980b9"
    description: "有機化學的核心概念"

  - id: technique
    label: 分析技術
    folder: "04_techniques"
    color: "#8e44ad"
    description: "NMR、IR、MS 等分析方法"

  - id: map
    label: 導覽頁
    folder: "00_maps"
    color: "#e67e22"
    description: "領域總覽"
```

### schema/domains.yaml

```yaml
domains:
  - id: hydrocarbons
    label: 烴類
    description: "烷烴、烯烴、炔烴、芳香烴"

  - id: functional_groups
    label: 官能團
    description: "醇、醛、酮、羧酸、酯、胺"

  - id: stereochemistry
    label: 立體化學
    description: "手性、構型、構象"

  - id: spectroscopy
    label: 光譜學
    description: "NMR、IR、MS、UV-Vis"
```

### schema/sections.yaml

```yaml
section_schemas:
  reaction:
    required:
      - heading: "反應概要"
        description: "用一句話說清楚這個反應在做什麼"
      - heading: "反應機制"
        description: "逐步的電子轉移過程"
      - heading: "反應條件"
        description: "溫度、催化劑、溶劑"
    optional:
      - heading: "立體化學"
      - heading: "應用範例"
      - heading: "常見錯誤"

  compound:
    required:
      - heading: "結構"
        description: "分子式、結構式、鍵結"
      - heading: "物理性質"
        description: "熔點、沸點、溶解度"
      - heading: "化學性質"
        description: "主要反應類型"
    optional:
      - heading: "製備方法"
      - heading: "用途"
      - heading: "安全資訊"
```

## 步驟四：建立 Vault 資料夾結構

在 Obsidian Vault 中建立對應的資料夾：

```
your-vault/
├── 00_maps/
├── 01_reactions/
├── 02_compounds/
├── 03_concepts/
└── 04_techniques/
```

## 步驟五：建立第一批筆記

### 手動建立

在每個資料夾中建立 Markdown 檔案，使用標準 frontmatter：

```markdown
---
title: SN1 反應
type: reaction
domain: functional_groups
tags: [取代反應, 碳陽離子]
related:
  - "[[SN2反應]]"
  - "[[碳陽離子]]"
prerequisites:
  - "[[離去基團]]"
  - "[[立體化學]]"
---

## 反應概要
SN1 是單分子親核取代反應…

## 反應機制
1. 離去基團離開，形成碳陽離子
2. 親核試劑攻擊碳陽離子
…
```

### 用腳本批量生成

```bash
python tools/generate_notes.py --vault /path/to/vault --batch batch1
```

## 步驟六：匯出與啟動原型

```bash
# 匯出 JSON
python tools/run_exports.py --vault /path/to/vault

# 啟動前端
python -m http.server 4173
# 訪問 http://127.0.0.1:4173/prototype/
```

## 步驟七：迭代擴充

1. 在 Obsidian 中持續編輯筆記
2. 定期執行 `run_exports.py` 更新前端資料
3. 使用 `validate.py` 檢查連結完整性
4. 使用 `enrich_notes.py` 豐富筆記內容

---

## 常見問題

### Q: 如何支援多種語言？

在 `note_types.yaml` 中加入 `label_en`、`label_zh` 等欄位，前端根據語言設定讀取對應標籤。

### Q: 如何在前端顯示自訂的 section？

前端的 `app.js` 讀取 `note_details.json` 中的 `sections` 陣列。只要筆記中有 `## 標題`，就會自動成為一個 section。不需要修改前端。

### Q: 如何處理跨領域的連結？

使用 bridge 頁面。在 `sections.yaml` 的 `bridge_schemas` 中定義 bridge 頁面的結構，然後在相關筆記的 frontmatter `related` 中互相引用。

### Q: 匯出的 JSON 檔案太大怎麼辦？

考慮：
1. 只匯出需要的 type（過濾）
2. 將 `body_full` 改為只匯出 `body_preview`（截斷）
3. 分批匯出（每 100 筆一個 JSON）
