#!/bin/bash
# Semantics PR installer script for Linux/macOS
# Requires GitHub CLI (gh) to be installed and authenticated
# Usage: curl -fsSL https://raw.githubusercontent.com/famda/platform-cli/main/docs/install-pr.sh | bash -s -- <pr_number>
# Usage: curl -fsSL https://raw.githubusercontent.com/famda/platform-cli/main/docs/install-pr.sh | bash -s -- <pr_number> --variant audio

set -e

REPO="famda/platform-cli"
INSTALL_DIR="$HOME/.semantics/bin"
VARIANT="full"
PR_NUMBER=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --variant|-v)
            if [ -z "${2-}" ] || [[ "$2" == -* ]]; then
                echo "error: --variant requires a value"
                echo "Usage: $0 <pr_number> [--variant <full|audio|video|document>]"
                exit 1
            fi
            VARIANT="$2"
            shift 2
            ;;
        *)
            if [ -z "$PR_NUMBER" ]; then
                PR_NUMBER="$1"
            else
                echo "Unknown option: $1"
                exit 1
            fi
            shift
            ;;
    esac
done

if [ -z "$PR_NUMBER" ]; then
    echo "Usage: $0 <pr_number> [--variant <full|audio|video|document>]"
    echo ""
    echo "Examples:"
    echo "  $0 42"
    echo "  $0 42 --variant audio"
    exit 1
fi

# Validate variant
case $VARIANT in
    full|audio|video|document) ;;
    *)
        echo "error: Invalid variant '$VARIANT'. Must be one of: full, audio, video, document"
        exit 1
        ;;
esac

info() { echo -e "\033[32m==>\033[0m $1"; }
warn() { echo -e "\033[33mwarning:\033[0m $1"; }
error() { echo -e "\033[31merror:\033[0m $1"; exit 1; }

# Check for gh CLI
if ! command -v gh &> /dev/null; then
    error "GitHub CLI (gh) is required. Install from https://cli.github.com/"
fi

# Check gh auth status
if ! gh auth status &> /dev/null; then
    error "GitHub CLI not authenticated. Run 'gh auth login' first."
fi

# User-friendly variant description
if [ "$VARIANT" = "full" ]; then
    VARIANT_DESC="all modules"
else
    VARIANT_DESC="$VARIANT module"
fi

info "Installing semantics ($VARIANT_DESC) from PR #$PR_NUMBER..."

# Detect OS and architecture
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Linux*)  PLATFORM="linux" ;;
    Darwin*) PLATFORM="macos" ;;
    *)       error "Unsupported OS: $OS" ;;
esac

case "$ARCH" in
    x86_64)  ARCH="x86_64" ;;
    amd64)   ARCH="x86_64" ;;
    arm64)   ARCH="arm64" ;;
    aarch64) ARCH="arm64" ;;
    *)       error "Unsupported architecture: $ARCH" ;;
esac

info "Detected: $PLATFORM-$ARCH"

# Get the PR's head commit SHA
info "Finding PR workflow run..."
HEAD_SHA=$(gh pr view "$PR_NUMBER" --repo "$REPO" --json headRefOid -q '.headRefOid')
if [ -z "$HEAD_SHA" ]; then
    error "Could not find PR #$PR_NUMBER"
fi

# Find the workflow run for this PR
RUN_ID=$(gh run list --repo "$REPO" --workflow "PR Build" --json databaseId,headSha,status,conclusion \
    -q ".[] | select(.headSha == \"$HEAD_SHA\" and .status == \"completed\" and .conclusion == \"success\") | .databaseId" \
    | head -1)

if [ -z "$RUN_ID" ]; then
    error "No successful PR Build workflow found for PR #$PR_NUMBER. The build may still be running or failed."
fi

# Create temp directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Create install directory
mkdir -p "$INSTALL_DIR"

