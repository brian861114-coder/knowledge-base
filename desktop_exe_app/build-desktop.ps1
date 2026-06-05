param(
  [switch]$SyncOnly
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceApp = Join-Path (Split-Path -Parent $projectRoot) "standalone_html_app"
$targetApp = Join-Path $projectRoot "app"
$npmCache = Join-Path $projectRoot ".tmp_npm_cache"
$electronCache = Join-Path $projectRoot ".tmp_electron_cache"
$builderCache = Join-Path $projectRoot ".tmp_builder_cache"

if (!(Test-Path $sourceApp)) {
  throw "Missing source app folder: $sourceApp"
}

if (!(Test-Path $targetApp)) {
  New-Item -ItemType Directory -Path $targetApp | Out-Null
}

Copy-Item (Join-Path $sourceApp "*") $targetApp -Recurse -Force
Write-Host "Synced standalone_html_app -> desktop_exe_app/app"

if ($SyncOnly) {
  exit 0
}

if (!(Test-Path $npmCache)) {
  New-Item -ItemType Directory -Path $npmCache | Out-Null
}

if (!(Test-Path $electronCache)) {
  New-Item -ItemType Directory -Path $electronCache | Out-Null
}

if (!(Test-Path $builderCache)) {
  New-Item -ItemType Directory -Path $builderCache | Out-Null
}

$env:npm_config_cache = $npmCache
$env:ELECTRON_CACHE = $electronCache
$env:ELECTRON_BUILDER_CACHE = $builderCache

if (!(Test-Path (Join-Path $projectRoot "node_modules"))) {
  & npm.cmd install
  if ($LASTEXITCODE -ne 0) {
    throw "npm install failed with exit code $LASTEXITCODE"
  }
}

& npm.cmd run build
if ($LASTEXITCODE -ne 0) {
  throw "npm run build failed with exit code $LASTEXITCODE"
}
