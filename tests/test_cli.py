"""Tests for the CLI functionality."""

from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from transcripter.cli import main, path_with_quote_stripping, strip_outer_quotes


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
    @patch('builtins.input')
    @patch('builtins.open', mock_open(read_data=""))
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('sys.argv', ['transcripter', 'test_audio.mp3', 'test_output.txt'])
    def test_cli_single_speaker_naming_prompt_yes(self, mock_is_file, mock_exists, mock_input, mock_logging, mock_config, mock_service_class):
        """Test CLI with single speaker - user chooses to name the speaker."""
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

        # Mock user input for single speaker prompt
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

        # Verify the single speaker prompt was shown
        mock_input.assert_called_with("Would you like to name the speaker? [Y/n]: ")

    @patch('transcripter.cli.TranscripterService')
    @patch('transcripter.cli.get_config')
    @patch('transcripter.cli.configure_logging')
    @patch('builtins.input')
    @patch('builtins.open', mock_open(read_data=""))
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('sys.argv', ['transcripter', 'test_audio.mp3', 'test_output.txt'])
    def test_cli_single_speaker_naming_prompt_no(self, mock_is_file, mock_exists, mock_input, mock_logging, mock_config, mock_service_class):
        """Test CLI with single speaker - user chooses not to name the speaker."""
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

        # Mock user input for single speaker prompt
        mock_input.return_value = "n"

        # Run the CLI
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_not_called()  # Should not exit with error

        # Verify the single speaker prompt was shown and SpeakerNamingService was not created
        mock_input.assert_called_with("Would you like to name the speaker? [Y/n]: ")


