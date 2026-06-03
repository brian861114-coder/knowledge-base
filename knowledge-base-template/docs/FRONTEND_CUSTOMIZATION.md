# 前端客製化指南

## 基本客製化

### 修改標題與品牌

`prototype/index.html`：

```html
<title>你的知識庫名稱</title>
<h1>你的知識庫名稱</h1>
<p>你的標語</p>
```

### 修改色彩主題

`prototype/styles.css` 頂部的 `:root` 變數：

```css
:root {
  --bg: #f7f4ee;              /* 背景色 */
  --ink: #181b22;             /* 文字色 */
  --accent: #2f64a3;          /* 主色調 */
  --warm: #b75e31;            /* 強調色 */
  --type-map: #ae5a31;        /* 導覽頁色彩 */
  --type-law: #315f98;        /* 定律色彩 */
  --type-concept: #648356;    /* 概念色彩 */
  --type-quantity: #83589a;   /* 物理量色彩 */
  --type-mathematical_tool: #9b6b35;  /* 數學工具色彩 */
}
```

### 修改領域描述

`prototype/app.js` 中的 `domainDescriptions` 物件：

```javascript
const domainDescriptions = {
  力學: "你的領域描述",
  電磁學: "你的領域描述",
  // ...
};
```

### 修改 type 標籤

`prototype/app.js` 中的 `typeLabel` 物件：

```javascript
const typeLabel = {
  map: "導覽頁",
  law: "定律",
  concept: "概念",
  // 新增你的 type：
  reaction: "反應",
  compound: "化合物",
};
```

### 修改字體

`prototype/styles.css` 頂部的 `@import`：

```css
@import url("https://fonts.googleapis.com/css2?family=Your+Font&display=swap");
```

然後在 `body` 的 `font-family` 中指定。

## 進階客製化

### 修改圖譜節點大小

`prototype/styles.css` 中的 `.node-core` 相關規則。

### 修改閱讀模式佈局

`prototype/styles.css` 中的 `.reader-layout.has-outline` 的 `grid-template-columns`。

### 修改搜尋結果數量上限

`prototype/app.js` 中搜尋相關的 `.slice(0, 50)` 數字。

## 資料來源切換

如果要支援多個知識庫，修改 `prototype/app.js` 頂部：

```javascript
const graphUrl = "../physics_graph.json";
const noteDetailsUrl = "../physics_note_details.json";
```

改為從 URL 參數讀取：

```javascript
const params = new URLSearchParams(window.location.search);
const db = params.get("db") || "default";
const graphUrl = `../${db}_graph.json`;
const noteDetailsUrl = `../${db}_note_details.json`;
```

然後用 `?db=physics` 或 `?db=chemistry` 切換。