# Function to download and install an artifact (silent mode available)
download_and_install() {
    local artifact_name="$1"
    local final_name="$2"
    
    local extract_dir="$TEMP_DIR/extract_$final_name"
    mkdir -p "$extract_dir"
    
    cd "$TEMP_DIR"
    if ! gh run download "$RUN_ID" --repo "$REPO" --name "$artifact_name" --dir "$extract_dir" 2>/dev/null; then
        error "Failed to download. Make sure the PR build completed successfully."
    fi
    
    # Find and extract the zip
    ZIP_FILE=$(find "$extract_dir" -name "*.zip" | head -1)
    if [ -z "$ZIP_FILE" ]; then
        error "Could not find downloaded artifact"
    fi
    
    unzip -q -o "$ZIP_FILE" -d "$extract_dir"
    
    # Find the executable
    EXTRACTED_EXE=$(find "$extract_dir" -type f -name "semantics*" ! -name "*.zip" | head -1)
    if [ -z "$EXTRACTED_EXE" ]; then
        error "Could not find executable in downloaded archive"
    fi
    
    mv "$EXTRACTED_EXE" "$INSTALL_DIR/$final_name"
    chmod +x "$INSTALL_DIR/$final_name"
}

info "Downloading..."

# Download and install components (silently)
LAUNCHER_ARTIFACT="semantics-pr-$PR_NUMBER-$PLATFORM-$ARCH"
download_and_install "$LAUNCHER_ARTIFACT" "semantics"

# Install the module variant(s)
if [ "$VARIANT" = "full" ]; then
    # For "full", install all individual modules
    info "Installing all modules..."
    AUDIO_ARTIFACT="semantics-audio-pr-$PR_NUMBER-$PLATFORM-$ARCH"
    download_and_install "$AUDIO_ARTIFACT" "semantics-audio"
    VIDEO_ARTIFACT="semantics-video-pr-$PR_NUMBER-$PLATFORM-$ARCH"
    download_and_install "$VIDEO_ARTIFACT" "semantics-video"
    DOCUMENT_ARTIFACT="semantics-document-pr-$PR_NUMBER-$PLATFORM-$ARCH"
    download_and_install "$DOCUMENT_ARTIFACT" "semantics-document"
else
    MODULE_ARTIFACT="semantics-$VARIANT-pr-$PR_NUMBER-$PLATFORM-$ARCH"
    download_and_install "$MODULE_ARTIFACT" "semantics-$VARIANT"
fi

info "Installing..."

# Add to PATH if not already there
add_to_path() {
    local shell_config="$1"
    local path_line="export PATH=\"\$HOME/.semantics/bin:\$PATH\""
    
    if [ -f "$shell_config" ]; then
        if ! grep -q ".semantics/bin" "$shell_config"; then
            echo "" >> "$shell_config"
            echo "# Added by semantics installer" >> "$shell_config"
            echo "$path_line" >> "$shell_config"
        fi
    fi
}

# Detect shell and add to appropriate config
SHELL_NAME=$(basename "$SHELL")
case "$SHELL_NAME" in
    bash)
        add_to_path "$HOME/.bashrc"
        add_to_path "$HOME/.bash_profile"
        ;;
    zsh)
        add_to_path "$HOME/.zshrc"
        ;;
    fish)
        FISH_CONFIG="$HOME/.config/fish/config.fish"
        if [ -f "$FISH_CONFIG" ]; then
            if ! grep -q ".semantics/bin" "$FISH_CONFIG"; then
                echo "" >> "$FISH_CONFIG"
                echo "# Added by semantics installer" >> "$FISH_CONFIG"
                echo "set -gx PATH \$HOME/.semantics/bin \$PATH" >> "$FISH_CONFIG"
            fi
        fi
        ;;
    *)
        warn "Unknown shell: $SHELL_NAME. Please add $INSTALL_DIR to your PATH manually."
        ;;
esac

add_to_path "$HOME/.profile"

# Update current session PATH
export PATH="$INSTALL_DIR:$PATH"

# Verify
info "Installation complete!"
echo ""
"$INSTALL_DIR/semantics" --version

echo ""
echo -e "\033[33mRestart your terminal or run:\033[0m"
echo "  export PATH=\"\$HOME/.semantics/bin:\$PATH\""
echo ""
if [ "$VARIANT" = "full" ]; then
    echo "Usage: semantics audio --help"
    echo "       semantics video --help"
    echo "       semantics document --help"
else
    echo "Usage: semantics $VARIANT --help"
fi
