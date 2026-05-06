"""Configuration settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM API Configuration (SiliconFlow / OpenAI compatible)
    api_key: str = ""
    base_url: str = "https://api.siliconflow.cn/v1"
    api_type: str = "openai"  # "openai" or "groq"

    # Model Configuration
    model: str = "Qwen/Qwen2.5-72B-Instruct"  # SiliconFlow model
    embedding_model: str = "BAAI/bge-large-zh-v1.5"  # Embedding model for RAG
    groq_model: str = "llama-3.3-70b-versatile"  # Groq model fallback
    google_model: str = "gemini-2.0-flash"

    # Optional: Tavily search
    tavily_api_key: str = ""

    # Qdrant Configuration
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "job_research"

    # Server Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Search Configuration
    max_search_results: int = 5
    search_timeout: int = 30


settings = Settings()
