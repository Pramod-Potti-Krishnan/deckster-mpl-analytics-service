"""
Configuration Settings for Analytics Microservice V2

REUSES existing environment variables and adds WebSocket-specific configuration.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os


class Settings(BaseSettings):
    """
    Configuration settings for Analytics Microservice V2.
    Reuses existing analytics configuration and adds WebSocket settings.
    """
    
    # Service configuration
    service_name: str = Field(default="analytics-microservice-v2", description="Service name")
    port: int = Field(default=8000, description="Service port")
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    
    # WebSocket configuration
    ws_url: str = Field(default="/ws", description="WebSocket endpoint URL")
    ws_timeout: int = Field(default=300, description="WebSocket timeout in seconds")
    max_connections: int = Field(default=100, description="Maximum concurrent connections")
    
    # LLM configuration - REUSED from existing analytics
    llm_provider: str = Field(default="gemini", description="LLM provider (gemini, openai)")
    google_api_key: str = Field(default="", description="Google API key for Gemini")
    openai_api_key: str = Field(default="", description="OpenAI API key")
    
    # Analytics configuration - UNCHANGED from existing
    enable_synthetic_data: bool = Field(default=True, description="Enable synthetic data generation")
    enable_llm_enhancement: bool = Field(default=True, description="Enable LLM label enhancement")
    default_theme: str = Field(default="modern", description="Default theme style")
    max_data_points: int = Field(default=10000, description="Maximum data points per chart")
    
    # Rate limiting - REUSED from existing
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=60, description="Requests per window")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # CORS configuration
    cors_origins: str = Field(default="*", description="Allowed CORS origins")
    
    # Cache configuration (optional future enhancement)
    enable_cache: bool = Field(default=False, description="Enable response caching")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    log_level: str = Field(default="INFO", description="Logging level")
    
    def get_cors_origins_list(self) -> List[str]:
        """Parse CORS origins from string"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def has_llm_configured(self) -> bool:
        """Check if any LLM provider is configured"""
        return bool(self.google_api_key or self.openai_api_key)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


def get_settings() -> Settings:
    """Get settings instance"""
    return Settings()