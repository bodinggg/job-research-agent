"""LLM client using OpenAI-compatible API."""
from langchain_openai import ChatOpenAI
from src.config import settings


def create_llm(
    model: str = None,
    temperature: float = 0.1,
) -> ChatOpenAI:
    """Create an LLM client configured for current provider.

    Args:
        model: Model name (defaults to settings.llm_model_name)
        temperature: Sampling temperature

    Returns:
        Configured ChatOpenAI instance
    """
    return ChatOpenAI(
        model=model or settings.llm_model_name,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=temperature,
    )


# Singleton instance
_llm = None


def get_llm() -> ChatOpenAI:
    """Get or create LLM singleton."""
    global _llm
    if _llm is None:
        _llm = create_llm()
    return _llm