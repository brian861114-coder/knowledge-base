# Desktop EXE App

這個子資料夾是桌面版包裝層，用來把知識地圖離線 HTML 應用打包成 Windows `.exe`。

## 結構

- `app/`: 實際被 Electron 載入的離線前端
- `main.js`: Electron 主程序
- `preload.js`: 最小 preload
- `package.json`: 啟動與打包設定
- `build-desktop.ps1`: 同步離線前端並重新打包
- `build/icon.ico`: 桌面版圖示

## 使用

只同步前端內容：

```powershell
npm.cmd run sync-app
```

同步後直接重新打包：

```powershell
npm.cmd run build:desktop
```

如果只是本機預覽桌面殼：

```powershell
npm.cmd run start
```

`build:desktop` 會先把 `standalone_html_app` 複製到 `app/`，再產生 Windows portable `.exe`。
