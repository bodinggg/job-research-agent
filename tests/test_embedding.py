"""Tests for embedding module."""
import pytest
from unittest.mock import patch, MagicMock
from src.embedding import create_embeddings, get_embeddings


class TestCreateEmbeddings:
    """Tests for create_embeddings factory function."""

    @patch('src.embedding.settings')
    def test_create_embeddings_with_config(self, mock_settings):
        """Test creating embeddings with settings."""
        mock_settings.embedding_model_name = "text-embedding-3-large"
        mock_settings.embedding_api_key = "test_key"
        mock_settings.embedding_base_url = "https://api.openai.com/v1"

        embeddings = create_embeddings()

        assert embeddings.model == "text-embedding-3-large"
        assert embeddings.openai_api_base == "https://api.openai.com/v1"


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