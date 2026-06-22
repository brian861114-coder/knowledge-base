# knowledge-base

## 中文

`knowledge-base` 是一個以外部 Obsidian Vault 為內容來源的互動式大學物理知識庫專案。這個 repo 同時承擔三件事：內容匯出工具鏈、結構 / 品質驗證、以及前端閱讀介面。

### 專案由兩部分組成
1. Git repo 本身
- schema
- 工具腳本
- 前端 prototype
- 匯出的 JSON 成果

2. 外部 Obsidian Vault
- 真正的 Markdown 筆記內容
- 知識庫的 source of truth

### 已知核心能力
- Schema-first 筆記工作流
- 結構驗證
- 知識庫整體驗證
- 內容品質稽核
- 筆記骨架生成
- JSON 匯出給前端讀取
- GitHub Pages 形式的前端展示

### 主要路徑
- `schema/`: 筆記型別、章節規則與內容規則
- `tools/`: 匯出、驗證、生成與遷移腳本
- `prototype/`: 前端閱讀原型
- `docs/`: 部署輸出
- `knowledge-base-template/`: 可重用模板
- `materials-science-engineering-kb/`: 材料科學子專案

### 專案定位
這不是單純展示頁，也不是單純筆記備份。它是一套完整的「外部 vault + schema + validator + export + frontend」知識庫工作流。

## English

`knowledge-base` is an interactive university-level physics knowledge base whose content source lives in an external Obsidian vault. This repository plays three roles at once: export toolchain, structure / quality validation, and frontend reading interface.

### The project has two parts
1. The Git repo itself
- schema files
- tooling scripts
- frontend prototype
- exported JSON artifacts

2. The external Obsidian vault
- the actual Markdown note content
- the source of truth for the knowledge base

### Known core capabilities
- schema-first note workflow
- structure validation
- full knowledge-base validation
- content-quality auditing
- note skeleton generation
- JSON export for frontend consumption
- GitHub Pages-style frontend publishing

### Main paths
- `schema/`: note types, section rules, and content rules
- `tools/`: export, validation, generation, and migration scripts
- `prototype/`: reading frontend prototype
- `docs/`: deploy output
- `knowledge-base-template/`: reusable template
- `materials-science-engineering-kb/`: materials-science subproject

### Project positioning
This is not just a showcase site and not just a note backup. It is a full knowledge-base workflow built around an external vault, schema, validators, export scripts, and a frontend reader.