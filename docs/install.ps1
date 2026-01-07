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

# User-friendly variant description
$VariantDesc = if ($Variant -eq "full") { "all modules" } else { "$Variant module" }

if ($Prerelease) {
    Write-Info "Installing semantics ($VariantDesc) - development build..."
} else {
    Write-Info "Installing semantics ($VariantDesc)..."
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

# Resolve $env:TEMP to long path (fixes 8.3 short path issues like C:\Users\TERRY~1.ANE)
$TempBase = (Get-Item $env:TEMP).FullName
$TempDir = Join-Path $TempBase "semantics-install-$PID"

# Function to download and install an executable (silent mode available)
function Install-Executable {
    param(
        [string]$ExeName,
        [string]$FinalName,
        [switch]$Silent
    )
    
    # Build download filename
    # Release format: semantics-v0.1.0-windows-x86_64.zip or semantics-audio-v0.1.0-windows-x86_64.zip
    # Dev format: semantics-windows-x86_64.zip or semantics-audio-windows-x86_64.zip
    if ($Prerelease) {
        $Filename = "$ExeName-$Platform-$Arch.zip"
    } else {
        $Filename = "$ExeName-$Version-$Platform-$Arch.zip"
    }
    
    $Url = "https://github.com/$Repo/releases/download/$Version/$Filename"
    $ZipPath = Join-Path $TempDir $Filename
    $ExtractDir = Join-Path $TempDir "extract_$ExeName"
    
    try {
        Invoke-WebRequest -Uri $Url -OutFile $ZipPath
    } catch {
        Write-Err "Download failed. Check if version '$Version' exists at https://github.com/$Repo/releases"
    }
    
    # Extract
    New-Item -ItemType Directory -Force -Path $ExtractDir | Out-Null
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractDir -Force
    
    # Find the executable in extracted contents
    $ExtractedExe = Get-ChildItem -Path $ExtractDir -Filter "*.exe" | Where-Object { $_.Name -like "semantics*" } | Select-Object -First 1
    if (-not $ExtractedExe) {
        Write-Err "Could not find executable in downloaded archive"
    }
    
    # Install
    Move-Item -Path $ExtractedExe.FullName -Destination (Join-Path $InstallDir $FinalName) -Force
}

try {
    New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
    
    Write-Info "Downloading..."
    
    # Download and install components (silently)
    Install-Executable -ExeName "semantics" -FinalName "semantics.exe" -Silent
    
    # Install the module variant(s)
    if ($Variant -eq "full") {
        # For "full", install all individual modules
        Write-Info "Installing all modules..."
        Install-Executable -ExeName "semantics-audio" -FinalName "semantics-audio.exe" -Silent
        Install-Executable -ExeName "semantics-video" -FinalName "semantics-video.exe" -Silent
        Install-Executable -ExeName "semantics-document" -FinalName "semantics-document.exe" -Silent
    } else {
        Install-Executable -ExeName "semantics-$Variant" -FinalName "semantics-$Variant.exe" -Silent
    }
    
    Write-Info "Installing..."
    
    # Add to PATH
    if ($env:GITHUB_ACTIONS) {
        # GitHub Actions: add to GITHUB_PATH
        $InstallDir | Out-File -FilePath $env:GITHUB_PATH -Append -Encoding utf8
        $env:Path = "$InstallDir;$env:Path"
    } else {
        # Regular install: add to user PATH if not already there
        $UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if ($UserPath -notlike "*$InstallDir*") {
            [Environment]::SetEnvironmentVariable("Path", "$UserPath;$InstallDir", "User")
            $env:Path = "$env:Path;$InstallDir"
        }
    }
    
    # Verify installation
    Write-Info "Installation complete!"
    Write-Host ""
    $LauncherExe = Join-Path $InstallDir "semantics.exe"
    & $LauncherExe --version
    
    Write-Host ""
    Write-Host "Restart your terminal or run:" -ForegroundColor Yellow
    Write-Host "  `$env:Path = [Environment]::GetEnvironmentVariable('Path', 'User')"
    Write-Host ""
    if ($Variant -eq "full") {
        Write-Host "Usage: semantics audio --help"
        Write-Host "       semantics video --help"
        Write-Host "       semantics document --help"
    } else {
        Write-Host "Usage: semantics $Variant --help"
    }
}
finally {
    # Cleanup temp directory
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue
    }
}

