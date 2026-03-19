from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    DB_PATH: str = "./data/medicos.db"

    class Config:
        env_file = ".env"

settings = Settings()
