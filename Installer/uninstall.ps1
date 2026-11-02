# ============================================================================
# SPACEGLASS -- WINDOWS 11 UNINSTALLATION SCRIPT (Installer/uninstall.ps1)
# Stops the local companion backend, deactivates Rainmeter widgets, removes
# the Windows Startup shortcut, and prompts before deleting user files.
# ============================================================================
$ErrorActionPreference = "Continue"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  SPACEGLASS -- Uninstaller" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan

$AppDataDir   = Join-Path $env:LOCALAPPDATA "SpaceGlass"
$PidFile      = Join-Path $AppDataDir "backend.pid"
$StartupDir   = [Environment]::GetFolderPath("Startup")
$ShortcutLnk  = Join-Path $StartupDir "SpaceGlass.lnk"
$DocumentsDir = [Environment]::GetFolderPath("MyDocuments")
$TargetSkin   = Join-Path $DocumentsDir "Rainmeter\Skins\SpaceGlass"

# 1. Stop running backend process if PID file exists
if (Test-Path $PidFile) {
    $BackendPid = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($BackendPid) {
        Write-Host "[1/4] Stopping SpaceGlass backend process (PID $BackendPid)..." -ForegroundColor Yellow
        Stop-Process -Id ([int]$BackendPid) -Force -ErrorAction SilentlyContinue
    }
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

# 2. Deactivate Rainmeter skins
$RainmeterCandidates = @(
    "$env:ProgramFiles\Rainmeter\Rainmeter.exe",
    "${env:ProgramFiles(x86)}\Rainmeter\Rainmeter.exe"
)
foreach ($exe in $RainmeterCandidates) {
    if (Test-Path $exe) {
        Write-Host "[2/4] Deactivating SpaceGlass widgets in Rainmeter..." -ForegroundColor Yellow
        & $exe "!DeactivateConfig" "SpaceGlass\Clock"
        & $exe "!DeactivateConfig" "SpaceGlass\Calendar"
        & $exe "!DeactivateConfig" "SpaceGlass\Events"
        & $exe "!DeactivateConfig" "SpaceGlass\Tasks"
        & $exe "!DeactivateConfig" "SpaceGlass"
        break
    }
}

# 3. Remove Windows Startup shortcut
if (Test-Path $ShortcutLnk) {
    Write-Host "[3/4] Removing Windows Startup shortcut..." -ForegroundColor Yellow
    Remove-Item $ShortcutLnk -Force
}

# 4. Confirm removal of Rainmeter skin directory and %LOCALAPPDATA%\SpaceGlass
if (Test-Path $TargetSkin) {
    $ConfirmSkin = Read-Host "[4/4] Remove SpaceGlass Rainmeter skin folder at '$TargetSkin'? (y/N)"
    if ($ConfirmSkin -match "^[Yy]$") {
        Remove-Item $TargetSkin -Recurse -Force
        Write-Host "  -> Removed $TargetSkin" -ForegroundColor Green
    }
}

if (Test-Path $AppDataDir) {
    $ConfirmData = Read-Host "Remove stored OAuth tokens, cache, and settings at '$AppDataDir'? (y/N)"
    if ($ConfirmData -match "^[Yy]$") {
        Remove-Item $AppDataDir -Recurse -Force
        Write-Host "  -> Removed $AppDataDir" -ForegroundColor Green
    }
}

Write-Host "`nSpaceGlass uninstallation finished." -ForegroundColor Green
