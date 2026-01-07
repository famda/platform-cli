#!/bin/bash
# Semantics installer script for Linux/macOS
# Usage: curl -fsSL https://raw.githubusercontent.com/famda/platform-cli/main/docs/install.sh | bash
# Usage: curl -fsSL https://raw.githubusercontent.com/famda/platform-cli/main/docs/install.sh | bash -s -- --prerelease
# Usage: curl -fsSL https://raw.githubusercontent.com/famda/platform-cli/main/docs/install.sh | bash -s -- --variant audio

set -e

REPO="famda/platform-cli"
INSTALL_DIR="$HOME/.semantics/bin"
PRERELEASE=false
VARIANT="full"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --prerelease|-p)
            PRERELEASE=true
            shift
            ;;
        --variant|-v)
            if [ -z "${2-}" ] || [[ "$2" == -* ]]; then
                echo "error: --variant requires a value (full, audio, video, document)"
                exit 1
            fi
            VARIANT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate variant
case $VARIANT in
    full|audio|video|document) ;;
    *)
        echo "error: Invalid variant '$VARIANT'. Must be one of: full, audio, video, document"
        exit 1
        ;;
esac

# Determine executable name
if [ "$VARIANT" = "full" ]; then
    EXE_NAME="semantics"
else
    EXE_NAME="semantics-$VARIANT"
fi

info() { echo -e "\033[32m==>\033[0m $1"; }
warn() { echo -e "\033[33mwarning:\033[0m $1"; }
error() { echo -e "\033[31merror:\033[0m $1"; exit 1; }

if [ "$PRERELEASE" = true ]; then
    info "Installing $EXE_NAME (development build)..."
else
    info "Installing $EXE_NAME..."
fi

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

# Get version
if [ "$PRERELEASE" = true ]; then
    VERSION="dev"
    info "Development build: $VERSION"
else
    # Use jq if available, otherwise fall back to grep/sed
    RELEASE_JSON=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest")
    if command -v jq >/dev/null 2>&1; then
        VERSION=$(echo "$RELEASE_JSON" | jq -r '.tag_name')
    else
        VERSION=$(echo "$RELEASE_JSON" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
    fi
    if [ -z "$VERSION" ] || [ "$VERSION" = "null" ]; then
        error "Could not determine latest version. Check https://github.com/$REPO/releases"
    fi
    info "Latest version: $VERSION"
fi

# Build download filename
# Release format: semantics-v0.1.0-linux-x86_64.zip or semantics-audio-v0.1.0-linux-x86_64.zip
# Dev format: semantics-linux-x86_64.zip or semantics-audio-linux-x86_64.zip
if [ "$PRERELEASE" = true ]; then
    FILENAME="$EXE_NAME-$PLATFORM-$ARCH.zip"
else
    FILENAME="$EXE_NAME-$VERSION-$PLATFORM-$ARCH.zip"
fi

URL="https://github.com/$REPO/releases/download/$VERSION/$FILENAME"

# Create temp directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

info "Downloading $URL..."
if ! curl -fsSL "$URL" -o "$TEMP_DIR/$FILENAME"; then
    error "Download failed. Check if version '$VERSION' exists at https://github.com/$REPO/releases"
fi

# Extract
info "Extracting..."
unzip -q "$TEMP_DIR/$FILENAME" -d "$TEMP_DIR"

# Find the executable
EXTRACTED_EXE=$(find "$TEMP_DIR" -type f -name "semantics*" ! -name "*.zip" | head -1)
if [ -z "$EXTRACTED_EXE" ]; then
    error "Could not find executable in downloaded archive"
fi

# Install
info "Installing to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

# Determine final executable name
if [ "$VARIANT" = "full" ]; then
    FINAL_EXE_NAME="semantics"
else
    FINAL_EXE_NAME="semantics-$VARIANT"
fi

mv "$EXTRACTED_EXE" "$INSTALL_DIR/$FINAL_EXE_NAME"
chmod +x "$INSTALL_DIR/$FINAL_EXE_NAME"

# Add to PATH
add_to_path() {
    local shell_config="$1"
    local path_line="export PATH=\"\$HOME/.semantics/bin:\$PATH\""
    
    if [ -f "$shell_config" ]; then
        if ! grep -q ".semantics/bin" "$shell_config"; then
            echo "" >> "$shell_config"
            echo "# Added by semantics installer" >> "$shell_config"
            echo "$path_line" >> "$shell_config"
            info "Added to $shell_config"
        fi
    fi
}

if [ -n "$GITHUB_ACTIONS" ]; then
    # GitHub Actions: add to GITHUB_PATH
    info "Adding to GITHUB_PATH for this workflow..."
    echo "$INSTALL_DIR" >> "$GITHUB_PATH"
    export PATH="$INSTALL_DIR:$PATH"
else
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
                    info "Added to $FISH_CONFIG"
                fi
            fi
            ;;
        *)
            warn "Unknown shell: $SHELL_NAME. Please add $INSTALL_DIR to your PATH manually."
            ;;
    esac
    
    # Also try .profile for login shells
    add_to_path "$HOME/.profile"
    
    # Update current session PATH
    export PATH="$INSTALL_DIR:$PATH"
fi

# Verify
info "Successfully installed $EXE_NAME!"
"$INSTALL_DIR/$FINAL_EXE_NAME" version

echo ""
echo -e "\033[33mRestart your terminal or run:\033[0m"
echo "  export PATH=\"\$HOME/.semantics/bin:\$PATH\""
