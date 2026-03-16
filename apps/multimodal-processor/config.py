"""
Configuration for Multimodal Processor
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    app_name: str = "LocalDBKit Multimodal Processor"
    app_version: str = "0.3.0"
    api_prefix: str = "/api/v1"

    # Tesseract OCR
    tesseract_lang: str = "eng+jpn"

    # Whisper
    whisper_model: str = "base"  # tiny, base, small, medium, large

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
    ]

    # File size limits (bytes)
    max_image_size: int = 10 * 1024 * 1024  # 10MB
    max_pdf_size: int = 50 * 1024 * 1024  # 50MB
    max_audio_size: int = 100 * 1024 * 1024  # 100MB
    max_video_size: int = 500 * 1024 * 1024  # 500MB

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    """Get settings instance"""
    return Settings()
