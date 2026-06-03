# 內容工作流程

## 日常編輯流程

```
1. 在 Obsidian 中編輯/新增筆記
2. 確保 frontmatter 完整（title, type, domain, tags）
3. 確保 section 結構符合 schema/sections.yaml 的定義
4. 使用 [[wikilink]] 建立筆記間的連結
5. 執行 run_exports.py 匯出
6. 在前端驗證顯示效果
```

## Frontmatter 標準欄位

```yaml
---
title: 筆記標題              # 必填
type: concept                # 必填：對應 note_types.yaml 中的 id
domain: mechanics            # 必填：對應 domains.yaml 中的 id
tags: [標籤1, 標籤2]         # 選填：用於搜尋與分類
related:                     # 選填：相關筆記
  - "[[其他筆記]]"
prerequisites:               # 選填：先備知識
  - "[[基礎概念]]"
related_laws:                # 選填（concept type 常用）
  - "[[相關定律]]"
related_quantities:          # 選填
  - "[[相關物理量]]"
math_tools:                  # 選填：使用的數學工具
  - "[[微積分]]"
---
```

## Section 結構規範

### 必要 Section

每種 type 都有 `required` 的 section。缺少這些 section 會在驗證時被標記。

### 物理直覺 Section

這是所有 type 都建議有的 section。它的目的是：

- 用**直覺語言**解釋核心概念，不依賴公式
- 回答「為什麼需要這個概念？」
- 幫助讀者在看公式之前先建立心智模型

**好的物理直覺範例**：

> 能量守恆之所以重要，不是因為它是一個漂亮的數學式，而是因為它告訴你：不管過程多複雜，你總是可以從頭尾的狀態算出答案，不需要追蹤中間每一步。

**壞的物理直覺範例**（避免這種）：

> 能量守恆是一個重要的物理定律，在許多情況下都有應用。

### 歷史背景 Section

- 說明概念/定律的發展脈絡
- 提到關鍵人物與時間點
- 不要寫成流水帳，聚焦在「為什麼那個時代需要這個概念」

## 匯出驗證標準

通過驗證的知識庫必須滿足：

```
broken [[wikilink]] targets    = 0
broken frontmatter relations   = 0
math $/$$ delimiter issues     = 0
duplicate titles               = 0
missing required fields        = 0
```

## 深化內容的方向

1. **增加推導步驟**：在核心概念/定律中加入 step-by-step 推導
2. **增加 bridge 頁面**：連接不同領域的筆記，減少孤立節點
3. **增加 reverse links**：從舊的核心頁面反向連結到新的 bridge 頁面
4. **豐富直覺與歷史**：避免模板化語言，每篇都寫出獨特的洞察
5. **增加實驗/案例**：理論筆記配上具體的實驗驗證或應用案例
