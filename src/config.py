"""Configuration settings with multi-provider support."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with support for multiple LLM/embedding providers."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # =============================================================================
    # LLM Provider Configuration
    # =============================================================================
    # Supported providers: siliconflow, groq, openai
    llm_provider: str = "siliconflow"

    # SiliconFlow (OpenAI-compatible)
    siliconflow_api_key: str = ""
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"
    siliconflow_model: str = "Qwen/Qwen2.5-72B-Instruct"

    # Groq
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # =============================================================================
    # Embedding Provider Configuration
    # =============================================================================
    # Supported providers: siliconflow, openai, local
    embedding_provider: str = "siliconflow"

    # SiliconFlow Embedding
    siliconflow_embedding_model: str = "BAAI/bge-large-zh-v1.5"

    # OpenAI Embedding
    openai_embedding_model: str = "Qwen/Qwen3-Embedding-8B"

    # =============================================================================
    # Search Configuration
    # =============================================================================
    tavily_api_key: str = ""

    # =============================================================================
    # Qdrant Configuration
    # =============================================================================
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "job_research"

    # =============================================================================
    # Server Configuration
    # =============================================================================
    api_host: str = "0.0.0.0"
    api_port: int = 8002

    # =============================================================================
    # Search Configuration
    # =============================================================================
    max_search_results: int = 5
    search_timeout: int = 30

    # =============================================================================
    # Provider Accessors
    # =============================================================================
    @property
    def api_key(self) -> str:
        """Get API key based on current LLM provider."""
        if self.llm_provider == "siliconflow":
            return self.siliconflow_api_key
        elif self.llm_provider == "groq":
            return self.groq_api_key
        elif self.llm_provider == "openai":
            return self.openai_api_key
        return ""

    @property
    def base_url(self) -> str:
        """Get base URL based on current LLM provider."""
        if self.llm_provider == "siliconflow":
            return self.siliconflow_base_url
        elif self.llm_provider == "groq":
            return "https://api.groq.com/openai/v1"
        elif self.llm_provider == "openai":
            return "https://api.openai.com/v1"
        return ""

    @property
    def model(self) -> str:
        """Get model name based on current LLM provider."""
        if self.llm_provider == "siliconflow":
            return self.siliconflow_model
        elif self.llm_provider == "groq":
            return self.groq_model
        elif self.llm_provider == "openai":
            return self.openai_model
        return ""

    @property
    def embedding_model(self) -> str:
        """Get embedding model based on current embedding provider."""
        if self.embedding_provider == "siliconflow":
            return self.siliconflow_embedding_model
        elif self.embedding_provider == "openai":
            return self.openai_embedding_model
        return self.siliconflow_embedding_model


settings = Settings()
