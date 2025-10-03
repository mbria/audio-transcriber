"""Tests for the SpeakerNamingService."""

from pathlib import Path
from unittest.mock import mock_open, patch

from transcripter.speaker_naming_service import SpeakerNamingService


class TestSpeakerNamingService:
    """Test cases for SpeakerNamingService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_file = Path("test_transcript.txt")
        self.service = SpeakerNamingService(self.test_file)

    def test_init(self):
        """Test service initialization."""
        assert self.service.transcript_file == self.test_file
        assert self.service.speakers == {}
        assert self.service.utterances == []
        assert self.service.speaker_utterance_indices == {}

    def test_analyze_transcript_success(self):
        """Test successful transcript analysis."""
        transcript_content = """Speaker A: Hello, how are you today?
Speaker B: I'm doing well, thank you for asking.
Speaker A: That's great to hear.
Speaker C: I agree, it's a wonderful day.
"""

        with patch("builtins.open", mock_open(read_data=transcript_content)):
            result = self.service.analyze_transcript()

        assert result is True
        assert len(self.service.speakers) == 3
        assert "Speaker A" in self.service.speakers
        assert "Speaker B" in self.service.speakers
        assert "Speaker C" in self.service.speakers

        assert len(self.service.utterances) == 4
        assert self.service.utterances[0] == ("Speaker A", "Hello, how are you today?")
        assert self.service.utterances[1] == ("Speaker B", "I'm doing well, thank you for asking.")

    def test_analyze_transcript_no_speakers(self):
        """Test transcript analysis with no speakers."""
        transcript_content = """This is just regular text without any speakers.
More text here.
"""

        with patch("builtins.open", mock_open(read_data=transcript_content)):
            result = self.service.analyze_transcript()

        assert result is False
        assert len(self.service.speakers) == 0
        assert len(self.service.utterances) == 0

    def test_analyze_transcript_empty_file(self):
        """Test transcript analysis with empty file."""
        with patch("builtins.open", mock_open(read_data="")):
            result = self.service.analyze_transcript()

        assert result is False
        assert len(self.service.speakers) == 0
        assert len(self.service.utterances) == 0

    def test_analyze_transcript_file_error(self):
        """Test transcript analysis with file read error."""
        with patch("builtins.open", side_effect=OSError("File not found")):
            result = self.service.analyze_transcript()

        assert result is False

    def test_analyze_transcript_ignores_speaker_in_middle_of_line(self):
        """Test that speaker detection only works at line start."""
        transcript_content = """Hello Speaker A: this should not be detected
Speaker A: This should be detected
Some text Speaker B: also ignored
Speaker B: This should be detected
"""

        with patch("builtins.open", mock_open(read_data=transcript_content)):
            result = self.service.analyze_transcript()

        assert result is True
        assert len(self.service.speakers) == 2
        assert len(self.service.utterances) == 2

    def test_analyze_transcript_single_speaker(self):
        """Test transcript analysis with single speaker."""
        transcript_content = """Speaker A: Hello, welcome to today's training session.
