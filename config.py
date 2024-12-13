from dotenv import load_dotenv, dotenv_values
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path

load_dotenv()
config = dotenv_values('.env')

DB_HOST = config.get("DB_HOST")
DB_PORT = config.get("DB_PORT")
DB_USER = config.get("DB_USER")
DB_PASS = config.get("DB_PASS")
DB_NAME = config.get("DB_NAME")
MODE = config.get("MODE")


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
    db_url: str = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    db_echo: bool = False

db_settings = DBSettings()