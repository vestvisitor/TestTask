from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    login: str
    password: str

    arguments: List[str]

    model_config = SettingsConfigDict(
        env_file=".env"
    )


settings = Settings()
