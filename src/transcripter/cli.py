"""Command-line interface for Transcripter."""

import argparse
import sys
from pathlib import Path

from .config import get_config
from .logging import configure_logging, get_logger
from .transcription_service import TranscripterService, TranscriptionError

logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Speech-to-text utility with speaker diarization using AssemblyAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  transcripter meeting.mp4 transcript.txt
  transcripter audio.wav output.srt --format srt
  transcripter /path/to/audio.mp3 /path/to/output.txt --verbose
        """
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the input audio/video file"
    )

    parser.add_argument(
        "output_file", 
        type=Path,
        nargs="?",
        help="Path to save the transcript file (optional, defaults to input filename with format extension in output directory)"
    )

    parser.add_argument(
        "--format",
        choices=["txt", "srt"],
        default="txt",
        help="Output format: txt (default) or srt subtitle format"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )


    parser.add_argument(
        "--version",
        action="version",
        version="Transcripter 0.1.0"
    )

    return parser


def validate_inputs(input_file: Path, output_file: Path) -> None:
    """Validate input arguments."""
    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file does not exist: {input_file}", file=sys.stderr)
        sys.exit(1)

    # Check if input file is readable
    if not input_file.is_file():
        print(f"Error: Input path is not a file: {input_file}", file=sys.stderr)
        sys.exit(1)

    # Check file extension (basic validation)
    supported_extensions = {'.mp3', '.mp4', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'}
    if input_file.suffix.lower() not in supported_extensions:
        print(f"Warning: File extension '{input_file.suffix}' may not be supported", file=sys.stderr)
        print(f"Supported formats: {', '.join(supported_extensions)}", file=sys.stderr)


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging
    config = get_config()
    log_level = "DEBUG" if args.verbose else config.log_level
    configure_logging(log_level)


    # Generate output file path if not provided
    if args.output_file is None:
        # Use input filename with format appended and appropriate extension in output directory
        input_stem = args.input_file.stem
        output_filename = f"{input_stem}.{args.format}"
        args.output_file = config.output_dir / output_filename

    # Validate inputs
    validate_inputs(args.input_file, args.output_file)

    logger.info(
        "Starting transcription",
        input_file=str(args.input_file),
        output_file=str(args.output_file),
        format=args.format
    )

    try:
        # Initialize transcription service
        service = TranscripterService(config)

        # Transcribe the file
        print(f"Transcribing {args.input_file}...")
        result = service.transcribe_file(args.input_file)

        # Save the transcript
        print(f"Saving transcript to {args.output_file}...")
        service.save_transcript(result, args.output_file, args.format)

        # Print summary
        print("\nTranscription completed successfully!")
        print(f"Speakers detected: {len({utt.speaker for utt in result.utterances})}")
        print(f"Total utterances: {len(result.utterances)}")
        if result.total_duration:
            duration_sec = result.total_duration / 1000
            print(f"Audio duration: {duration_sec:.1f} seconds")
        if result.processing_time_ms:
            print(f"Processing time: {result.processing_time_ms}ms")

        logger.info("Transcription completed successfully")

    except TranscriptionError as e:
        print(f"Transcription error: {e}", file=sys.stderr)
        logger.error("Transcription failed", error=str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nTranscription cancelled by user", file=sys.stderr)
        logger.info("Transcription cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        logger.error("Unexpected error occurred", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
