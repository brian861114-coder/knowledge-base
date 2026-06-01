$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$preferredPython = "C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$url = "http://127.0.0.1:4173/prototype/"

if (Test-Path $preferredPython) {
    $pythonExe = $preferredPython
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonExe = (Get-Command py).Source
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonExe = (Get-Command python).Source
} else {
    throw "Python executable not found. Install Python or update start_prototype.ps1."
}

$existing = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 4173 -State Listen -ErrorAction SilentlyContinue
if (-not $existing) {
    $pythonArgs = if ([System.IO.Path]::GetFileName($pythonExe).ToLowerInvariant() -eq "py.exe") {
        "-3", "-m", "http.server", "4173", "--bind", "127.0.0.1"
    } else {
        "-m", "http.server", "4173", "--bind", "127.0.0.1"
    }

    Start-Process -FilePath $pythonExe `
        -ArgumentList $pythonArgs `
        -WorkingDirectory $projectRoot `
        -WindowStyle Hidden | Out-Null
    Start-Sleep -Milliseconds 800
}

Start-Process $url
Write-Output "Prototype opened at $url"
