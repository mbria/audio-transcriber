"""Tests for data models."""

from pathlib import Path

from transcripter.models import SpeakerUtterance, TranscriptionResult


class TestSpeakerUtterance:
    """Test SpeakerUtterance model."""

    def test_speaker_utterance_creation(self):
        """Test creating a speaker utterance."""
        utterance = SpeakerUtterance(
            speaker="A",
            text="Hello, how are you?",
            start=1000,
            end=3000,
            confidence=0.95
        )

        assert utterance.speaker == "A"
        assert utterance.text == "Hello, how are you?"
        assert utterance.start == 1000
        assert utterance.end == 3000
        assert utterance.confidence == 0.95


class TestTranscriptionResult:
    """Test TranscriptionResult model."""

    def test_transcription_result_creation(self):
        """Test creating a transcription result."""
        utterances = [
            SpeakerUtterance(
                speaker="A",
                text="Hello, how are you?",
                start=1000,
                end=3000
            ),
            SpeakerUtterance(
                speaker="B",
                text="I'm doing well, thank you.",
                start=3500,
                end=6000
            )
        ]

        result = TranscriptionResult(
            utterances=utterances,
            total_duration=6,
            processing_time_ms=1500,
            audio_file=Path("test.mp3")
        )

        assert len(result.utterances) == 2
        assert result.total_duration == 6
        assert result.processing_time_ms == 1500
        assert result.audio_file == Path("test.mp3")

    def test_to_transcript_text(self):
        """Test converting to transcript text format."""
        utterances = [
            SpeakerUtterance(
                speaker="A",
                text="Hello, how are you?",
                start=1000,
                end=3000
            ),
            SpeakerUtterance(
                speaker="B",
                text="I'm doing well, thank you.",
                start=3500,
                end=6000
            )
        ]

        result = TranscriptionResult(
            utterances=utterances,
            audio_file=Path("test.mp3")
        )

        expected = "Speaker A: Hello, how are you?\n\nSpeaker B: I'm doing well, thank you."
        assert result.to_transcript_text() == expected

    def test_to_srt_format(self):
        """Test converting to SRT subtitle format."""
        utterances = [
            SpeakerUtterance(
                speaker="A",
                text="Hello, how are you?",
                start=1000,
                end=3000
            )
        ]

        result = TranscriptionResult(
            utterances=utterances,
            audio_file=Path("test.mp3")
        )

        srt_content = result.to_srt_format()
        assert "00:00:01,000 --> 00:00:03,000" in srt_content
        assert "Speaker A: Hello, how are you?" in srt_content

    def test_ms_to_srt_time_conversion(self):
        """Test milliseconds to SRT time format conversion."""
        # Test various time conversions
        test_cases = [
            (1000, "00:00:01,000"),
            (61000, "00:01:01,000"),
            (3661000, "01:01:01,000"),
            (123, "00:00:00,123")
        ]

        for ms, expected in test_cases:
            result = TranscriptionResult._ms_to_srt_time(ms)
            assert result == expected

