@echo off
setlocal enabledelayedexpansion

:: ============================================================
::  Prototype Semantic Lens — 啟動器
::  用 HTTP 伺服器開啟（避免 file:// 封鎖 ES module）
:: ============================================================

set "PORT=4173"
set "BIND=127.0.0.1"
set "URL=http://%BIND%:%PORT%/prototype_semantic_lens/index.html"

echo [Semantic Lens] 正在啟動...

:: --- 1. 先關閉佔用 PORT 的舊 server ---
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT% " ^| findstr "LISTENING" 2^>nul') do (
    echo [Semantic Lens] 關閉舊 server (PID %%a)...
    taskkill /PID %%a /F >nul 2>&1
    timeout /t 1 /nobreak >nul
)

:: --- 2. 啟動 HTTP server ---
cd /d "%~dp0"
start "SemanticLensServer" /MIN python -m http.server %PORT% --bind %BIND%

:: --- 3. 等待 server 就緒 ---
echo [Semantic Lens] 等待伺服器就緒...
set "READY=0"
for /L %%i in (1,1,15) do (
    timeout /t 1 /nobreak >nul
    curl -s -o NUL -w "%%{http_code}" "%URL%" 2>nul | findstr "200" >nul && set "READY=1" && goto :open
)
echo [Semantic Lens] 警告：伺服器啟動較慢，仍嘗試開啟瀏覽器...

:open
:: --- 4. 開啟瀏覽器 ---
start "" "%URL%"
echo [Semantic Lens] 已開啟 %URL%
echo [Semantic Lens] 提示：若頁面無法載入，請確認 Python 已安裝（python --version）

endlocal
