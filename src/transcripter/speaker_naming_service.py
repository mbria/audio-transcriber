"""Speaker naming service for interactive speaker identification and renaming."""

import re
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


class SpeakerNamingService:
    """Service for interactive speaker naming in transcription files."""

    def __init__(self, transcript_file: Path):
        """Initialize the service with a transcript file.

        Args:
            transcript_file: Path to the transcript file to process
        """
        self.transcript_file = transcript_file
        self.speakers: dict[str, str] = {}  # Original -> New name mapping
        self.utterances: list[tuple[str, str]] = []  # (speaker, content) pairs
        self.speaker_utterance_indices: dict[str, int] = {}  # Track current utterance index for each speaker

    def analyze_transcript(self) -> bool:
        """Analyze the transcript to identify speakers and utterances.

        Returns:
            True if speakers were found, False otherwise
        """
        try:
            with open(self.transcript_file, encoding='utf-8') as f:
                content = f.read()

            # Split into lines and process
            lines = content.strip().split('\n')
            speaker_pattern = re.compile(r'^Speaker ([A-Z]+):\s*(.+)$')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                match = speaker_pattern.match(line)
                if match:
                    speaker_id = f"Speaker {match.group(1)}"
                    utterance = match.group(2).strip()
                    self.utterances.append((speaker_id, utterance))

            # Extract unique speakers
            unique_speakers = {speaker for speaker, _ in self.utterances}
            self.speakers = {speaker: speaker for speaker in unique_speakers}

            # Initialize utterance indices for each speaker (start at 0 for first occurrence)
            self.speaker_utterance_indices = dict.fromkeys(unique_speakers, 0)

            logger.info("Transcript analysis complete",
                       speakers_found=len(self.speakers),
                       utterances_found=len(self.utterances))

            return len(self.speakers) > 0

        except Exception as e:
            logger.error("Failed to analyze transcript", error=str(e))
            return False

    def get_speaker_context(self, speaker_id: str, utterance_index: int | None = None) -> list[tuple[str, str]]:
        """Get 3-utterance context for a speaker (before, current, after).

        Args:
            speaker_id: The speaker to get context for
            utterance_index: Index of the target utterance (if None, use tracked index)

        Returns:
            List of (speaker, content) tuples for context
        """
        context = []

        # Find all utterances for this speaker
        target_utterances = [(i, speaker, content) for i, (speaker, content)
                           in enumerate(self.utterances) if speaker == speaker_id]

        if not target_utterances:
            return context

        # Use tracked index if no specific index provided
        if utterance_index is None:
            utterance_index = self.speaker_utterance_indices.get(speaker_id, 0)

        # Ensure index is within bounds
        if utterance_index >= len(target_utterances):
            utterance_index = len(target_utterances) - 1

        # Get the target utterance index
        target_index = target_utterances[utterance_index][0]

        # Special case: if this is the first utterance of the first speaker (index 0),
        # show current + next 2 instead of before/current/after
        if target_index == 0 and utterance_index == 0:
            # Show current utterance
            current_speaker, current_content = self.utterances[target_index]
            context.append((current_speaker, current_content))

            # Show next 2 utterances (if they exist)
            for i in range(1, 3):
                if target_index + i < len(self.utterances):
                    next_speaker, next_content = self.utterances[target_index + i]
                    context.append((next_speaker, next_content))
        else:
            # Normal case: before, current, after
            # Get previous utterance (if exists)
            if target_index > 0:
                prev_speaker, prev_content = self.utterances[target_index - 1]
                context.append((prev_speaker, prev_content))

            # Get current utterance
            current_speaker, current_content = self.utterances[target_index]
            context.append((current_speaker, current_content))

            # Get next utterance (if exists)
            if target_index < len(self.utterances) - 1:
                next_speaker, next_content = self.utterances[target_index + 1]
                context.append((next_speaker, next_content))

        return context

    def display_speaker_context(self, speaker_id: str, utterance_index: int | None = None) -> None:
        """Display 3-utterance context for a speaker.

        Args:
            speaker_id: The speaker to show context for
            utterance_index: Index of the target utterance (default: tracked index)
        """
        context = self.get_speaker_context(speaker_id, utterance_index)

        if not context:
            print(f"No context found for {speaker_id}")
            return

        print(f"\nContext for {speaker_id}:")
        print("-" * 50)

        for speaker, content in context:
            # Truncate content to 200 chars for readability
            truncated_content = content[:200] + "..." if len(content) > 200 else content
            print(f"{speaker}: {truncated_content}")

            print("-" * 50)

    def advance_speaker_utterance_index(self, speaker_id: str) -> bool:
        """Advance to the next utterance for a speaker.

        Args:
            speaker_id: The speaker to advance

        Returns:
            True if advanced successfully, False if no more utterances
        """
        # Find all utterances for this speaker
        target_utterances = [(i, speaker, content) for i, (speaker, content)
                           in enumerate(self.utterances) if speaker == speaker_id]

        if not target_utterances:
            return False

        current_index = self.speaker_utterance_indices.get(speaker_id, 0)

        # Advance to next utterance if available
        if current_index < len(target_utterances) - 1:
            self.speaker_utterance_indices[speaker_id] = current_index + 1
            return True
        else:
            return False

    def prompt_for_speaker_name(self, speaker_id: str, show_context: bool = False) -> str:
        """Prompt user for a speaker name.

        Args:
            speaker_id: The speaker being renamed
            show_context: Whether to show context before prompting

        Returns:
            The new name for the speaker
        """
        if show_context:
            self.display_speaker_context(speaker_id)

        while True:
            user_input = input(f"\n{speaker_id}?: ").strip()

            if user_input.lower() == "more":
                if self.advance_speaker_utterance_index(speaker_id):
                    self.display_speaker_context(speaker_id)
                else:
                    print(f"No more utterances available for {speaker_id}")
                continue

            # Confirm the choice
            if user_input:
                confirm = input(f"Rename {speaker_id} to '{user_input}'? [Y/n]: ").strip().lower()
                if confirm in ['', 'y', 'yes']:
                    return user_input
                else:
                    continue
            else:
                # Empty input - keep original name
                confirm = input(f"Keep {speaker_id} as '{speaker_id}'? [Y/n]: ").strip().lower()
                if confirm in ['', 'y', 'yes']:
                    return speaker_id
                else:
                    continue

    def process_speaker_naming(self) -> bool:
        """Process interactive speaker naming.

        Returns:
            True if processing completed successfully, False otherwise
        """
        if not self.utterances:
            print("No speakers found in transcript.")
            return False

        sorted_speakers = sorted(self.speakers.keys())
        print(f"\nFound {len(sorted_speakers)} speakers: {', '.join(sorted_speakers)}")

        # Process each speaker
        for i, speaker_id in enumerate(sorted_speakers):
            # Show context for first speaker by default
            show_context = (i == 0)

            new_name = self.prompt_for_speaker_name(speaker_id, show_context=show_context)
            self.speakers[speaker_id] = new_name

            if new_name != speaker_id:
                logger.info("Speaker renamed", original=speaker_id, new=new_name)

        return True

    def apply_speaker_names(self) -> bool:
        """Apply the new speaker names to the transcript file.

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.transcript_file, encoding='utf-8') as f:
                content = f.read()

            # Replace speaker names
            for original_name, new_name in self.speakers.items():
                if original_name != new_name:
                    # Replace at the beginning of lines only
                    pattern = f"^{re.escape(original_name)}:"
                    replacement = f"{new_name}:"
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

            # Write back to file
            with open(self.transcript_file, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info("Speaker names applied to transcript",
                       replacements=len([k for k, v in self.speakers.items() if k != v]))

            return True

        except Exception as e:
            logger.error("Failed to apply speaker names", error=str(e))
            return False

    def run_interactive_naming(self) -> bool:
        """Run the complete interactive speaker naming process.

        Returns:
            True if completed successfully, False otherwise
        """
        print("Starting speaker naming process...")

        # Analyze transcript
        if not self.analyze_transcript():
            print("Failed to analyze transcript or no speakers found.")
            return False

        # Process naming
        if not self.process_speaker_naming():
            print("Speaker naming process was cancelled.")
            return False

        # Apply changes
        if not self.apply_speaker_names():
            print("Failed to apply speaker name changes.")
            return False

        print("Speaker naming completed successfully!")
        return True
