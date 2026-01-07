# Semantics installer script for Windows
# Usage: irm https://raw.githubusercontent.com/famda/platform-cli/main/docs/install.ps1 | iex
# Usage: iex "& { $(irm https://raw.githubusercontent.com/famda/platform-cli/main/docs/install.ps1) } -Prerelease"
# Usage: iex "& { $(irm https://raw.githubusercontent.com/famda/platform-cli/main/docs/install.ps1) } -Variant audio"

param(
    [switch]$Prerelease,
    [ValidateSet("full", "audio", "video", "document")]
    [string]$Variant = "full"
)

$ErrorActionPreference = "Stop"

$Repo = "famda/platform-cli"
$InstallDir = "$env:LOCALAPPDATA\semantics"

function Write-Info { param($msg) Write-Host "==> " -ForegroundColor Green -NoNewline; Write-Host $msg }
function Write-Warn { param($msg) Write-Host "warning: " -ForegroundColor Yellow -NoNewline; Write-Host $msg }
function Write-Err { param($msg) Write-Host "error: " -ForegroundColor Red -NoNewline; Write-Host $msg; exit 1 }

# Determine executable name based on variant
if ($Variant -eq "full") {
    $ExeName = "semantics"
} else {
    $ExeName = "semantics-$Variant"
}

if ($Prerelease) {
    Write-Info "Installing $ExeName (development build)..."
} else {
    Write-Info "Installing $ExeName..."
}

# Detect platform
$Arch = if ([Environment]::Is64BitOperatingSystem) { "x86_64" } else { "x86" }
$Platform = "windows"

# Get release version
try {
    if ($Prerelease) {
        # Dev prerelease always uses 'dev' tag - no API call needed
        $Version = "dev"
        Write-Info "Development build: $Version"
    } else {
        $Release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest"
        $Version = $Release.tag_name
        Write-Info "Latest version: $Version"
    }
} catch {
    Write-Err "Could not determine latest version. Check https://github.com/$Repo/releases"
}

# Build download filename
# Release format: semantics-v0.1.0-windows-x86_64.zip or semantics-audio-v0.1.0-windows-x86_64.zip
# Dev format: semantics-windows-x86_64.zip or semantics-audio-windows-x86_64.zip
if ($Prerelease) {
    $Filename = "$ExeName-$Platform-$Arch.zip"
} else {
    $Filename = "$ExeName-$Version-$Platform-$Arch.zip"
}

$Url = "https://github.com/$Repo/releases/download/$Version/$Filename"

# Resolve $env:TEMP to long path (fixes 8.3 short path issues like C:\Users\TERRY~1.ANE)
$TempBase = (Get-Item $env:TEMP).FullName
$TempDir = Join-Path $TempBase "semantics-install-$PID"
$ZipPath = Join-Path $TempDir $Filename

Write-Info "Downloading $Url..."

New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
try {
    Invoke-WebRequest -Uri $Url -OutFile $ZipPath

    # Extract
    Write-Info "Extracting..."
    Expand-Archive -Path $ZipPath -DestinationPath $TempDir -Force

    # Find the executable in extracted contents
    $ExtractedExe = Get-ChildItem -Path $TempDir -Filter "*.exe" | Where-Object { $_.Name -like "semantics*" } | Select-Object -First 1
    if (-not $ExtractedExe) {
        Write-Err "Could not find executable in downloaded archive"
    }

    # Install
    Write-Info "Installing to $InstallDir..."
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

    # Determine final executable name (always use semantics.exe for full, semantics-variant.exe for others)
    $FinalExeName = if ($Variant -eq "full") { "semantics.exe" } else { "semantics-$Variant.exe" }
    Move-Item -Path $ExtractedExe.FullName -Destination (Join-Path $InstallDir $FinalExeName) -Force

    # Add to PATH
    if ($env:GITHUB_ACTIONS) {
        # GitHub Actions: add to GITHUB_PATH
        Write-Info "Adding to GITHUB_PATH for this workflow..."
        $InstallDir | Out-File -FilePath $env:GITHUB_PATH -Append -Encoding utf8
        $env:Path = "$InstallDir;$env:Path"
    } else {
        # Regular install: add to user PATH if not already there
        $UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if ($UserPath -notlike "*$InstallDir*") {
            Write-Info "Adding $InstallDir to PATH..."
            [Environment]::SetEnvironmentVariable("Path", "$UserPath;$InstallDir", "User")
            $env:Path = "$env:Path;$InstallDir"
        }
    }

    # Verify
    $InstalledExe = Join-Path $InstallDir $FinalExeName
    Write-Info "Successfully installed $ExeName!"
    & $InstalledExe version

    Write-Host ""
    Write-Host "Restart your terminal or run:" -ForegroundColor Yellow
    Write-Host "  `$env:Path = [Environment]::GetEnvironmentVariable('Path', 'User')"
}
catch {
    Write-Err "Download failed. Check if version '$Version' exists at https://github.com/$Repo/releases"
}
finally {
    # Cleanup temp directory
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue
    }
}

