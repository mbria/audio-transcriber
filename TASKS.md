# Project Tasks

- [x] Project setup and containerization
  - [x] Initialize uv project with pyproject.toml
  - [x] Create docker-compose.yml and Dockerfile
  - [x] Set up justfile with basic recipes
- [x] AssemblyAI SDK integration
  - [x] Research AssemblyAI features for speaker diarization
  - [x] Add AssemblyAI SDK dependency
- [x] Configuration management
  - [x] Set up Pydantic configuration with environment variables
  - [x] Add structured logging with correlation IDs
- [x] Core transcription service
  - [x] Implement TranscripterService with speaker diarization
  - [x] Add robust error handling with retries
  - [x] Support multiple output formats (txt, srt)
- [x] Data models
  - [x] Create SpeakerUtterance and TranscriptionResult models
  - [x] Add format conversion methods (txt, srt)
- [x] Command-line interface
  - [x] Create CLI with argument parsing
  - [x] Add input validation and error handling
  - [x] Support verbose logging and custom API keys
- [x] Testing infrastructure
  - [x] Create comprehensive test suite
  - [x] Add tests for models, config, and service
  - [x] Achieve >80% code coverage
- [x] Documentation
  - [x] Create comprehensive README with usage examples
  - [x] Add API integration examples
  - [x] Document configuration options
- [x] Enhanced CLI and justfile usability
  - [x] Make output file optional with automatic naming
  - [x] Use TRANSCRIPTER_OUTPUT_DIR for default output location
  - [x] Update justfile with named parameters and optional output file
  - [x] Remove API key parameter (assume proper .env setup)
  - [x] Fix justfile syntax errors and conditional logic
  - [x] Fix file path quoting for filenames with spaces
  - [x] Append format to output filename to avoid overwriting different formats
  - [x] Strip outer quotes from input file paths to handle shell-quoted arguments
- [ ] Final validation and testing
  - [ ] Run full test suite with coverage
  - [ ] Verify linting and type checking
  - [ ] Test CLI functionality with sample audio
  - [ ] Validate Docker container builds

## Speaker Naming Feature

- [x] Interactive speaker naming system
  - [x] Create SpeakerNamingService for managing speaker identification and naming
  - [x] Implement speaker counting and analysis logic
  - [x] Add interactive prompt system for naming speakers with context preview
  - [x] Support "more" command to show additional speaker context
  - [x] Implement text replacement functionality for speaker names
  - [x] Create comprehensive unit tests for the speaker naming service
  - [x] Integrate speaker naming into main transcription workflow as default behavior

## Speaker Naming Bug Fixes

- [x] Fix speaker naming workflow issues
  - [x] Add initial Y/n prompt to ask if user wants to rename speakers
  - [x] Fix "more" command to show next utterances for each speaker (not same ones)
  - [x] Fix "set of 3" logic for first speaker (current + next 2, not before/current/after)
  - [x] Update unit tests to cover the corrected behavior

## Speaker Naming UX Improvements

- [x] Enhance user experience
  - [x] Improve confirmation prompt format to "rename Speaker A to [new name]?"
  - [x] Increase context display from 100 to 200 characters for better readability

## Single Speaker Support Enhancement

- [x] Support single speaker recordings (e.g., training sessions)
  - [x] Update CLI logic to prompt for single speaker naming with custom message
  - [x] Enhance SpeakerNamingService messaging for single speaker scenarios
  - [x] Add comprehensive tests for single speaker functionality
  - [x] Ensure backward compatibility with multi-speaker recordings

## Enhanced Quote Handling for File Names

- [x] Support various quote types in file names
  - [x] Enhance strip_outer_quotes function to handle multiple quote types
  - [x] Support standard quotes (", ')
  - [x] Support backticks (`)
  - [x] Support smart quotes (" " ' ')
  - [x] Support guillemets (« » ‹ ›)
  - [x] Support German-style quotes („ " ‚ ')
  - [x] Preserve quotes within filenames (e.g., `A "really ugly" conversation.mp4`)
  - [x] Strip only outer quotes from path arguments
  - [x] Add comprehensive test suite with 20 test cases
  - [x] Verify all 78 tests pass with 89.57% coverage

