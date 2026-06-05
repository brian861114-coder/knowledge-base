# Standalone HTML App

這個子資料夾是一份可直接雙擊 `index.html` 開啟的本機版知識圖譜，不需要啟動伺服器。

## 使用方式

1. 進入這個資料夾。
2. 直接打開 `index.html`。
3. 不需要啟動本機伺服器（使用 `file://` 協議即可）。

## 如何更新資料

1. 執行 `python tools/run_exports.py --vault /path/to/vault --out-dir ./standalone_html_app` 將 JSON 輸出到此目錄。
2. 或手動將生成好的 `graph.json` 和 `note_details.json` 複製過來。

## 離線內嵌模式（選用）

如果想完全離線使用（不依賴外部 JSON 載入），可以將資料嵌入到 JavaScript 中：

```bash
# 將 graph.json 轉為 JS 變數
echo "window.__KB_GRAPH__ = " > standalone_html_app/graph-data.js
cat graph.json >> standalone_html_app/graph-data.js
echo ";" >> standalone_html_app/graph-data.js

# 將 note_details.json 轉為 JS 變數
echo "window.__KB_NOTE_DETAILS__ = " > standalone_html_app/note-details-data.js
cat note_details.json >> standalone_html_app/note-details-data.js
echo ";" >> standalone_html_app/note-details-data.js
```

然後在 `index.html` 中加入這兩個 `<script>` 標籤，並修改 `app.js` 中資料來源的設定。
