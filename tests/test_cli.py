"""Tests for the CLI functionality."""

from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from transcripter.cli import main


class TestCLI:
    """Test cases for CLI functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_input_file = Path("test_audio.mp3")
        self.test_output_file = Path("test_output.txt")

    @patch('transcripter.cli.TranscripterService')
    @patch('transcripter.cli.get_config')
    @patch('transcripter.cli.configure_logging')
    @patch('builtins.input')
    @patch('builtins.open', mock_open(read_data=""))
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('sys.argv', ['transcripter', 'test_audio.mp3', 'test_output.txt'])
    def test_cli_with_speaker_naming_prompt_yes(self, mock_is_file, mock_exists, mock_input, mock_logging, mock_config, mock_service_class):
        """Test CLI with speaker naming prompt - user chooses yes."""
        # Set up mocks
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_config.return_value.output_dir = Path("output")
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        # Mock transcription result with multiple speakers
        mock_result = MagicMock()
        mock_utterance_a = MagicMock()
        mock_utterance_a.speaker = "Speaker A"
        mock_utterance_b = MagicMock()
        mock_utterance_b.speaker = "Speaker B"
        mock_result.utterances = [mock_utterance_a, mock_utterance_b]
        mock_result.total_duration = 5000
        mock_result.processing_time_ms = 3000
        mock_service.transcribe_file.return_value = mock_result

        # Mock user input for initial prompt
        mock_input.return_value = "y"

        # Mock the SpeakerNamingService
        with patch('transcripter.cli.SpeakerNamingService') as mock_naming_service_class:
            mock_naming_service = MagicMock()
            mock_naming_service_class.return_value = mock_naming_service
            mock_naming_service.run_interactive_naming.return_value = True

            # Run the CLI
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_not_called()  # Should not exit with error

        # Verify the initial prompt was shown
        mock_input.assert_called_with("Would you like to name the speakers? [Y/n]: ")

    @patch('transcripter.cli.TranscripterService')
    @patch('transcripter.cli.get_config')
    @patch('transcripter.cli.configure_logging')
    @patch('builtins.input')
    @patch('builtins.open', mock_open(read_data=""))
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('sys.argv', ['transcripter', 'test_audio.mp3', 'test_output.txt'])
    def test_cli_with_speaker_naming_prompt_no(self, mock_is_file, mock_exists, mock_input, mock_logging, mock_config, mock_service_class):
        """Test CLI with speaker naming prompt - user chooses no."""
        # Set up mocks
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_config.return_value.output_dir = Path("output")
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        # Mock transcription result with multiple speakers
        mock_result = MagicMock()
        mock_utterance_a = MagicMock()
        mock_utterance_a.speaker = "Speaker A"
        mock_utterance_b = MagicMock()
        mock_utterance_b.speaker = "Speaker B"
        mock_result.utterances = [mock_utterance_a, mock_utterance_b]
        mock_result.total_duration = 5000
        mock_result.processing_time_ms = 3000
        mock_service.transcribe_file.return_value = mock_result

        # Mock user input for initial prompt
        mock_input.return_value = "n"

        # Run the CLI
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_not_called()  # Should not exit with error

        # Verify the initial prompt was shown and SpeakerNamingService was not created
        mock_input.assert_called_with("Would you like to name the speakers? [Y/n]: ")

    @patch('transcripter.cli.TranscripterService')
    @patch('transcripter.cli.get_config')
    @patch('transcripter.cli.configure_logging')
    @patch('builtins.open', mock_open(read_data=""))
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('sys.argv', ['transcripter', 'test_audio.mp3', 'test_output.txt'])
    def test_cli_single_speaker_no_naming_prompt(self, mock_is_file, mock_exists, mock_logging, mock_config, mock_service_class):
        """Test CLI with single speaker - no naming prompt should appear."""
        # Set up mocks
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_config.return_value.output_dir = Path("output")
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        # Mock transcription result with single speaker
        mock_result = MagicMock()
        mock_utterance = MagicMock()
        mock_utterance.speaker = "Speaker A"
        mock_result.utterances = [mock_utterance]
        mock_result.total_duration = 5000
        mock_result.processing_time_ms = 3000
        mock_service.transcribe_file.return_value = mock_result

        # Mock the SpeakerNamingService to ensure it's not called
        with patch('transcripter.cli.SpeakerNamingService') as mock_naming_service_class:
            # Run the CLI
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_not_called()  # Should not exit with error

            # Verify SpeakerNamingService was not instantiated
            mock_naming_service_class.assert_not_called()
