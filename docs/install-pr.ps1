# Semantics PR installer script for Windows
# Requires GitHub CLI (gh) to be installed and authenticated
# Usage: iex "& { $(irm https://raw.githubusercontent.com/famda/platform-cli/main/docs/install-pr.ps1) } -PRNumber 123"
# Usage: iex "& { $(irm https://raw.githubusercontent.com/famda/platform-cli/main/docs/install-pr.ps1) } -PRNumber 123 -Variant audio"

param(
    [Parameter(Mandatory=$true)]
    [int]$PRNumber,
    [ValidateSet("all", "audio", "video", "document")]
    [string]$Variant = ""
)

$ErrorActionPreference = "Stop"

$Repo = "famda/platform-cli"
$InstallDir = "$env:LOCALAPPDATA\semantics"

function Write-Info { param($msg) Write-Host "==> " -ForegroundColor Green -NoNewline; Write-Host $msg }
function Write-Warn { param($msg) Write-Host "warning: " -ForegroundColor Yellow -NoNewline; Write-Host $msg }
function Write-Err { param($msg) Write-Host "error: " -ForegroundColor Red -NoNewline; Write-Host $msg; exit 1 }

# Check for gh CLI
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Err "GitHub CLI (gh) is required. Install from https://cli.github.com/"
}

# Check gh auth status
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Err "GitHub CLI not authenticated. Run 'gh auth login' first."
}

# Default to all modules if no variant specified
if ([string]::IsNullOrEmpty($Variant)) {
    $Variant = "all"
}

# User-friendly variant description
$VariantDesc = if ($Variant -eq "all") { "all modules" } else { "$Variant module" }

Write-Info "Installing semantics ($VariantDesc) from PR #$PRNumber..."

# Get the PR's head commit SHA
Write-Info "Finding PR workflow run..."
$prInfo = gh pr view $PRNumber --repo $Repo --json headRefOid | ConvertFrom-Json
$headSha = $prInfo.headRefOid

# Find the workflow run for this PR
$runs = gh run list --repo $Repo --workflow "PR Build" --json databaseId,headSha,status,conclusion | ConvertFrom-Json
$matchingRun = $runs | Where-Object { $_.headSha -eq $headSha -and $_.status -eq "completed" -and $_.conclusion -eq "success" } | Select-Object -First 1

if (-not $matchingRun) {
    Write-Err "No successful PR Build workflow found for PR #$PRNumber. The build may still be running or failed."
}

$runId = $matchingRun.databaseId

# Determine architecture
$Arch = if ([Environment]::Is64BitOperatingSystem) { "x86_64" } else { "x86" }

# Create temp directory
$TempBase = (Get-Item $env:TEMP).FullName
$TempDir = Join-Path $TempBase "semantics-pr-install-$PID"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

# Function to download and install an artifact (silent)
function Install-Artifact {
    param(
        [string]$ArtifactName,
        [string]$FinalName
    )
    
    $ExtractDir = Join-Path $TempDir "extract_$FinalName"
    New-Item -ItemType Directory -Force -Path $ExtractDir | Out-Null
    
    Push-Location $TempDir
    try {
        gh run download $runId --repo $Repo --name $ArtifactName --dir $ExtractDir 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Download failed"
        }
    } catch {
        Write-Err "Failed to download. Make sure the PR build completed successfully."
    }
    Pop-Location
    
    # Find and extract the zip
    $ZipFile = Get-ChildItem -Path $ExtractDir -Filter "*.zip" -Recurse | Select-Object -First 1
    if (-not $ZipFile) {
        Write-Err "Could not find downloaded artifact"
    }
    
    Expand-Archive -Path $ZipFile.FullName -DestinationPath $ExtractDir -Force
    
    # Find the executable
    $ExtractedExe = Get-ChildItem -Path $ExtractDir -Filter "*.exe" | Where-Object { $_.Name -like "semantics*" } | Select-Object -First 1
    if (-not $ExtractedExe) {
        Write-Err "Could not find executable in downloaded archive"
    }
    
    Move-Item -Path $ExtractedExe.FullName -Destination (Join-Path $InstallDir $FinalName) -Force
}

try {
    Write-Info "Downloading..."
    
    # Download and install components (silently)
    $LauncherArtifact = "semantics-pr-$PRNumber-windows-$Arch"
    Install-Artifact -ArtifactName $LauncherArtifact -FinalName "semantics.exe"
    
    # Install the module variant(s)
    if ($Variant -eq "all") {
        # Install all individual modules
        Write-Info "Installing all modules..."
        $AudioArtifact = "semantics-audio-pr-$PRNumber-windows-$Arch"
        Install-Artifact -ArtifactName $AudioArtifact -FinalName "semantics-audio.exe"
        $VideoArtifact = "semantics-video-pr-$PRNumber-windows-$Arch"
        Install-Artifact -ArtifactName $VideoArtifact -FinalName "semantics-video.exe"
        $DocumentArtifact = "semantics-document-pr-$PRNumber-windows-$Arch"
        Install-Artifact -ArtifactName $DocumentArtifact -FinalName "semantics-document.exe"
    } else {
        $ModuleArtifact = "semantics-$Variant-pr-$PRNumber-windows-$Arch"
        Install-Artifact -ArtifactName $ModuleArtifact -FinalName "semantics-$Variant.exe"
    }
    
    Write-Info "Installing..."

    # Add to PATH if not already there
    $UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($UserPath -notlike "*$InstallDir*") {
        [Environment]::SetEnvironmentVariable("Path", "$UserPath;$InstallDir", "User")
        $env:Path = "$env:Path;$InstallDir"
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
    if ($Variant -eq "all") {
        Write-Host "Usage: semantics audio --help"
        Write-Host "       semantics video --help"
        Write-Host "       semantics document --help"
    } else {
        Write-Host "Usage: semantics $Variant --help"
    }
}
finally {
    # Cleanup
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue
    }
}
