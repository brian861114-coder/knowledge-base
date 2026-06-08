param(
    [Parameter(Mandatory = $true)]
    [string]$SessionDir,
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 8766,
    [string]$LogDir = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = "C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$resolvedLogDir = if ([string]::IsNullOrWhiteSpace($LogDir)) { Join-Path $repoRoot "tmp\review_logs" } else { $LogDir }
$stdoutLog = Join-Path $resolvedLogDir "review_server_${Port}_stdout.log"
$stderrLog = Join-Path $resolvedLogDir "review_server_${Port}_stderr.log"

Set-Location $repoRoot
New-Item -ItemType Directory -Force -Path $resolvedLogDir | Out-Null
"[$(Get-Date -Format o)] Starting review server for $SessionDir on ${BindHost}:$Port" | Out-File -FilePath $stdoutLog -Encoding utf8 -Append
try {
    & $python tools\review_server.py --session-dir $SessionDir --host $BindHost --port $Port 1>> $stdoutLog 2>> $stderrLog
}
catch {
    $_ | Out-File -FilePath $stderrLog -Encoding utf8 -Append
    throw
}
