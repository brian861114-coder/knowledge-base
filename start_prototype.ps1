$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$configPath = Join-Path $projectRoot ".knowledge-base.local.json"
$config = $null

if (Test-Path $configPath) {
    $config = Get-Content $configPath -Raw | ConvertFrom-Json
}

$preferredPython = if ($env:KB_PYTHON_PATH) {
    $env:KB_PYTHON_PATH
} elseif ($config -and $config.pythonPath) {
    $config.pythonPath
} else {
    "C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
}

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

$url = "http://${bindHost}:${port}/prototype/"

if (Test-Path $preferredPython) {
    $pythonExe = $preferredPython
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonExe = (Get-Command py).Source
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonExe = (Get-Command python).Source
} else {
    throw "Python executable not found. Install Python, set KB_PYTHON_PATH, or update .knowledge-base.local.json."
}

$existing = Get-NetTCPConnection -LocalAddress $bindHost -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if (-not $existing) {
    $pythonArgs = if ([System.IO.Path]::GetFileName($pythonExe).ToLowerInvariant() -eq "py.exe") {
        "-3", "-m", "http.server", "$port", "--bind", $bindHost
    } else {
        "-m", "http.server", "$port", "--bind", $bindHost
    }

    Start-Process -FilePath $pythonExe `
        -ArgumentList $pythonArgs `
        -WorkingDirectory $projectRoot `
        -WindowStyle Hidden | Out-Null
    Start-Sleep -Milliseconds 800
}

Start-Process $url
Write-Output "Prototype opened at $url"
