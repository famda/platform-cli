# Semantics CLI

Process different file types with specialized AI handlers. A modular CLI for audio transcription, video analysis, and document text extraction.

## Install

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/famda/platform-cli/main/docs/install.sh | bash
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/famda/platform-cli/main/docs/install.ps1 | iex
```

### Install Options

Install a specific variant (smaller download):

```bash
# Linux/macOS
curl -fsSL https://raw.githubusercontent.com/famda/platform-cli/main/docs/install.sh | bash -s -- --variant audio

# Windows
irm https://raw.githubusercontent.com/famda/platform-cli/main/docs/install.ps1 | iex; Install-Semantics -Variant audio
```

## Quick Start

```bash
# Transcribe an audio file
semantics audio recording.mp3 -o ./output --transcribe

# Extract text from a PDF
semantics document scan.pdf -o ./output --extract-text

# Detect objects in a video
semantics video clip.mp4 -o ./output --detect-objects
```

## Variants

Choose the variant that fits your needs:

| Variant | Executable | Includes |
|---------|------------|----------|
| **Full** | `semantics` | All modules (audio, video, document) |
| **Audio** | `semantics-audio` | Audio transcription and metadata extraction |
| **Video** | `semantics-video` | Video transcription and object detection |
| **Document** | `semantics-document` | PDF and image text extraction |

## Usage

### Audio Processing

```bash
# Transcribe audio to text
semantics audio input.wav -o ./output --transcribe

# With language and model options
semantics audio input.mp3 -o ./output --transcribe --language es --model large

# Extract metadata
semantics audio input.wav -o ./output --extract-metadata

# Chain operations
semantics audio input.wav -o ./output --transcribe --extract-metadata
```

### Video Processing

```bash
# Transcribe video audio
semantics video video.mp4 -o ./output --transcribe

# Detect objects with confidence threshold
semantics video video.mp4 -o ./output --detect-objects --confidence 0.7

# Chain operations
semantics video video.mp4 -o ./output --transcribe --detect-objects
```

### Document Processing

```bash
# Extract text from PDF
semantics document document.pdf -o ./output --extract-text

# Extract as JSON
semantics document scan.png -o ./output --extract-text --format json
```

### Help

```bash
semantics --help
semantics audio --help
semantics video --help
semantics document --help
```

## Commands

### Audio

| Flag | Description | Options |
|------|-------------|---------|
| `--transcribe` | Convert audio to text | `--language`, `--model` |
| `--extract-metadata` | Get audio file metadata | - |

### Video

| Flag | Description | Options |
|------|-------------|---------|
| `--transcribe` | Transcribe video audio | `--language`, `--model` |
| `--detect-objects` | Detect objects in frames | `--confidence`, `--model` |

### Document

| Flag | Description | Options |
|------|-------------|---------|
| `--extract-text` | Extract text from PDF/images | `--format` (text/json) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, architecture, and how to add new modules.

## License

MIT License
