"""Core transcription service using AssemblyAI."""

import time
from pathlib import Path

import assemblyai as aai
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import TranscripterConfig, get_config, get_correlation_id
from .logging import get_logger
from .models import SentimentResult, SpeakerUtterance, TranscriptionResult

logger = get_logger(__name__)


class TranscriptionError(Exception):
    """Custom exception for transcription-related errors."""
    pass


class TranscripterService:
    """Service for transcribing audio files with speaker diarization."""

    def __init__(self, config: TranscripterConfig | None = None):
        """Initialize the transcription service."""
        self.config = config or get_config()
        self._setup_assemblyai()

    def _setup_assemblyai(self) -> None:
        """Set up AssemblyAI client with API key."""
        if not self.config.assemblyai_api_key:
            raise TranscriptionError("AssemblyAI API key is required")

        aai.settings.api_key = self.config.assemblyai_api_key
        logger.info("AssemblyAI client configured", api_key_length=len(self.config.assemblyai_api_key))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    def transcribe_file(self, audio_file_path: Path, enable_sentiment_analysis: bool = False) -> TranscriptionResult:
        """
        Transcribe an audio file with speaker diarization.

        Args:
            audio_file_path: Path to the audio file to transcribe
            enable_sentiment_analysis: Enable sentiment analysis for each sentence

        Returns:
            TranscriptionResult with speaker utterances and optional sentiment analysis

        Raises:
            TranscriptionError: If transcription fails
        """
        correlation_id = get_correlation_id()
        logger.info(
            "Starting transcription",
            audio_file=str(audio_file_path),
            sentiment_analysis=enable_sentiment_analysis,
            correlation_id=correlation_id
        )

        start_time = time.time()

        try:
            # Validate file exists
            if not audio_file_path.exists():
                raise TranscriptionError(f"Audio file not found: {audio_file_path}")

            # Create transcriber and configure for speaker diarization
            transcriber = aai.Transcriber()

            # Configure transcription settings
            config = aai.TranscriptionConfig(
                speaker_labels=True,  # Enable speaker diarization
                speakers_expected=None,  # Let AssemblyAI auto-detect speaker count
                auto_highlights=True,  # Enable auto-highlights for better accuracy
                sentiment_analysis=enable_sentiment_analysis,  # Optional sentiment analysis
                entity_detection=False,  # Disable to focus on accuracy
            )

            logger.info("Starting AssemblyAI transcription")

            # Transcribe the file
            transcript = transcriber.transcribe(str(audio_file_path), config=config)

            # Wait for completion
            while transcript.status not in [aai.TranscriptStatus.completed, aai.TranscriptStatus.error]:
                logger.debug("Transcription in progress", status=transcript.status)
                time.sleep(1)
                if transcript.id is None:
                    raise TranscriptionError("Transcript ID is None")
                transcript = aai.Transcript.get_by_id(transcript.id)

            if transcript.status == aai.TranscriptStatus.error:
                raise TranscriptionError(f"Transcription failed: {transcript.error}")

            # Process the results
            processing_time = int((time.time() - start_time) * 1000)
            result = self._process_transcript(transcript, audio_file_path, processing_time, enable_sentiment_analysis)

            logger.info(
                "Transcription completed",
                utterances_count=len(result.utterances),
                sentiment_results_count=len(result.sentiment_results) if result.sentiment_results else 0,
                processing_time_ms=processing_time,
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(
                "Transcription failed",
                error=str(e),
                audio_file=str(audio_file_path),
                correlation_id=correlation_id
            )
            raise TranscriptionError(f"Failed to transcribe {audio_file_path}: {e}") from e

    def _process_transcript(
        self,
        transcript: aai.Transcript,
        audio_file_path: Path,
        processing_time_ms: int,
        sentiment_analysis_enabled: bool = False
    ) -> TranscriptionResult:
        """Process AssemblyAI transcript into our format."""
        utterances = []

        # Process utterances with speaker labels
        if hasattr(transcript, 'utterances') and transcript.utterances:
            for utterance in transcript.utterances:
                speaker_utterance = SpeakerUtterance(
                    speaker=utterance.speaker or "Unknown",
                    text=utterance.text,
                    start=utterance.start,
                    end=utterance.end,
                    confidence=getattr(utterance, 'confidence', None)
                )
                utterances.append(speaker_utterance)
        else:
            # Fallback: treat entire transcript as single speaker
            logger.warning("No speaker utterances found, treating as single speaker")
            if transcript.text:
                speaker_utterance = SpeakerUtterance(
                    speaker="A",
                    text=transcript.text,
                    start=0,
                    end=transcript.audio_duration or 0,
                    confidence=getattr(transcript, 'confidence', None)
                )
                utterances.append(speaker_utterance)

        # Process sentiment analysis results if available
        sentiment_results = None
        if sentiment_analysis_enabled and hasattr(transcript, 'sentiment_analysis') and transcript.sentiment_analysis:
            sentiment_results = []
            for sentiment in transcript.sentiment_analysis:
                sentiment_result = SentimentResult(
                    text=sentiment.text,
                    sentiment=sentiment.sentiment,  # type: ignore[arg-type]
                    confidence=sentiment.confidence,
                    start=sentiment.start,
                    end=sentiment.end,
                    speaker=getattr(sentiment, 'speaker', None)
                )
                sentiment_results.append(sentiment_result)
            logger.info("Processed sentiment analysis results", count=len(sentiment_results))

        return TranscriptionResult(
            utterances=utterances,
            total_duration=transcript.audio_duration,
            processing_time_ms=processing_time_ms,
            audio_file=audio_file_path,
            sentiment_results=sentiment_results
        )

    def save_transcript(
        self,
        result: TranscriptionResult,
        output_path: Path,
        format: str = "txt"
    ) -> None:
        """
        Save transcription result to file.

        Args:
            result: TranscriptionResult to save
            output_path: Path to save the transcript
            format: Output format ("txt" or "srt")
        """
        logger.info("Saving transcript", output_path=str(output_path), format=format)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate content based on format
        if format.lower() == "srt":
            content = result.to_srt_format()
        else:
            content = result.to_transcript_text()

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info("Transcript saved", output_path=str(output_path), content_length=len(content))
