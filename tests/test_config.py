"""Tests for configuration management."""

import os
from pathlib import Path
from unittest.mock import patch

from transcripter.config import (
    TranscripterConfig,
    generate_correlation_id,
    get_correlation_id,
    set_correlation_id,
)


class TestTranscripterConfig:
    """Test TranscripterConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = TranscripterConfig()

        assert config.assemblyai_api_key == ""
        assert config.log_level == "INFO"
        assert config.output_dir == Path("./data/output")
        assert config.max_retries == 3
        assert config.timeout == 300

    def test_config_from_env_vars(self):
        """Test configuration from environment variables."""
        env_vars = {
            "TRANSCRIPTER_ASSEMBLYAI_API_KEY": "test_api_key",
            "TRANSCRIPTER_LOG_LEVEL": "DEBUG",
            "TRANSCRIPTER_MAX_RETRIES": "5",
            "TRANSCRIPTER_TIMEOUT": "600"
        }

        with patch.dict(os.environ, env_vars):
            config = TranscripterConfig()

            assert config.assemblyai_api_key == "test_api_key"
            assert config.log_level == "DEBUG"
            assert config.max_retries == 5
            assert config.timeout == 600

    def test_output_dir_creation(self):
        """Test that output directory is created during initialization."""
        test_dir = Path("./test_output_dir")
        
        # Mock the mkdir method
        with patch.object(Path, 'mkdir') as mock_mkdir:
            config = TranscripterConfig(output_dir=test_dir)
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestCorrelationID:
    """Test correlation ID functionality."""

    def test_generate_correlation_id(self):
        """Test correlation ID generation."""
        cid1 = generate_correlation_id()
        cid2 = generate_correlation_id()

        # Should be different UUIDs
        assert cid1 != cid2
        assert len(cid1) == 36  # UUID string length
        assert len(cid2) == 36

    def test_get_correlation_id_without_set(self):
        """Test getting correlation ID when none is set."""
        # Clear any existing correlation ID
        set_correlation_id("")
        # Get a new correlation ID
        cid = get_correlation_id()
        
        # Should generate a new one
        assert len(cid) == 36

    def test_set_and_get_correlation_id(self):
        """Test setting and getting correlation ID."""
        test_cid = "test-correlation-id"
        set_correlation_id(test_cid)

        retrieved_cid = get_correlation_id()
        assert retrieved_cid == test_cid
