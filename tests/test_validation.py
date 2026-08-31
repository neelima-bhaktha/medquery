import os
from unittest.mock import patch

import pytest

from src.config.validation import validate_config


def test_validate_config_success():
    with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_mock_test_key_12345"}):
        # Should not raise exception
        validate_config(strict=True)


@patch("src.config.validation.load_dotenv")
def test_validate_config_missing_key_raises_runtime_error(mock_load_dotenv):
    with patch.dict(os.environ, {}, clear=True):
        # Ensure GROQ_API_KEY is completely cleared from environment
        os.environ.pop("GROQ_API_KEY", None)
        os.environ.pop("groq_api_key", None)

        with pytest.raises(RuntimeError) as exc_info:
            validate_config(strict=True)

        assert "GROQ_API_KEY" in str(exc_info.value)
        assert "CRITICAL STARTUP ERROR" in str(exc_info.value)
