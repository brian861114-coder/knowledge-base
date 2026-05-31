$ErrorActionPreference = "Stop"

$projectRoot = "C:\Users\brian\Downloads\vibe_coding\knowledge_map"
$pythonExe = "C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$url = "http://127.0.0.1:4173/prototype/"

$existing = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 4173 -State Listen -ErrorAction SilentlyContinue
if (-not $existing) {
    Start-Process -FilePath $pythonExe `
        -ArgumentList "-m", "http.server", "4173", "--bind", "127.0.0.1" `
        -WorkingDirectory $projectRoot `
        -WindowStyle Hidden | Out-Null
    Start-Sleep -Milliseconds 800
}

Start-Process $url
Write-Output "Prototype opened at $url"
