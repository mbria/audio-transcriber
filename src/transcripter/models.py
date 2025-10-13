"""Data models for transcription results."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

SentimentType = Literal["POSITIVE", "NEUTRAL", "NEGATIVE"]


class SentimentResult(BaseModel):
    """Sentiment analysis result for a text segment."""

    text: str = Field(..., description="Text that was analyzed")
    sentiment: SentimentType = Field(..., description="Detected sentiment")
    confidence: float = Field(..., description="Confidence score (0-1)")
    start: int = Field(..., description="Start time in milliseconds")
    end: int = Field(..., description="End time in milliseconds")
    speaker: str | None = Field(None, description="Speaker identifier if available")


class SpeakerUtterance(BaseModel):
    """Represents a single utterance by a speaker."""

    speaker: str = Field(..., description="Speaker identifier")
    text: str = Field(..., description="Transcribed text")
    start: int = Field(..., description="Start time in milliseconds")
    end: int = Field(..., description="End time in milliseconds")
    confidence: float | None = Field(None, description="Confidence score (0-1)")


class TranscriptionResult(BaseModel):
    """Complete transcription result with speaker diarization."""

    utterances: list[SpeakerUtterance] = Field(default_factory=list, description="List of speaker utterances")
    total_duration: int | None = Field(None, description="Total audio duration in seconds")
    processing_time_ms: int | None = Field(None, description="Processing time in milliseconds")
    audio_file: Path = Field(..., description="Path to the source audio file")
    sentiment_results: list[SentimentResult] | None = Field(None, description="Sentiment analysis results if enabled")

    def to_transcript_text(self) -> str:
        """Convert to readable transcript format with optional sentiment analysis."""
        lines = []
        for utterance in self.utterances:
            speaker_line = f"Speaker {utterance.speaker}: {utterance.text}"
            lines.append(speaker_line)

        # Add sentiment analysis section if available
        if self.sentiment_results:
            lines.append("\n" + "="*60)
            lines.append("SENTIMENT ANALYSIS")
            lines.append("="*60)
            for sentiment in self.sentiment_results:
                sentiment_line = f"[{sentiment.sentiment}] (confidence: {sentiment.confidence:.2f})"
                if sentiment.speaker:
                    sentiment_line = f"Speaker {sentiment.speaker} - {sentiment_line}"
                sentiment_line += f"\n{sentiment.text}"
                lines.append(sentiment_line)

        return "\n\n".join(lines)

    def to_srt_format(self) -> str:
        """Convert to SRT subtitle format."""
        lines = []
        for i, utterance in enumerate(self.utterances, 1):
            # Convert milliseconds to SRT time format
            start_time = self._ms_to_srt_time(utterance.start)
            end_time = self._ms_to_srt_time(utterance.end)

            lines.append(f"{i}")
            lines.append(f"{start_time} --> {end_time}")
            lines.append(f"Speaker {utterance.speaker}: {utterance.text}")
            lines.append("")  # Empty line between entries

        return "\n".join(lines)

    @staticmethod
    def _ms_to_srt_time(ms: int) -> str:
        """Convert milliseconds to SRT time format (HH:MM:SS,mmm)."""
        seconds = ms // 1000
        milliseconds = ms % 1000
        minutes = seconds // 60
        seconds = seconds % 60
        hours = minutes // 60
        minutes = minutes % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

