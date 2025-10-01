# Transcripter

A speech-to-text utility with speaker diarization using AssemblyAI. Transcribe audio and video files from meetings and discussions with accurate speaker attribution.

## Features

- **Speaker Diarization**: Automatically identifies and attributes speech to different speakers
- **Multiple Formats**: Supports MP3, MP4, WAV, M4A, AAC, FLAC, OGG, and WMA files
- **Output Formats**: Generate transcripts in plain text or SRT subtitle format
- **Robust Error Handling**: Built-in retry logic and comprehensive error reporting
- **Structured Logging**: Detailed logging with correlation IDs for debugging
- **Container Support**: Ready-to-use Docker containers for deployment

## Quick Start

### Prerequisites

- Python 3.11+
- AssemblyAI API key ([Get one here](https://www.assemblyai.com/))

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd transcripter
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env and add your AssemblyAI API key
   ```

### Basic Usage

```bash
# Transcribe a meeting recording (output file optional - defaults to same name with .txt extension)
uv run transcripter meeting.mp4

# Or specify custom output file
uv run transcripter meeting.mp4 transcript.txt

# Generate SRT subtitles (output file optional - defaults to same name with .srt extension)
uv run transcripter audio.wav --format srt

# Verbose output for debugging
uv run transcripter audio.mp3 --verbose
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
just dev-install

# Run tests with coverage
just test

# Run linting and type checking
just check

# Auto-fix code issues
just fix

# Format code
just format
```

### Project Structure

```
transcripter/
├── src/transcripter/          # Source code
│   ├── __init__.py
│   ├── cli.py                 # Command-line interface
│   ├── config.py              # Configuration management
│   ├── logging.py             # Structured logging setup
│   ├── models.py              # Data models
│   └── transcription_service.py # Core transcription logic
├── tests/                     # Test suite
├── data/                      # Local data processing
│   ├── input/                 # Input audio files
│   └── output/                # Generated transcripts
├── docker/                    # Docker configuration
├── pyproject.toml            # Project configuration
├── justfile                  # Task automation
└── docker-compose.yml        # Container orchestration
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TRANSCRIPTER_ASSEMBLYAI_API_KEY` | AssemblyAI API key | Required |
| `TRANSCRIPTER_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `TRANSCRIPTER_OUTPUT_DIR` | Default output directory | ./data/output |
| `TRANSCRIPTER_MAX_RETRIES` | Maximum retry attempts | 3 |
| `TRANSCRIPTER_TIMEOUT` | Request timeout (seconds) | 300 |

### Command Line Options

```bash
transcripter [OPTIONS] INPUT_FILE [OUTPUT_FILE]

Arguments:
  INPUT_FILE    Path to the input audio/video file
  OUTPUT_FILE   Path to save the transcript file (optional, defaults to input filename with .txt extension in TRANSCRIPTER_OUTPUT_DIR)

Options:
  --format [txt|srt]    Output format (default: txt)
  --verbose, -v         Enable verbose logging
  --version             Show version information
  --help               Show help message
```

**Note**: The API key must be configured in your `.env` file as `TRANSCRIPTER_ASSEMBLYAI_API_KEY`.

## Output Formats

### Text Format
```
Speaker A: Hello, how are you today?

Speaker B: I'm doing well, thank you for asking.

Speaker A: That's great to hear.
```

### SRT Format
```
1
00:00:01,000 --> 00:00:03,000
Speaker A: Hello, how are you today?

2
00:00:03,500 --> 00:00:06,000
Speaker B: I'm doing well, thank you for asking.
```

## Docker Usage

### Build and Run

```bash
# Build the container
just build

# Start the development environment
just up

# Run transcription in container
docker-compose run transcripter audio.mp3 output.txt
```

### Environment Setup

Create a `.env` file with your AssemblyAI API key:

```bash
TRANSCRIPTER_ASSEMBLYAI_API_KEY=your_api_key_here
```

## API Integration

### Using Just Commands (Recommended)

**Note**: All commands require your AssemblyAI API key to be configured in your `.env` file as `TRANSCRIPTER_ASSEMBLYAI_API_KEY`.

```bash
# Basic transcription (output goes to TRANSCRIPTER_OUTPUT_DIR)
just transcribe "path/to/audio.m4a"

# Generate SRT subtitles
just transcribe-srt "path/to/audio.m4a"

# With verbose logging
just transcribe-verbose "path/to/audio.m4a"

# Show all available commands
just --list
```

### Using the Service Programmatically

```python
from transcripter.config import get_config
from transcripter.transcription_service import TranscripterService
from pathlib import Path

# Initialize service
config = get_config()
service = TranscripterService(config)

# Transcribe file
result = service.transcribe_file(Path("meeting.mp4"))

# Save transcript (will use default output directory and filename)
output_path = config.output_dir / "meeting.txt"
service.save_transcript(result, output_path)

# Access utterances
for utterance in result.utterances:
    print(f"Speaker {utterance.speaker}: {utterance.text}")
```

## Quality Assurance

The project maintains high code quality standards:

- **Type Safety**: Full type hints with pyright validation
- **Code Quality**: Ruff linting and formatting
- **Testing**: Comprehensive test suite with >80% coverage
- **Error Handling**: Robust error handling with retries
- **Logging**: Structured logging with correlation IDs

### Running Quality Checks

```bash
# Run all quality checks
just quality

# Individual checks
just check    # Linting and type checking
just test     # Test suite with coverage
just fix      # Auto-fix issues
```

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your AssemblyAI API key is set correctly
   ```bash
   export TRANSCRIPTER_ASSEMBLYAI_API_KEY=your_key_here
   ```

2. **File Not Found**: Verify the input file exists and is readable
   ```bash
   ls -la your_audio_file.mp3
   ```

3. **Unsupported Format**: Check if your audio format is supported
   - Supported: MP3, MP4, WAV, M4A, AAC, FLAC, OGG, WMA
   - Unsupported: Some proprietary formats

4. **Network Issues**: The service includes automatic retries for network problems

### Debug Mode

Enable verbose logging for detailed debugging:

```bash
transcripter audio.mp3 output.txt --verbose
```

## Contributing

1. Follow the established code style (PEP 8)
2. Add tests for new functionality
3. Ensure all quality checks pass
4. Update documentation as needed

## License

[Add your license information here]

## Acknowledgments

- [AssemblyAI](https://www.assemblyai.com/) for providing the transcription API
- Built with modern Python development practices

