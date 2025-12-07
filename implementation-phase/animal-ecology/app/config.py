from functools import lru_cache
from pathlib import Path
import os

from pydantic import BaseModel


class Settings(BaseModel):
    api_token: str = "dev-token"
    db_path: Path = Path("data/config.db")
    config_signing_salt: str = "dev-salt"


@lru_cache()
def get_settings() -> Settings:
    """Load settings from environment with safe defaults."""
    return Settings(
        api_token=os.getenv("API_TOKEN", "dev-token"),
        db_path=Path(os.getenv("DB_PATH", "data/config.db")),
        config_signing_salt=os.getenv("CONFIG_SIGNING_SALT", "dev-salt"),
    )
