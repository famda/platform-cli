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

if ($Prerelease) {
    Write-Info "Installing semantics with $Variant module (development build)..."
} else {
    Write-Info "Installing semantics with $Variant module..."
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

# Function to download and install an executable
function Install-Executable {
    param(
        [string]$ExeName,
        [string]$FinalName
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
    
    Write-Info "Downloading $ExeName..."
    
    try {
        Invoke-WebRequest -Uri $Url -OutFile $ZipPath
    } catch {
        Write-Err "Download failed for $ExeName. Check if version '$Version' exists at https://github.com/$Repo/releases"
    }
    
    # Extract
    Write-Info "Extracting $ExeName..."
    New-Item -ItemType Directory -Force -Path $ExtractDir | Out-Null
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractDir -Force
    
    # Find the executable in extracted contents
    $ExtractedExe = Get-ChildItem -Path $ExtractDir -Filter "*.exe" | Where-Object { $_.Name -like "semantics*" } | Select-Object -First 1
    if (-not $ExtractedExe) {
        Write-Err "Could not find executable in downloaded archive for $ExeName"
    }
    
    # Install
    Move-Item -Path $ExtractedExe.FullName -Destination (Join-Path $InstallDir $FinalName) -Force
    Write-Info "Installed: $FinalName"
}

try {
    New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
    
    # Always install the launcher first (unified 'semantics' command)
    Install-Executable -ExeName "semantics" -FinalName "semantics.exe"
    
    # Install the module variant
    if ($Variant -eq "full") {
        # Full variant includes all modules in one executable
        Install-Executable -ExeName "semantics-full" -FinalName "semantics-full.exe"
        Write-Info "Full version installed. Use 'semantics audio', 'semantics video', or 'semantics document'."
    } else {
        # Individual module variant
        Install-Executable -ExeName "semantics-$Variant" -FinalName "semantics-$Variant.exe"
    }
    
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
    
    # Verify installation
    Write-Info "Installation complete!"
    $LauncherExe = Join-Path $InstallDir "semantics.exe"
    & $LauncherExe --version
    
    Write-Host ""
    Write-Info "Installed executables:"
    Get-ChildItem -Path $InstallDir -Filter "semantics*.exe" | ForEach-Object { Write-Host "  $($_.Name)" }
    
    Write-Host ""
    Write-Host "Restart your terminal or run:" -ForegroundColor Yellow
    Write-Host "  `$env:Path = [Environment]::GetEnvironmentVariable('Path', 'User')"
    Write-Host ""
    Write-Host "Then use: semantics $Variant --help"
}
finally {
    # Cleanup temp directory
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue
    }
}

