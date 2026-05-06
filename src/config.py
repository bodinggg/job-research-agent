"""Configuration settings."""
import os
from dotenv import load_dotenv

load_dotenv()


def getenv(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def getenv_int(key: str, default: int = 0) -> int:
    return int(os.getenv(key, str(default)))


class Settings:
    """Application settings."""

    # LLM
    llm_provider: str = getenv("LLM_PROVIDER", "openai")
    llm_base_url: str = getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    llm_api_key: str = getenv("LLM_API_KEY", "")
    llm_model_name: str = getenv("LLM_MODEL_NAME", "gpt-4o")

    # Embedding
    embedding_provider: str = getenv("EMBEDDING_PROVIDER", "openai")
    embedding_base_url: str = getenv("EMBEDDING_BASE_URL", "https://api.openai.com/v1")
    embedding_api_key: str = getenv("EMBEDDING_API_KEY", "")
    embedding_model_name: str = getenv("EMBEDDING_MODEL_NAME", "text-embedding-3-large")

    # Search
    tavily_api_key: str = getenv("TAVILY_API_KEY", "")

    # Qdrant
    qdrant_host: str = getenv("QDRANT_HOST", "localhost")
    qdrant_port: int = getenv_int("QDRANT_PORT", 6333)
    qdrant_collection: str = getenv("QDRANT_COLLECTION", "job_research")

    # Server
    api_host: str = getenv("API_HOST", "0.0.0.0")
    api_port: int = getenv_int("API_PORT", 8002)

    max_search_results: int = getenv_int("MAX_SEARCH_RESULTS", 5)
    search_timeout: int = getenv_int("SEARCH_TIMEOUT", 30)


settings = Settings()