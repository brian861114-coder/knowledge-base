# Standalone HTML App

這個子資料夾是一份可直接雙擊 `index.html` 開啟的本機版知識地圖。

## 使用方式

1. 進入這個資料夾。
2. 直接打開 `index.html`。
3. 不需要啟動本機伺服器。

## 重要說明

- `graph-data.js` 與 `note-details-data.js` 已經內含目前匯出的資料。
- 如果根目錄的 `physics_graph.json` 或 `physics_note_details.json` 之後更新，這個子資料夾裡的兩個資料檔也要重新產生，否則內容不會同步。
- 若畫面中某些中文內容仍有亂碼，那是現有匯出資料本身的編碼品質問題，不是這個離線 HTML 外殼的問題。
