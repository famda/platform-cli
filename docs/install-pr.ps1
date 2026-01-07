# Semantics PR installer script for Windows
# Requires GitHub CLI (gh) to be installed and authenticated
# Usage: iex "& { $(irm https://raw.githubusercontent.com/famda/platform-cli/main/docs/install-pr.ps1) } -PRNumber 123"
# Usage: iex "& { $(irm https://raw.githubusercontent.com/famda/platform-cli/main/docs/install-pr.ps1) } -PRNumber 123 -Variant audio"

param(
    [Parameter(Mandatory=$true)]
    [int]$PRNumber,
    [ValidateSet("full", "audio", "video", "document")]
    [string]$Variant = "full"
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

# Determine executable name based on variant
if ($Variant -eq "full") {
    $ExeName = "semantics"
} else {
    $ExeName = "semantics-$Variant"
}

Write-Info "Installing $ExeName from PR #$PRNumber..."

# Get the PR's head commit SHA
Write-Info "Finding PR workflow run..."
$prInfo = gh pr view $PRNumber --repo $Repo --json headRefOid | ConvertFrom-Json
$headSha = $prInfo.headRefOid
Write-Info "PR head commit: $($headSha.Substring(0, 7))"

# Find the workflow run for this PR
$runs = gh run list --repo $Repo --workflow "PR Build" --json databaseId,headSha,status,conclusion | ConvertFrom-Json
$matchingRun = $runs | Where-Object { $_.headSha -eq $headSha -and $_.status -eq "completed" -and $_.conclusion -eq "success" } | Select-Object -First 1

if (-not $matchingRun) {
    Write-Err "No successful PR Build workflow found for PR #$PRNumber. The build may still be running or failed."
}

$runId = $matchingRun.databaseId
Write-Info "Found workflow run: $runId"

# Determine artifact name
$Arch = if ([Environment]::Is64BitOperatingSystem) { "x86_64" } else { "x86" }
$ArtifactName = "$ExeName-pr-$PRNumber-windows-$Arch"

# Create temp directory
$TempBase = (Get-Item $env:TEMP).FullName
$TempDir = Join-Path $TempBase "semantics-pr-install-$PID"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

try {
    # Download artifact using gh
    Write-Info "Downloading artifact: $ArtifactName..."
    Push-Location $TempDir
    gh run download $runId --repo $Repo --name $ArtifactName
    Pop-Location

    # Find and extract the zip
    $ZipFile = Get-ChildItem -Path $TempDir -Filter "*.zip" -Recurse | Select-Object -First 1
    if (-not $ZipFile) {
        Write-Err "No zip file found in downloaded artifact"
    }

    Write-Info "Extracting..."
    Expand-Archive -Path $ZipFile.FullName -DestinationPath $TempDir -Force

    # Find the executable
    $ExtractedExe = Get-ChildItem -Path $TempDir -Filter "*.exe" | Where-Object { $_.Name -like "semantics*" } | Select-Object -First 1
    if (-not $ExtractedExe) {
        Write-Err "Could not find executable in downloaded archive"
    }

    # Install
    Write-Info "Installing to $InstallDir..."
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

    # Use variant-specific name
    $FinalExeName = if ($Variant -eq "full") { "semantics.exe" } else { "semantics-$Variant.exe" }
    Move-Item -Path $ExtractedExe.FullName -Destination (Join-Path $InstallDir $FinalExeName) -Force

    # Add to PATH if not already there
    $UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($UserPath -notlike "*$InstallDir*") {
        Write-Info "Adding $InstallDir to PATH..."
        [Environment]::SetEnvironmentVariable("Path", "$UserPath;$InstallDir", "User")
        $env:Path = "$env:Path;$InstallDir"
    }

    # Verify
    $InstalledExe = Join-Path $InstallDir $FinalExeName
    Write-Info "Successfully installed $ExeName from PR #$PRNumber!"
    & $InstalledExe --version

    Write-Host ""
    Write-Host "Restart your terminal or run:" -ForegroundColor Yellow
    Write-Host "  `$env:Path = [Environment]::GetEnvironmentVariable('Path', 'User')"
}
finally {
    # Cleanup
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir
    }
}
