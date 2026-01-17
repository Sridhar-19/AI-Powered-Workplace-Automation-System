"""
Configuration management for AI Workplace Automation System
Uses Pydantic Settings for type-safe configuration with environment variables
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Configuration
    env: str = Field(default="development", description="Environment: development, staging, production")
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Debug mode")
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="OpenAI model to use")
    openai_embedding_model: str = Field(default="text-embedding-3-small", description="Embedding model")
    openai_max_tokens: int = Field(default=4000, description="Maximum tokens for completion")
    openai_temperature: float = Field(default=0.7, description="Model temperature")
    
    # Pinecone Configuration
    pinecone_api_key: str = Field(..., description="Pinecone API key")
    pinecone_environment: str = Field(..., description="Pinecone environment")
    pinecone_index_name: str = Field(default="workplace-docs", description="Pinecone index name")
    pinecone_dimension: int = Field(default=1536, description="Vector dimension")
    
    # Microsoft Teams Bot Configuration
    microsoft_app_id: Optional[str] = Field(default=None, description="Azure Bot App ID")
    microsoft_app_password: Optional[str] = Field(default=None, description="Azure Bot App Password")
    microsoft_app_tenant_id: Optional[str] = Field(default=None, description="Azure Tenant ID")
    bot_endpoint: str = Field(default="/api/messages", description="Bot messaging endpoint")
    
    # Security
    secret_key: str = Field(..., description="Secret key for JWT tokens")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Token expiration time")
    
    # File Upload Configuration
    max_upload_size: int = Field(default=10485760, description="Max upload size in bytes (10MB)")
    allowed_extensions: List[str] = Field(default=["pdf", "docx", "txt", "doc"], description="Allowed file extensions")
    
    # Document Processing
    chunk_size: int = Field(default=1000, description="Document chunk size in tokens")
    chunk_overlap: int = Field(default=200, description="Chunk overlap in tokens")
    max_chunks_per_document: int = Field(default=100, description="Maximum chunks per document")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")
    rate_limit_burst: int = Field(default=100, description="Rate limit burst size")
    
    # Performance
    worker_count: int = Field(default=4, description="Number of workers")
    max_concurrent_requests: int = Field(default=100, description="Max concurrent requests")
    
    # Redis (Optional - for session management)
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials in CORS")
    
    @validator("allowed_extensions", pre=True)
    def parse_extensions(cls, v):
        """Parse allowed extensions from string or list"""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings
