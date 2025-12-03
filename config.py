import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOG_DIR: Path = BASE_DIR / "logs"
    
    # Allow overriding via environment variables
    # e.g. TAIFEX_DATA_DIR=/tmp/data
    model_config = {
        "env_prefix": "TAIFEX_",
        "case_sensitive": True
    }

settings = Settings()

# Ensure directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.LOG_DIR, exist_ok=True)
