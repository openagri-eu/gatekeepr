import os
import json

from typing import ClassVar
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "GateKeeper"
    debug: bool = True

    secret_key: str
    db_user: str
    db_name: str
    db_pass: str
    db_host: str
    db_port: str

    # Define token expiration settings with type annotations
    ACCESS_TOKEN_EXPIRE_HOURS: ClassVar[int] = 1
    REFRESH_TOKEN_EXPIRE_DAYS: ClassVar[int] = 7
    AUTH_TOKEN_EXPIRE_MINUTES: ClassVar[int] = 30

    JWT_SIGNING_KEY: str = os.getenv("JWT_SIGNING_KEY", "default_key")

    # Parse redirect URLs dynamically from environment variables
    redirects: dict = {}

    @property
    def database_url(self):
        return f"mysql+pymysql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        extra = "ignore"

    def load_redirects(self):
        # Load redirect URLs exclusively from redirects.json
        try:
            with open("redirects.json", "r") as f:
                self.redirects = json.load(f)
                print("Redirects loaded successfully.")
        except FileNotFoundError:
            print("redirects.json file not found. No redirects loaded.")


# Instantiate settings and load redirects
settings = Settings()
settings.load_redirects()
