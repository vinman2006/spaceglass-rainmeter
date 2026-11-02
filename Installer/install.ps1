# ============================================================================
# SPACEGLASS -- WINDOWS 11 POWERSHELL INSTALLER (Installer/install.ps1)
# - Checks Python 3.11+ availability
# - Checks Rainmeter availability
# - Installs Python dependencies from Backend/requirements.txt
# - Creates protected %LOCALAPPDATA%\SpaceGlass directory
# - Prompts for confirmation before overwriting existing Rainmeter skins
# - Copies SpaceGlass skin and Backend to Rainmeter Skins folder
# - Configures optional Windows Startup shortcut
# ============================================================================
param(
    [switch]$Unattended = $false
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  SPACEGLASS v1.0.0 -- Windows 11 Desktop Widget System Installer" -ForegroundColor Cyan
Write-Host "  Tagline: Your Universe. Your Schedule." -ForegroundColor Gray
Write-Host "============================================================================" -ForegroundColor Cyan

$InstallerDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SourceRoot   = Split-Path -Parent $InstallerDir

# 1. Verify Python 3.11+ availability
Write-Host "`n[1/7] Checking Python 3.11+ availability..." -ForegroundColor Yellow
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    Write-Host "ERROR: Python was not found in PATH. Install Python 3.11 or newer from https://www.python.org/downloads/ and check 'Add Python to PATH'." -ForegroundColor Red
    exit 1
}

$PyVerOutput = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$PyParts = $PyVerOutput.Split(".")
if ([int]$PyParts[0] -lt 3 -or ([int]$PyParts[0] -eq 3 -and [int]$PyParts[1] -lt 11)) {
    Write-Host "ERROR: SpaceGlass requires Python 3.11 or newer (found Python $PyVerOutput)." -ForegroundColor Red
    exit 1
}
Write-Host "  -> Found Python $PyVerOutput" -ForegroundColor Green

# 2. Verify Rainmeter availability
Write-Host "`n[2/7] Checking Rainmeter installation..." -ForegroundColor Yellow
$RainmeterCandidates = @(
    "$env:ProgramFiles\Rainmeter\Rainmeter.exe",
    "${env:ProgramFiles(x86)}\Rainmeter\Rainmeter.exe"
)
$RainmeterExe = $null
foreach ($candidate in $RainmeterCandidates) {
    if (Test-Path $candidate) {
        $RainmeterExe = $candidate
        break
    }
}
if (-not $RainmeterExe) {
    Write-Host "WARNING: Rainmeter.exe was not found in standard Program Files directories." -ForegroundColor Magenta
    Write-Host "         Download and install Rainmeter 4.5+ from https://www.rainmeter.net/ to display the desktop widgets." -ForegroundColor Magenta
} else {
    Write-Host "  -> Found Rainmeter at: $RainmeterExe" -ForegroundColor Green
}

# 3. Install Python dependencies
Write-Host "`n[3/7] Installing Python backend dependencies..." -ForegroundColor Yellow
$ReqFile = Join-Path $SourceRoot "Backend\requirements.txt"
& python -m pip install --upgrade pip --quiet
& python -m pip install -r $ReqFile
Write-Host "  -> Python packages installed successfully." -ForegroundColor Green

# 4. Create %LOCALAPPDATA%\SpaceGlass protected storage directory
Write-Host "`n[4/7] Creating protected application data directory..." -ForegroundColor Yellow
$AppDataDir = Join-Path $env:LOCALAPPDATA "SpaceGlass"
if (-not (Test-Path $AppDataDir)) {
    New-Item -ItemType Directory -Path $AppDataDir -Force | Out-Null
}
$DefaultSettings = Join-Path $AppDataDir "settings.json"
$ExampleSettings = Join-Path $SourceRoot "Config\settings.example.json"
if (-not (Test-Path $DefaultSettings) -and (Test-Path $ExampleSettings)) {
    Copy-Item $ExampleSettings $DefaultSettings
    Write-Host "  -> Initialized default settings at $DefaultSettings" -ForegroundColor Green
} else {
    Write-Host "  -> Preserved existing user settings in $AppDataDir" -ForegroundColor Green
}

# 5. Copy SpaceGlass skin to Rainmeter Skins folder (with overwrite confirmation)
Write-Host "`n[5/7] Installing SpaceGlass Rainmeter skin..." -ForegroundColor Yellow
$DocumentsDir = [Environment]::GetFolderPath("MyDocuments")
$SkinsRoot    = Join-Path $DocumentsDir "Rainmeter\Skins"
$TargetSkin   = Join-Path $SkinsRoot "SpaceGlass"

