$ErrorActionPreference = "Stop"

# ============================================================
#  Prototype Semantic Lens — PowerShell 啟動器
#  支援設定檔覆寫、自動關閉舊 server、Health check
# ============================================================

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$configPath = Join-Path $scriptRoot ".knowledge-base.local.json"
$config = $null

if (Test-Path $configPath) {
    try { $config = Get-Content $configPath -Raw | ConvertFrom-Json } catch {}
}

# --- 設定 ---
$bindHost = if ($env:KB_PROTOTYPE_HOST) {
    $env:KB_PROTOTYPE_HOST
} elseif ($config -and $config.prototypeHost) {
    $config.prototypeHost
} else {
    "127.0.0.1"
}

$port = if ($env:KB_PROTOTYPE_PORT) {
    [int]$env:KB_PROTOTYPE_PORT
} elseif ($config -and $config.prototypePort) {
    [int]$config.prototypePort
} else {
    4173
}

$url = "http://${bindHost}:${port}/prototype_semantic_lens/index.html"

# --- 尋找 Python ---
$pythonCandidates = @(
    "python",                            # PATH 中的 python（最高優先）
    "python3",
    $env:KB_PYTHON_PATH,
    $config.pythonPath,
    "C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
) | Where-Object { $_ -and (Get-Command $_ -ErrorAction SilentlyContinue) }

$pythonExe = $pythonCandidates | Select-Object -First 1

if (-not $pythonExe) {
    Write-Host "[Semantic Lens] 錯誤：找不到 Python。請安裝 Python 或設定 KB_PYTHON_PATH 環境變數。" -ForegroundColor Red
    Read-Host "按 Enter 結束"
    exit 1
}

Write-Host "[Semantic Lens] 使用 Python: $pythonExe"

# --- 關閉舊 server ---
$existing = Get-NetTCPConnection -LocalAddress $bindHost -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    $oldPid = $existing.OwningProcess
    Write-Host "[Semantic Lens] 關閉舊 server (PID $oldPid)..."
    Stop-Process -Id $oldPid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
}

# --- 啟動 HTTP server ---
$pythonFileName = [System.IO.Path]::GetFileName($pythonExe)
$pythonArgs = @("-m", "http.server", "$port", "--bind", $bindHost)

Write-Host "[Semantic Lens] 啟動 HTTP server (port $port)..."
$proc = Start-Process -FilePath $pythonExe `
    -ArgumentList $pythonArgs `
    -WorkingDirectory $scriptRoot `
    -WindowStyle Minimized `
    -PassThru

# --- Health check ---
$ready = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
        # 繼續等待
    }
}

if (-not $ready) {
    Write-Host "[Semantic Lens] 警告：伺服器啟動較慢，仍嘗試開啟瀏覽器..." -ForegroundColor Yellow
}

# --- 開啟瀏覽器 ---
Start-Process $url
Write-Host "[Semantic Lens] 已開啟 $url" -ForegroundColor Green
