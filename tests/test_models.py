"""Tests for data models."""

from pathlib import Path

from transcripter.models import SentimentResult, SpeakerUtterance, TranscriptionResult


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


class TestSentimentResult:
    """Test SentimentResult model."""

    def test_sentiment_result_creation(self):
        """Test creating a sentiment result."""
        sentiment = SentimentResult(
            text="This is great!",
            sentiment="POSITIVE",
            confidence=0.92,
            start=1000,
            end=3000,
            speaker="A"
        )

        assert sentiment.text == "This is great!"
        assert sentiment.sentiment == "POSITIVE"
        assert sentiment.confidence == 0.92
        assert sentiment.start == 1000
        assert sentiment.end == 3000
        assert sentiment.speaker == "A"

    def test_sentiment_result_without_speaker(self):
        """Test creating sentiment result without speaker."""
        sentiment = SentimentResult(
            text="This is neutral.",
            sentiment="NEUTRAL",
            confidence=0.88,
            start=1000,
            end=3000
        )

        assert sentiment.speaker is None


class TestTranscriptionResultWithSentiment:
    """Test TranscriptionResult with sentiment analysis."""

    def test_transcription_result_with_sentiment(self):
        """Test creating transcription result with sentiment analysis."""
        utterances = [
            SpeakerUtterance(
                speaker="A",
                text="This is great!",
                start=1000,
                end=3000
            )
        ]

        sentiments = [
            SentimentResult(
                text="This is great!",
                sentiment="POSITIVE",
                confidence=0.92,
                start=1000,
                end=3000,
                speaker="A"
            )
        ]

        result = TranscriptionResult(
            utterances=utterances,
            audio_file=Path("test.mp3"),
            sentiment_results=sentiments
        )

        assert len(result.sentiment_results) == 1
        assert result.sentiment_results[0].sentiment == "POSITIVE"
        assert result.sentiment_results[0].confidence == 0.92

    def test_to_transcript_text_with_sentiment(self):
        """Test converting to transcript text with sentiment analysis."""
        utterances = [
            SpeakerUtterance(
                speaker="A",
                text="This is great!",
                start=1000,
                end=3000
            ),
            SpeakerUtterance(
                speaker="B",
                text="I'm not sure about that.",
                start=3500,
                end=6000
            )
        ]

        sentiments = [
            SentimentResult(
                text="This is great!",
                sentiment="POSITIVE",
                confidence=0.92,
                start=1000,
                end=3000,
                speaker="A"
            ),
            SentimentResult(
                text="I'm not sure about that.",
                sentiment="NEGATIVE",
                confidence=0.85,
                start=3500,
                end=6000,
                speaker="B"
            )
        ]

        result = TranscriptionResult(
            utterances=utterances,
            audio_file=Path("test.mp3"),
            sentiment_results=sentiments
        )

        text = result.to_transcript_text()

        # Check that utterances are present
        assert "Speaker A: This is great!" in text
        assert "Speaker B: I'm not sure about that." in text

        # Check that sentiment section is present
        assert "SENTIMENT ANALYSIS" in text
        assert "[POSITIVE]" in text
        assert "[NEGATIVE]" in text
        assert "(confidence: 0.92)" in text
        assert "(confidence: 0.85)" in text

    def test_to_transcript_text_without_sentiment(self):
        """Test transcript text without sentiment analysis (default behavior)."""
        utterances = [
            SpeakerUtterance(
                speaker="A",
                text="Hello world",
                start=1000,
                end=3000
            )
        ]

        result = TranscriptionResult(
            utterances=utterances,
            audio_file=Path("test.mp3")
        )

        text = result.to_transcript_text()

        # Should not have sentiment section
        assert "SENTIMENT ANALYSIS" not in text
        assert "Speaker A: Hello world" in text

