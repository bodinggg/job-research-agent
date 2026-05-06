"""Embedding client using OpenAI-compatible API (SiliconFlow)."""
from langchain_openai import OpenAIEmbeddings
from src.config import settings


def create_embeddings() -> OpenAIEmbeddings:
    """Create an embeddings client configured for SiliconFlow API.

    Returns:
        Configured OpenAIEmbeddings instance
    """
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.api_key,
        base_url=settings.base_url,
    )


# Singleton instance
_embeddings = None


def get_embeddings() -> OpenAIEmbeddings:
    """Get or create embeddings singleton."""
    global _embeddings
    if _embeddings is None:
        _embeddings = create_embeddings()
    return _embeddings