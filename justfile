# Transcripter - Speech-to-Text Service Commands
# 
# Prerequisites: Set TRANSCRIPTER_ASSEMBLYAI_API_KEY in your .env file
# Quick setup: just setup

# Transcribe audio file to text (output file optional - defaults to same name with .txt extension)
# Set sentiment='true' to enable sentiment analysis
transcribe input_file output_file='' sentiment='false':
    uv run transcripter "{{input_file}}" {{ if output_file == "" { "" } else { '"' + output_file + '"' } }} {{ if sentiment == "true" { "--sentiment" } else { "" } }}

# Transcribe to SRT subtitle format (output file optional - defaults to same name with .srt extension)
# Set sentiment='true' to enable sentiment analysis
transcribe-srt input_file output_file='' sentiment='false':
    uv run transcripter "{{input_file}}" {{ if output_file == "" { "" } else { '"' + output_file + '"' } }} --format srt {{ if sentiment == "true" { "--sentiment" } else { "" } }}

# Transcribe with verbose logging for debugging (output file optional)
# Set sentiment='true' to enable sentiment analysis
transcribe-verbose input_file output_file='' sentiment='false':
    uv run transcripter "{{input_file}}" {{ if output_file == "" { "" } else { '"' + output_file + '"' } }} --verbose {{ if sentiment == "true" { "--sentiment" } else { "" } }}

# Transcribe with sentiment analysis enabled (convenience recipe)
transcribe-sentiment input_file output_file='':
    uv run transcripter "{{input_file}}" {{ if output_file == "" { "" } else { '"' + output_file + '"' } }} --sentiment

# Show help and usage examples
help:
    uv run transcripter --help

# Quick setup - install dependencies and create directories
setup:
    uv sync
    mkdir -p data/input data/output

# Development and Quality Commands

# Run tests with coverage
test:
    uv run pytest --cov=src/transcripter --cov-report=term-missing

# Run linting and type checking
check:
    uv run ruff check src/ tests/
    uv run pyright src/

# Auto-fix code quality issues
fix:
    uv run ruff check --fix src/ tests/
    uv run ruff format src/ tests/

# Run all quality checks
quality: install check test

# Install dependencies
install:
    uv sync

# Install development dependencies
dev-install:
    uv sync --group dev

# Container Commands

# Build container images
build:
    docker-compose build

# Start containerized service
up:
    docker-compose up -d

# Stop containers
down:
    docker-compose down

# Clean up containers and volumes
clean:
    docker-compose down -v --remove-orphans
    docker system prune -f

# Transcribe using container (when API key is in .env)
transcribe-docker input_file output_file:
    docker-compose run --rm transcripter {{input_file}} {{output_file}}

# Example transcriptions (requires sample files in data/input/)
example-text:
    uv run transcripter data/input/sample.mp4

example-srt:
    uv run transcripter data/input/sample.mp4 --format srt

example-verbose:
    uv run transcripter data/input/sample.mp4 --verbose
