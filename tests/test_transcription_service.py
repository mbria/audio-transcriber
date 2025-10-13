"""Tests for transcription service."""

from pathlib import Path
from unittest.mock import Mock, patch

import assemblyai as aai
import pytest

from transcripter.config import TranscripterConfig
from transcripter.models import SpeakerUtterance, TranscriptionResult
from transcripter.transcription_service import TranscripterService, TranscriptionError


class TestTranscripterService:
    """Test TranscripterService class."""

    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        config = TranscripterConfig(assemblyai_api_key="")

        with pytest.raises(TranscriptionError, match="AssemblyAI API key is required"):
            TranscripterService(config)

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        config = TranscripterConfig(assemblyai_api_key="test_key")

        with patch('transcripter.transcription_service.aai.settings') as mock_settings:
            service = TranscripterService(config)
            mock_settings.api_key = "test_key"
            assert service.config == config

    @patch('transcripter.transcription_service.aai.Transcriber')
    def test_transcribe_file_success(self, mock_transcriber_class):
        """Test successful transcription."""
        # Setup
        config = TranscripterConfig(assemblyai_api_key="test_key")
        service = TranscripterService(config)

        # Mock transcript result
        mock_utterance = Mock()
        mock_utterance.speaker = "A"
        mock_utterance.text = "Hello world"
        mock_utterance.start = 1000
        mock_utterance.end = 3000
        mock_utterance.confidence = 0.95

        mock_transcript = Mock()
        mock_transcript.status = aai.TranscriptStatus.completed
        mock_transcript.utterances = [mock_utterance]
        mock_transcript.audio_duration = 5

        # Mock transcriber instance
        mock_transcriber = Mock()
        mock_transcriber.transcribe.return_value = mock_transcript
        mock_transcriber.get_transcript.return_value = mock_transcript
        mock_transcriber_class.return_value = mock_transcriber

        # Test
        audio_file = Path("test.mp3")
        with patch('pathlib.Path.exists', return_value=True):
            result = service.transcribe_file(audio_file)

        # Verify
        assert isinstance(result, TranscriptionResult)
        assert len(result.utterances) == 1
        assert result.utterances[0].speaker == "A"
        assert result.utterances[0].text == "Hello world"
        assert result.total_duration == 5

    def test_transcribe_file_not_found(self):
        """Test transcription with non-existent file."""
        config = TranscripterConfig(assemblyai_api_key="test_key")

        with patch('transcripter.transcription_service.aai.settings'):
            service = TranscripterService(config)

            with pytest.raises(TranscriptionError, match="Audio file not found"):
                service.transcribe_file(Path("nonexistent.mp3"))

    @patch('transcripter.transcription_service.aai.Transcriber')
    def test_transcribe_file_error_status(self, mock_transcriber_class):
        """Test transcription with error status."""
        config = TranscripterConfig(assemblyai_api_key="test_key")
        service = TranscripterService(config)

        # Mock transcript with error
        mock_transcript = Mock()
        mock_transcript.status = aai.TranscriptStatus.error
        mock_transcript.error = "Transcription failed"

        mock_transcriber = Mock()
        mock_transcriber.transcribe.return_value = mock_transcript
        mock_transcriber.get_transcript.return_value = mock_transcript
        mock_transcriber_class.return_value = mock_transcriber

        # Create a temporary file for testing
        with patch('pathlib.Path.exists', return_value=True):
            with patch('transcripter.transcription_service.aai.TranscriptionConfig') as mock_config:
                mock_config.return_value = Mock()
                with pytest.raises(TranscriptionError, match="Transcription failed"):
                    service.transcribe_file(Path("test.mp3"))

    def test_process_transcript_with_utterances(self):
        """Test processing transcript with speaker utterances."""
        config = TranscripterConfig(assemblyai_api_key="test_key")
        service = TranscripterService(config)

        # Mock transcript with utterances
        mock_utterance = Mock()
        mock_utterance.speaker = "A"
        mock_utterance.text = "Hello world"
        mock_utterance.start = 1000
        mock_utterance.end = 3000
        mock_utterance.confidence = 0.95

        mock_transcript = Mock()
        mock_transcript.utterances = [mock_utterance]
        mock_transcript.audio_duration = 5

        # Test
        result = service._process_transcript(mock_transcript, Path("test.mp3"), 1500)

        # Verify
        assert len(result.utterances) == 1
        assert result.utterances[0].speaker == "A"
        assert result.utterances[0].text == "Hello world"
        assert result.utterances[0].start == 1000
        assert result.utterances[0].end == 3000
        assert result.utterances[0].confidence == 0.95
        assert result.total_duration == 5
        assert result.processing_time_ms == 1500

    def test_process_transcript_fallback(self):
        """Test processing transcript without utterances (fallback)."""
        config = TranscripterConfig(assemblyai_api_key="test_key")
        service = TranscripterService(config)

        # Mock transcript without utterances
        mock_transcript = Mock()
        mock_transcript.utterances = None
        mock_transcript.text = "Hello world"
        mock_transcript.audio_duration = 5
        mock_transcript.confidence = 0.95

        # Test
        result = service._process_transcript(mock_transcript, Path("test.mp3"), 1500)

        # Verify fallback behavior
        assert len(result.utterances) == 1
        assert result.utterances[0].speaker == "A"  # Default speaker
        assert result.utterances[0].text == "Hello world"
        assert result.utterances[0].start == 0
        assert result.utterances[0].end == 5
        assert result.utterances[0].confidence == 0.95

    def test_save_transcript_txt(self):
        """Test saving transcript in text format."""
        config = TranscripterConfig(assemblyai_api_key="test_key")
        service = TranscripterService(config)

        # Create test result
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

        # Test saving
        output_path = Path("test_output.txt")

        with patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('builtins.open', create=True) as mock_open:

            service.save_transcript(result, output_path, "txt")

            # Verify directory creation
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

            # Verify file writing
            mock_open.assert_called_once_with(output_path, 'w', encoding='utf-8')

    def test_save_transcript_srt(self):
        """Test saving transcript in SRT format."""
        config = TranscripterConfig(assemblyai_api_key="test_key")
        service = TranscripterService(config)

        # Create test result
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

        # Test saving
        output_path = Path("test_output.srt")

        with patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('builtins.open', create=True) as mock_open:

            service.save_transcript(result, output_path, "srt")

            # Verify directory creation and file writing
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            mock_open.assert_called_once_with(output_path, 'w', encoding='utf-8')