Speaker A: Today we'll be covering the basics of our system.
Speaker A: Let's start with an overview of the main features.
"""

        with patch("builtins.open", mock_open(read_data=transcript_content)):
            result = self.service.analyze_transcript()

        assert result is True
        assert len(self.service.speakers) == 1
        assert "Speaker A" in self.service.speakers
        assert len(self.service.utterances) == 3
        assert self.service.utterances[0] == ("Speaker A", "Hello, welcome to today's training session.")
        assert self.service.utterances[1] == ("Speaker A", "Today we'll be covering the basics of our system.")
        assert self.service.utterances[2] == ("Speaker A", "Let's start with an overview of the main features.")

    def test_get_speaker_context_first_speaker(self):
        """Test getting context for the first speaker in the transcript."""
        # Set up utterances
        self.service.utterances = [
            ("Speaker A", "First utterance"),
            ("Speaker B", "Second utterance"),
            ("Speaker A", "Third utterance"),
            ("Speaker C", "Fourth utterance"),
        ]

        context = self.service.get_speaker_context("Speaker A", 0)

        # Should get: (current, next 2) for first speaker's first utterance
        assert len(context) == 3
        assert context[0] == ("Speaker A", "First utterance")
        assert context[1] == ("Speaker B", "Second utterance")
        assert context[2] == ("Speaker A", "Third utterance")

    def test_get_speaker_context_middle_speaker(self):
        """Test getting context for a speaker in the middle."""
        self.service.utterances = [
            ("Speaker A", "First utterance"),
            ("Speaker B", "Second utterance"),
            ("Speaker C", "Third utterance"),
            ("Speaker A", "Fourth utterance"),
        ]

        context = self.service.get_speaker_context("Speaker B", 1)

        # Should get: (previous, current, next)
        assert len(context) == 3
        assert context[0] == ("Speaker A", "First utterance")
        assert context[1] == ("Speaker B", "Second utterance")
        assert context[2] == ("Speaker C", "Third utterance")

    def test_get_speaker_context_last_speaker(self):
        """Test getting context for the last speaker."""
        self.service.utterances = [
            ("Speaker A", "First utterance"),
            ("Speaker B", "Second utterance"),
            ("Speaker C", "Third utterance"),
        ]

        context = self.service.get_speaker_context("Speaker C", 2)

        # Should get: (previous, current) - no next
        assert len(context) == 2
        assert context[0] == ("Speaker B", "Second utterance")
        assert context[1] == ("Speaker C", "Third utterance")

    def test_get_speaker_context_nonexistent_speaker(self):
        """Test getting context for a speaker that doesn't exist."""
        self.service.utterances = [
            ("Speaker A", "First utterance"),
            ("Speaker B", "Second utterance"),
        ]

        context = self.service.get_speaker_context("Speaker C", 0)
        assert len(context) == 0

    def test_advance_speaker_utterance_index_success(self):
        """Test successfully advancing to next utterance."""
        self.service.utterances = [
            ("Speaker A", "First utterance"),
            ("Speaker A", "Second utterance"),
            ("Speaker A", "Third utterance"),
            ("Speaker B", "Other speaker"),
        ]
        self.service.speaker_utterance_indices = {"Speaker A": 0}

        result = self.service.advance_speaker_utterance_index("Speaker A")

        assert result is True
        assert self.service.speaker_utterance_indices["Speaker A"] == 1

    def test_advance_speaker_utterance_index_no_more_utterances(self):
        """Test advancing when no more utterances available."""
        self.service.utterances = [
            ("Speaker A", "First utterance"),
            ("Speaker A", "Second utterance"),
        ]
        self.service.speaker_utterance_indices = {"Speaker A": 1}  # Already at last utterance

        result = self.service.advance_speaker_utterance_index("Speaker A")

        assert result is False
        assert self.service.speaker_utterance_indices["Speaker A"] == 1  # Unchanged

    def test_advance_speaker_utterance_index_nonexistent_speaker(self):
        """Test advancing for non-existent speaker."""
        result = self.service.advance_speaker_utterance_index("Speaker C")

        assert result is False

    def test_get_speaker_context_first_speaker_special_case(self):
        """Test special case for first speaker showing current + next 2."""
        self.service.utterances = [
            ("Speaker A", "First utterance"),
            ("Speaker B", "Second utterance"),
            ("Speaker C", "Third utterance"),
            ("Speaker A", "Fourth utterance"),
        ]
        self.service.speaker_utterance_indices = {"Speaker A": 0}

        context = self.service.get_speaker_context("Speaker A", 0)

        # Should show current + next 2 (not before/current/after)
        assert len(context) == 3
        assert context[0] == ("Speaker A", "First utterance")
        assert context[1] == ("Speaker B", "Second utterance")
        assert context[2] == ("Speaker C", "Third utterance")

    def test_get_speaker_context_first_speaker_subsequent_utterances(self):
        """Test that subsequent utterances for first speaker use normal logic."""
        self.service.utterances = [
            ("Speaker A", "First utterance"),
            ("Speaker B", "Second utterance"),
            ("Speaker A", "Third utterance"),
            ("Speaker C", "Fourth utterance"),
        ]
        self.service.speaker_utterance_indices = {"Speaker A": 1}  # Second utterance of Speaker A

        context = self.service.get_speaker_context("Speaker A", 1)

        # Should use normal before/current/after logic
        assert len(context) == 3
        assert context[0] == ("Speaker B", "Second utterance")  # Before
        assert context[1] == ("Speaker A", "Third utterance")   # Current
        assert context[2] == ("Speaker C", "Fourth utterance")  # After

    def test_display_speaker_context(self, capsys):
        """Test displaying speaker context."""
        self.service.utterances = [
            ("Speaker A", "First utterance"),
            ("Speaker B", "Second utterance that is quite long and should be truncated at 200 characters to test the truncation functionality properly and ensure it works with the new longer limit"),
            ("Speaker A", "Third utterance"),
        ]

        self.service.display_speaker_context("Speaker B", 1)

        captured = capsys.readouterr()
        output = captured.out

        assert "Context for Speaker B:" in output
        assert "Speaker A: First utterance" in output
        assert "Speaker B: Second utterance that is quite long and should be truncated at 200 characters to test the truncation functionality properly and ensure it works with the new longer limit" in output
        assert "Speaker A: Third utterance" in output
        assert "-" * 50 in output

    def test_display_speaker_context_no_context(self, capsys):
        """Test displaying context for non-existent speaker."""
        self.service.display_speaker_context("Speaker C")

        captured = capsys.readouterr()
        assert "No context found for Speaker C" in captured.out

    @patch('builtins.input')
    def test_prompt_for_speaker_name_with_context(self, mock_input, capsys):
        """Test prompting for speaker name with context display."""
        mock_input.side_effect = ["Bob", "y"]

        self.service.utterances = [
            ("Speaker A", "First utterance"),
            ("Speaker A", "Second utterance"),
        ]

        result = self.service.prompt_for_speaker_name("Speaker A", show_context=True)

        assert result == "Bob"
        captured = capsys.readouterr()
        assert "Context for Speaker A:" in captured.out
        # Check that the confirmation prompt uses the new format
        mock_input.assert_any_call("Rename Speaker A to 'Bob'? [Y/n]: ")

    @patch('builtins.input')
    def test_prompt_for_speaker_name_without_context(self, mock_input):
        """Test prompting for speaker name without context display."""
        mock_input.side_effect = ["Alice", "y"]

        result = self.service.prompt_for_speaker_name("Speaker A", show_context=False)

        assert result == "Alice"

    @patch('builtins.input')
    def test_prompt_for_speaker_name_empty_input(self, mock_input):
        """Test prompting with empty input (keep original name)."""
        mock_input.side_effect = ["", "y"]

        result = self.service.prompt_for_speaker_name("Speaker A")

        assert result == "Speaker A"
        # Check that the confirmation prompt uses the new format
        mock_input.assert_any_call("Keep Speaker A as 'Speaker A'? [Y/n]: ")

    @patch('builtins.input')
    def test_prompt_for_speaker_name_more_command(self, mock_input, capsys):
        """Test the 'more' command functionality."""
        mock_input.side_effect = ["more", "Charlie", "y"]

        self.service.utterances = [
            ("Speaker A", "First utterance"),
            ("Speaker A", "Second utterance"),
            ("Speaker A", "Third utterance"),
        ]
        self.service.speaker_utterance_indices = {"Speaker A": 0}

        result = self.service.prompt_for_speaker_name("Speaker A", show_context=True)

        assert result == "Charlie"
        # Should have displayed context twice (once initially, once for "more")
        captured = capsys.readouterr()
        assert captured.out.count("Context for Speaker A:") == 2
        # Verify that the utterance index advanced
        assert self.service.speaker_utterance_indices["Speaker A"] == 1

    @patch('builtins.input')
    def test_prompt_for_speaker_name_rejection_and_retry(self, mock_input):
        """Test rejection and retry functionality."""
        mock_input.side_effect = ["Bob", "n", "Alice", "y"]

        result = self.service.prompt_for_speaker_name("Speaker A")

        assert result == "Alice"
        # Check that the confirmation prompts use the new format
        mock_input.assert_any_call("Rename Speaker A to 'Bob'? [Y/n]: ")
        mock_input.assert_any_call("Rename Speaker A to 'Alice'? [Y/n]: ")

    @patch('builtins.input')
    def test_process_speaker_naming_success(self, mock_input):
        """Test successful speaker naming process."""
        mock_input.side_effect = ["Bob", "y", "Alice", "y", "Charlie", "y"]

        # Set up speakers and utterances
        self.service.speakers = {"Speaker A": "Speaker A", "Speaker B": "Speaker B", "Speaker C": "Speaker C"}
        self.service.utterances = [
            ("Speaker A", "First utterance"),
            ("Speaker B", "Second utterance"),
            ("Speaker C", "Third utterance"),
        ]

        result = self.service.process_speaker_naming()

        assert result is True
        assert self.service.speakers["Speaker A"] == "Bob"
        assert self.service.speakers["Speaker B"] == "Alice"
        assert self.service.speakers["Speaker C"] == "Charlie"

    def test_process_speaker_naming_no_utterances(self):
        """Test speaker naming with no utterances."""
        result = self.service.process_speaker_naming()
        assert result is False

    def test_process_speaker_naming_single_speaker(self, capsys):
        """Test speaker naming with single speaker."""
        # Set up single speaker
        self.service.speakers = {"Speaker A": "Speaker A"}
        self.service.utterances = [
            ("Speaker A", "First utterance"),
            ("Speaker A", "Second utterance"),
        ]

        with patch('builtins.input', side_effect=["Bob", "y"]):
            result = self.service.process_speaker_naming()

        assert result is True
        assert self.service.speakers["Speaker A"] == "Bob"
        
        # Check that the single speaker message was displayed
        captured = capsys.readouterr()
        assert "Found 1 speaker: Speaker A" in captured.out

    def test_apply_speaker_names_success(self):
        """Test successful application of speaker names."""
        # Set up speakers with some renamed
        self.service.speakers = {
            "Speaker A": "Bob",
            "Speaker B": "Speaker B",  # Not renamed
            "Speaker C": "Alice",
        }

        original_content = """Speaker A: Hello there
Speaker B: How are you?
Speaker C: I'm fine, thanks
Speaker A: That's great
"""


        with patch("builtins.open", mock_open(read_data=original_content)) as mock_file:
            mock_file.return_value.__enter__.return_value.write.side_effect = None
            result = self.service.apply_speaker_names()

        assert result is True
        # Verify write was called
        mock_file.return_value.__enter__.return_value.write.assert_called()

    def test_apply_speaker_names_no_changes(self):
        """Test applying speaker names when no changes are needed."""
        self.service.speakers = {
            "Speaker A": "Speaker A",
            "Speaker B": "Speaker B",
        }

        original_content = """Speaker A: Hello
Speaker B: Hi there
"""

        with patch("builtins.open", mock_open(read_data=original_content)):
            result = self.service.apply_speaker_names()

        assert result is True

    def test_apply_speaker_names_file_error(self):
        """Test applying speaker names with file error."""
        self.service.speakers = {"Speaker A": "Bob"}

        with patch("builtins.open", side_effect=OSError("File error")):
            result = self.service.apply_speaker_names()

        assert result is False

    def test_apply_speaker_names_only_replaces_at_line_start(self):
        """Test that speaker replacement only happens at line start."""
        self.service.speakers = {"Speaker A": "Bob"}

        original_content = """Hello Speaker A: this should not change
Speaker A: This should change to Bob
Some text Speaker A: also should not change
"""


        with patch("builtins.open", mock_open(read_data=original_content)):
            result = self.service.apply_speaker_names()

        assert result is True

    @patch('transcripter.speaker_naming_service.SpeakerNamingService.analyze_transcript')
    @patch('transcripter.speaker_naming_service.SpeakerNamingService.process_speaker_naming')
    @patch('transcripter.speaker_naming_service.SpeakerNamingService.apply_speaker_names')
    def test_run_interactive_naming_success(self, mock_apply, mock_process, mock_analyze):
        """Test successful interactive naming process."""
        mock_analyze.return_value = True
        mock_process.return_value = True
        mock_apply.return_value = True

        result = self.service.run_interactive_naming()

        assert result is True
        mock_analyze.assert_called_once()
        mock_process.assert_called_once()
        mock_apply.assert_called_once()

    @patch('transcripter.speaker_naming_service.SpeakerNamingService.analyze_transcript')
    def test_run_interactive_naming_analysis_fails(self, mock_analyze):
        """Test interactive naming when analysis fails."""
        mock_analyze.return_value = False

        result = self.service.run_interactive_naming()

        assert result is False

    @patch('transcripter.speaker_naming_service.SpeakerNamingService.analyze_transcript')
    @patch('transcripter.speaker_naming_service.SpeakerNamingService.process_speaker_naming')
    def test_run_interactive_naming_process_cancelled(self, mock_process, mock_analyze):
        """Test interactive naming when process is cancelled."""
        mock_analyze.return_value = True
        mock_process.return_value = False

        result = self.service.run_interactive_naming()

        assert result is False

    @patch('transcripter.speaker_naming_service.SpeakerNamingService.analyze_transcript')
    @patch('transcripter.speaker_naming_service.SpeakerNamingService.process_speaker_naming')
    @patch('transcripter.speaker_naming_service.SpeakerNamingService.apply_speaker_names')
    def test_run_interactive_naming_apply_fails(self, mock_apply, mock_process, mock_analyze):
        """Test interactive naming when apply fails."""
        mock_analyze.return_value = True
        mock_process.return_value = True
        mock_apply.return_value = False

        result = self.service.run_interactive_naming()

        assert result is False
