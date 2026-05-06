"""Embedding client using OpenAI-compatible API."""
from langchain_openai import OpenAIEmbeddings
from src.config import settings


def create_embeddings() -> OpenAIEmbeddings:
    """Create an embeddings client configured for current provider.

    Returns:
        Configured OpenAIEmbeddings instance
    """
    return OpenAIEmbeddings(
        model=settings.embedding_model_name,
        api_key=settings.embedding_api_key,
        base_url=settings.embedding_base_url,
    )


# Singleton instance
_embeddings = None


def get_embeddings() -> OpenAIEmbeddings:
    """Get or create embeddings singleton."""
    global _embeddings
    if _embeddings is None:
        _embeddings = create_embeddings()
    return _embeddings