if (-not (Test-Path $SkinsRoot)) {
    New-Item -ItemType Directory -Path $SkinsRoot -Force | Out-Null
}

$ProceedCopy = $true
if ((Test-Path $TargetSkin) -and (-not $Unattended)) {
    $Confirm = Read-Host "SpaceGlass skin folder already exists at '$TargetSkin'. Overwrite skin files? (y/N)"
    if ($Confirm -notmatch "^[Yy]$") {
        Write-Host "  -> Skipped overwriting existing Rainmeter skin files." -ForegroundColor Yellow
        $ProceedCopy = $false
    }
}

if ($ProceedCopy) {
    if (-not (Test-Path $TargetSkin)) {
        New-Item -ItemType Directory -Path $TargetSkin -Force | Out-Null
    }
    $FoldersToCopy = @("Clock", "Calendar", "Events", "Tasks", "@Resources", "Backend", "Installer", "Config")
    foreach ($folder in $FoldersToCopy) {
        $src = Join-Path $SourceRoot $folder
        $dst = Join-Path $TargetSkin $folder
        if (Test-Path $src) {
            Copy-Item -Path $src -Destination $dst -Recurse -Force
        }
    }
    Copy-Item -Path (Join-Path $SourceRoot "SpaceGlass.ini") -Destination (Join-Path $TargetSkin "SpaceGlass.ini") -Force
    Write-Host "  -> Installed SpaceGlass skin to: $TargetSkin" -ForegroundColor Green
}

# 6. Configure Windows Startup Shortcut
Write-Host "`n[6/7] Configuring Windows Startup integration..." -ForegroundColor Yellow
$EnableStartup = $true
if (-not $Unattended) {
    $StartupReply = Read-Host "Start SpaceGlass backend automatically when Windows 11 signs in? (Y/n)"
    if ($StartupReply -match "^[Nn]$") {
        $EnableStartup = $false
    }
}
if ($EnableStartup) {
    $StartupDir  = [Environment]::GetFolderPath("Startup")
    $ShortcutLnk = Join-Path $StartupDir "SpaceGlass.lnk"
    $VbsPath     = Join-Path $TargetSkin "Installer\start_spaceglass.vbs"
    if (-not (Test-Path $VbsPath)) {
        $VbsPath = Join-Path $SourceRoot "Installer\start_spaceglass.vbs"
    }
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutLnk)
    $Shortcut.TargetPath = "wscript.exe"
    $Shortcut.Arguments  = "`"$VbsPath`""
    $Shortcut.WorkingDirectory = Split-Path -Parent $VbsPath
    $Shortcut.Description = "SpaceGlass Companion Backend Launcher"
    $Shortcut.Save()
    Write-Host "  -> Created Windows Startup shortcut: $ShortcutLnk" -ForegroundColor Green
}

# 7. Start Backend and Activate Widgets in Rainmeter
Write-Host "`n[7/7] Starting SpaceGlass companion backend & activating widgets..." -ForegroundColor Yellow
$VbsToRun = Join-Path $TargetSkin "Installer\start_spaceglass.vbs"
if (-not (Test-Path $VbsToRun)) {
    $VbsToRun = Join-Path $SourceRoot "Installer\start_spaceglass.vbs"
}
Start-Process "wscript.exe" -ArgumentList "`"$VbsToRun`""

if ($RainmeterExe) {
    & $RainmeterExe "!RefreshApp"
    Start-Sleep -Seconds 1
    & $RainmeterExe "!ActivateConfig" "SpaceGlass\Clock" "Clock.ini"
    & $RainmeterExe "!ActivateConfig" "SpaceGlass\Calendar" "Calendar.ini"
    & $RainmeterExe "!ActivateConfig" "SpaceGlass\Events" "Events.ini"
    & $RainmeterExe "!ActivateConfig" "SpaceGlass\Tasks" "Tasks.ini"
    Write-Host "  -> Activated Clock, Calendar, Events, and Tasks widgets in Rainmeter." -ForegroundColor Green
}

Write-Host "`n============================================================================" -ForegroundColor Cyan
Write-Host "  SPACEGLASS INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "  Next Step: Place your Google OAuth Desktop 'credentials.json' in:" -ForegroundColor White
Write-Host "             $AppDataDir\credentials.json" -ForegroundColor Yellow
Write-Host "  Then right-click any SpaceGlass widget -> 'SpaceGlass Settings...' ->" -ForegroundColor White
Write-Host "  GOOGLE tab -> 'Connect Google Account'." -ForegroundColor White
Write-Host "============================================================================" -ForegroundColor Cyan
