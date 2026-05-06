"""Tests for config module."""
import pytest
from src.config import Settings


class TestSettings:
    """Tests for Settings configuration."""

    def test_env_value_loading(self):
        """Test settings loaded from .env file."""
        settings = Settings()
        # Siliconflow API
        assert settings.llm_provider == "openai"
        assert settings.llm_base_url == "https://api.siliconflow.cn/v1"
        assert settings.llm_model_name == "Pro/deepseek-ai/DeepSeek-V3.2"
        assert settings.llm_api_key == "sk-tbtajmqautrqqpcwgllvjiebuwkjlxpetxkwbaztpmuoczyy"
        # Embedding
        assert settings.embedding_model_name == "Qwen/Qwen3-Embedding-8B"
        # Qdrant
        assert settings.qdrant_host == "localhost"
        assert settings.qdrant_port == 6333
        # Server
        assert settings.api_port == 8002