"""Data models for transcription results."""

from pathlib import Path

from pydantic import BaseModel, Field


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
    total_duration: int | None = Field(None, description="Total audio duration in milliseconds")
    processing_time_ms: int | None = Field(None, description="Processing time in milliseconds")
    audio_file: Path = Field(..., description="Path to the source audio file")

    def to_transcript_text(self) -> str:
        """Convert to readable transcript format."""
        lines = []
        for utterance in self.utterances:
            speaker_line = f"Speaker {utterance.speaker}: {utterance.text}"
            lines.append(speaker_line)
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

