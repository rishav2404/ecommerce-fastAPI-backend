# """
# Configuration settings for the FastAPI e-commerce application.
# Manages environment variables and application settings.
# """
# from typing import Optional
# from pydantic import BaseSettings


# class Settings(BaseSettings):
#     """Application settings with environment variable support."""
    
#     # Database settings
#     mongodb_url: str
#     database_name: str
    
#     # Application settings
#     debug: bool = False
#     host: str = "0.0.0.0"
#     port: int = 8000
    
#     class Config:
#         env_file = ".env"
#         case_sensitive = False


# # Global settings instance
# settings = Settings()



"""
Configuration settings for the FastAPI e-commerce application.
Manages environment variables and application settings.
"""
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database settings
    mongodb_url: str
    database_name: str
    
    # Application settings
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()