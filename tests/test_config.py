"""Tests for config module."""
import pytest
from src.config import Settings


class TestSettings:
    """Tests for Settings configuration."""

    def test_default_provider_is_siliconflow(self):
        """Test default LLM provider is siliconflow."""
        settings = Settings()
        assert settings.llm_provider == "siliconflow"

    def test_default_embedding_provider_is_siliconflow(self):
        """Test default embedding provider is siliconflow."""
        settings = Settings()
        assert settings.embedding_provider == "siliconflow"

    def test_provider_api_key_siliconflow(self):
        """Test API key returns correct provider key."""
        settings = Settings()
        settings.siliconflow_api_key = "test_siliconflow_key"
        assert settings.api_key == "test_siliconflow_key"

    def test_provider_api_key_groq(self):
        """Test API key returns Groq key when provider is groq."""
        settings = Settings()
        settings.llm_provider = "groq"
        settings.groq_api_key = "test_groq_key"
        assert settings.api_key == "test_groq_key"

    def test_provider_api_key_openai(self):
        """Test API key returns OpenAI key when provider is openai."""
        settings = Settings()
        settings.llm_provider = "openai"
        settings.openai_api_key = "test_openai_key"
        assert settings.api_key == "test_openai_key"

    def test_provider_base_url_siliconflow(self):
        """Test base URL returns correct provider URL."""
        settings = Settings()
        settings.siliconflow_base_url = "https://api.siliconflow.cn/v1"
        assert settings.base_url == "https://api.siliconflow.cn/v1"

    def test_provider_base_url_groq(self):
        """Test base URL returns Groq URL when provider is groq."""
        settings = Settings()
        settings.llm_provider = "groq"
        assert settings.base_url == "https://api.groq.com/openai/v1"

    def test_provider_base_url_openai(self):
        """Test base URL returns OpenAI URL when provider is openai."""
        settings = Settings()
        settings.llm_provider = "openai"
        assert settings.base_url == "https://api.openai.com/v1"

    def test_provider_model_siliconflow(self):
        """Test model returns correct provider model."""
        settings = Settings()
        settings.siliconflow_model = "Qwen/Qwen2.5-72B-Instruct"
        assert settings.model == "Qwen/Qwen2.5-72B-Instruct"

    def test_provider_model_groq(self):
        """Test model returns Groq model when provider is groq."""
        settings = Settings()
        settings.llm_provider = "groq"
        settings.groq_model = "llama-3.3-70b-versatile"
        assert settings.model == "llama-3.3-70b-versatile"

    def test_provider_model_openai(self):
        """Test model returns OpenAI model when provider is openai."""
        settings = Settings()
        settings.llm_provider = "openai"
        settings.openai_model = "gpt-4o"
        assert settings.model == "gpt-4o"

    def test_embedding_model_siliconflow(self):
        """Test embedding model returns SiliconFlow model."""
        settings = Settings()
        settings.siliconflow_embedding_model = "BAAI/bge-large-zh-v1.5"
        assert settings.embedding_model == "BAAI/bge-large-zh-v1.5"

    def test_embedding_model_openai(self):
        """Test embedding model returns OpenAI model when provider is openai."""
        settings = Settings()
        settings.embedding_provider = "openai"
        settings.openai_embedding_model = "text-embedding-3-large"
        assert settings.embedding_model == "text-embedding-3-large"

    def test_qdrant_defaults(self):
        """Test Qdrant configuration defaults."""
        settings = Settings()
        assert settings.qdrant_host == "localhost"
        assert settings.qdrant_port == 6333
        assert settings.qdrant_collection == "job_research"

    def test_server_defaults(self):
        """Test server configuration defaults."""
        settings = Settings()
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8002

    def test_search_defaults(self):
        """Test search configuration defaults."""
        settings = Settings()
        assert settings.max_search_results == 5
        assert settings.search_timeout == 30