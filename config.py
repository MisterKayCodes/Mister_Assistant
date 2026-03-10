from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    """
    Project Configuration (The DNA).
    Sensitive data is loaded from .env or environment variables.
    """
    BOT_TOKEN: SecretStr
    ALLOWED_USER_ID: int = 0  # Initial owner ID, 0 means not set
    DATABASE_URL: str = "sqlite+aiosqlite:///data/mister_assistant.db"
    
    # Recovery Settings
    RECOVERY_KEY_ROOT: str = "MISTER-SECRET-RECOVERY"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
