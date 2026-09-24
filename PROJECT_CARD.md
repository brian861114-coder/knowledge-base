---
id: knowledge-base
name: knowledge-base
summary: 封存的物理知識庫工作流：外部 vault + schema／驗證／匯出 + 圖譜前端。
state: archived
locations:
  - host: nitro
    path: C:\Users\brian\Downloads\10_projects\19_archive\knowledge-base
    role: source
status_source: AI_HANDOFF.md
snapshot: summary
related:
  - knowledge-base-template
card_reviewed: 2026-09-24
---

## 用途
把 Obsidian 物理筆記變成可驗證、可匯出、可瀏覽的圖譜（README；ARCHITECTURE 2026-08-06）。內容正本在外部 vault，不在此 repo。

## 功能
schema 驗證、JSON 匯出、`prototype/` 圖譜與閱讀、`docs/` GitHub Pages、材料子專案與 Semantic Lens 原型。

## 結構與入口
`schema/`、`tools/run_exports.py`、`prototype/index.html`、`start_prototype.cmd`、衍生檔 `physics_graph.json`。模板複本：`knowledge-base-template/`。

## 外部依賴
Python、Obsidian（外部 vault）、MathJax／GitHub Pages（文件）。遠端 `knowledge-base`。

## 禁區
`.knowledge-base.local.json`（若存在）、金鑰、vault 筆記正文。Handoff 裡的舊本機路徑當過期。

## 給 AI 的注意事項
勿手改匯出 JSON。Handoff（2026-06-07）路徑／篇數與 ARCHITECTURE（417 篇）不一致，以現場為準 [未驗收]。`related` 僅因 README 點名模板目錄。
