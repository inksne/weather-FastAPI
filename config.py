from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path
import os

load_dotenv()

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")


class AuthJWT(BaseModel):
    private_key_path: Path = Path("certs") / "jwt-private.pem"
    public_key_path: Path = Path("certs") / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 5
    refresh_token_expire_days: int = 30


class Settings(BaseSettings):
    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()

class DBSettings(BaseSettings):
    db_url: str = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DB}'
    db_echo: bool = False

db_settings = DBSettings()