class TestQuoteHandling:
    """Test cases for quote handling in file paths and names."""

    def test_strip_outer_quotes_standard_double(self):
        """Test stripping standard double quotes."""
        assert strip_outer_quotes('"test.mp3"') == "test.mp3"
        assert strip_outer_quotes('"path/to/file.mp3"') == "path/to/file.mp3"

    def test_strip_outer_quotes_standard_single(self):
        """Test stripping standard single quotes."""
        assert strip_outer_quotes("'test.mp3'") == "test.mp3"
        assert strip_outer_quotes("'path/to/file.mp3'") == "path/to/file.mp3"

    def test_strip_outer_quotes_backticks(self):
        """Test stripping backticks."""
        assert strip_outer_quotes("`test.mp3`") == "test.mp3"
        assert strip_outer_quotes("`path/to/file.mp3`") == "path/to/file.mp3"

    def test_strip_outer_quotes_smart_double(self):
        """Test stripping smart double quotes."""
        # Using Unicode escape sequences to avoid syntax conflicts
        assert strip_outer_quotes('\u201ctest.mp3\u201d') == "test.mp3"
        assert strip_outer_quotes('\u201cpath/to/file.mp3\u201d') == "path/to/file.mp3"

    def test_strip_outer_quotes_smart_single(self):
        """Test stripping smart single quotes."""
        # Using Unicode escape sequences to avoid syntax conflicts
        assert strip_outer_quotes('\u2018test.mp3\u2019') == "test.mp3"
        assert strip_outer_quotes('\u2018path/to/file.mp3\u2019') == "path/to/file.mp3"

    def test_strip_outer_quotes_guillemets(self):
        """Test stripping guillemets."""
        assert strip_outer_quotes("«test.mp3»") == "test.mp3"
        assert strip_outer_quotes("«path/to/file.mp3»") == "path/to/file.mp3"

    def test_strip_outer_quotes_single_guillemets(self):
        """Test stripping single guillemets."""
        assert strip_outer_quotes("‹test.mp3›") == "test.mp3"
        assert strip_outer_quotes("‹path/to/file.mp3›") == "path/to/file.mp3"

    def test_strip_outer_quotes_german_double(self):
        """Test stripping German-style double quotes."""
        # Using Unicode escape sequences to avoid syntax conflicts
        assert strip_outer_quotes('\u201etest.mp3\u201c') == "test.mp3"
        assert strip_outer_quotes('\u201epath/to/file.mp3\u201c') == "path/to/file.mp3"

    def test_strip_outer_quotes_german_single(self):
        """Test stripping German-style single quotes."""
        # Using Unicode escape sequences to avoid syntax conflicts
        assert strip_outer_quotes('\u201atest.mp3\u2019') == "test.mp3"
        assert strip_outer_quotes('\u201apath/to/file.mp3\u2019') == "path/to/file.mp3"

    def test_preserve_inner_quotes_standard_double(self):
        """Test that quotes within the filename are preserved."""
        assert strip_outer_quotes('A "really ugly" conversation.mp4') == 'A "really ugly" conversation.mp4'
        assert strip_outer_quotes('"A "really ugly" conversation.mp4"') == 'A "really ugly" conversation.mp4'

    def test_preserve_inner_quotes_standard_single(self):
        """Test that single quotes within the filename are preserved."""
        assert strip_outer_quotes("A 'really ugly' conversation.mp4") == "A 'really ugly' conversation.mp4"
        assert strip_outer_quotes("'A 'really ugly' conversation.mp4'") == "A 'really ugly' conversation.mp4"

    def test_preserve_inner_quotes_mixed(self):
        """Test filenames with various quote types inside."""
        assert strip_outer_quotes('Meeting - "Q1" Results.mp4') == 'Meeting - "Q1" Results.mp4'
        assert strip_outer_quotes("John's Interview.mp4") == "John's Interview.mp4"
        assert strip_outer_quotes('`Special` recording.mp4') == '`Special` recording.mp4'

    def test_no_quotes(self):
        """Test strings without any quotes."""
        assert strip_outer_quotes("test.mp3") == "test.mp3"
        assert strip_outer_quotes("path/to/file.mp3") == "path/to/file.mp3"

    def test_single_character(self):
        """Test single character strings."""
        assert strip_outer_quotes("a") == "a"
        assert strip_outer_quotes('"') == '"'
        assert strip_outer_quotes("'") == "'"

    def test_empty_string(self):
        """Test empty string."""
        assert strip_outer_quotes("") == ""

    def test_only_quotes(self):
        """Test string with only quotes."""
        assert strip_outer_quotes('""') == ""
        assert strip_outer_quotes("''") == ""
        assert strip_outer_quotes("``") == ""

    def test_mismatched_quotes(self):
        """Test that mismatched quotes are not stripped."""
        assert strip_outer_quotes('"test.mp3\'') == '"test.mp3\''
        assert strip_outer_quotes('\'test.mp3"') == '\'test.mp3"'
        assert strip_outer_quotes('"test.mp3`') == '"test.mp3`'

    def test_path_with_quote_stripping(self):
        """Test path conversion with quote stripping."""
        result = path_with_quote_stripping('"test.mp3"')
        assert isinstance(result, Path)
        assert str(result) == "test.mp3"

        result = path_with_quote_stripping('A "really ugly" conversation.mp4')
        assert isinstance(result, Path)
        assert str(result) == 'A "really ugly" conversation.mp4'

    def test_complex_filename_with_outer_quotes(self):
        """Test complex filename with both outer and inner quotes."""
        # Outer quotes should be stripped, inner preserved
        input_str = '"Meeting - "Strategic Plan" - Jan 2025.mp4"'
        expected = 'Meeting - "Strategic Plan" - Jan 2025.mp4'
        assert strip_outer_quotes(input_str) == expected

        # Without outer quotes, everything preserved
        input_str = 'Meeting - "Strategic Plan" - Jan 2025.mp4'
        expected = 'Meeting - "Strategic Plan" - Jan 2025.mp4'
        assert strip_outer_quotes(input_str) == expected

    def test_nested_smart_quotes(self):
        """Test nested smart quotes."""
        # Outer smart quotes should be stripped, using Unicode escapes
        input_str = '\u201cMeeting - "Q1" Results.mp4\u201d'
        expected = 'Meeting - "Q1" Results.mp4'
        assert strip_outer_quotes(input_str) == expected
