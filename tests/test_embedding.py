"""Tests for embedding module."""
import pytest
from unittest.mock import patch, MagicMock
from src.embedding import create_embeddings, get_embeddings


class TestCreateEmbeddings:
    """Tests for create_embeddings factory function."""

    @patch('src.embedding.settings')
    def test_create_embeddings_siliconflow(self, mock_settings):
        """Test creating embeddings with SiliconFlow provider."""
        mock_settings.embedding_provider = "siliconflow"
        mock_settings.siliconflow_embedding_model = "BAAI/bge-large-zh-v1.5"
        mock_settings.siliconflow_api_key = "test_key"
        mock_settings.siliconflow_base_url = "https://api.siliconflow.cn/v1"

        embeddings = create_embeddings()

        assert embeddings.model == "BAAI/bge-large-zh-v1.5"
        assert embeddings.openai_api_base == "https://api.siliconflow.cn/v1"

    @patch('src.embedding.settings')
    def test_create_embeddings_openai(self, mock_settings):
        """Test creating embeddings with OpenAI provider."""
        mock_settings.embedding_provider = "openai"
        mock_settings.openai_embedding_model = "text-embedding-3-large"
        mock_settings.openai_api_key = "test_key"

        embeddings = create_embeddings()

        assert embeddings.model == "text-embedding-3-large"
        assert embeddings.openai_api_base is None  # OpenAI uses default base

    @patch('src.embedding.settings')
    def test_create_embeddings_default_fallback(self, mock_settings):
        """Test creating embeddings falls back to SiliconFlow."""
        mock_settings.embedding_provider = "unknown"
        mock_settings.siliconflow_embedding_model = "BAAI/bge-large-zh-v1.5"
        mock_settings.siliconflow_api_key = "test_key"
        mock_settings.siliconflow_base_url = "https://api.siliconflow.cn/v1"

        embeddings = create_embeddings()

        assert embeddings.model == "BAAI/bge-large-zh-v1.5"


class TestGetEmbeddings:
    """Tests for get_embeddings singleton."""

    def test_get_embeddings_returns_same_instance(self):
        """Test get_embeddings returns singleton."""
        # Reset singleton
        import src.embedding
        src.embedding._embeddings = None

        with patch('src.embedding.create_embeddings') as mock_create:
            mock_instance = MagicMock()
            mock_create.return_value = mock_instance

            result1 = get_embeddings()
            result2 = get_embeddings()

            assert result1 is result2
            assert result2 is mock_instance