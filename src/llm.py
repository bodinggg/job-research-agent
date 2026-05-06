"""LLM client using OpenAI-compatible API (SiliconFlow)."""
from langchain_openai import ChatOpenAI
from src.config import settings


def create_llm(
    model: str = None,
    temperature: float = 0.1,
) -> ChatOpenAI:
    """Create an LLM client configured for SiliconFlow API.

    Args:
        model: Model name (defaults to settings.model)
        temperature: Sampling temperature

    Returns:
        Configured ChatOpenAI instance
    """
    return ChatOpenAI(
        model=model or settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url,
        temperature=temperature,
    )
