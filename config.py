from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    BILLZ_TOKEN: str = None
    DATABASE_URL: str = None
    REDIS_URL: str = None
    SECRET_TOKEN: str = None
    DEBUG: bool = True
    TOKEN_EXPIRATION_DAYS: int = 15
    BILLZ_EXPIRE_DATA_MINUTES: int = 5
    OTP_DURING_MINUTE: int = 2
    c: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")