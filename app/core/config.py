from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


def get_cors_origins() -> List[str]:
    """Parse CORS_ORIGINS from environment variable"""
    cors_origins_str = os.getenv("CORS_ORIGINS", "")
    if cors_origins_str:
        # Parse comma-separated string or JSON-like string
        if cors_origins_str.startswith("[") and cors_origins_str.endswith("]"):
            # Try to parse as JSON-like string
            import json
            try:
                return json.loads(cors_origins_str)
            except:
                # Fallback: split by comma
                return [origin.strip().strip('"').strip("'") for origin in cors_origins_str.strip("[]").split(",") if origin.strip()]
        else:
            # Comma-separated string
            return [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]
    # Default origins
    return [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Financial Management API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",  # Ignore extra fields like CORS_ORIGINS
    }


# Create settings instance
_base_settings = Settings()

# Create a wrapper that includes CORS_ORIGINS
class SettingsWrapper:
    def __init__(self, base_settings: Settings):
        self._base = base_settings
        self.CORS_ORIGINS = get_cors_origins()
    
    def __getattr__(self, name):
        return getattr(self._base, name)


settings = SettingsWrapper(_base_settings)
