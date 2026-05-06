"""Embedding client using OpenAI-compatible API (SiliconFlow)."""
from langchain_openai import OpenAIEmbeddings
from src.config import settings


def create_embeddings() -> OpenAIEmbeddings:
    """Create an embeddings client configured for current embedding provider.

    Returns:
        Configured OpenAIEmbeddings instance
    """
    if settings.embedding_provider == "siliconflow":
        return OpenAIEmbeddings(
            model=settings.siliconflow_embedding_model,
            api_key=settings.siliconflow_api_key,
            base_url=settings.siliconflow_base_url,
        )
    elif settings.embedding_provider == "openai":
        return OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
        )
    else:
        # Default to SiliconFlow
        return OpenAIEmbeddings(
            model=settings.siliconflow_embedding_model,
            api_key=settings.siliconflow_api_key,
            base_url=settings.siliconflow_base_url,
        )


# Singleton instance
_embeddings = None


def get_embeddings() -> OpenAIEmbeddings:
    """Get or create embeddings singleton."""
    global _embeddings
    if _embeddings is None:
        _embeddings = create_embeddings()
    return _embeddings