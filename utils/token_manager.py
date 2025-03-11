from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from config import settings

ALGORITHM = "HS256"


def create_jwt_token(data: dict) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(days=settings.TOKEN_EXPIRATION_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expiration})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_TOKEN, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt_token(encoded_jwt: str):
    try:
        decoded_jwt = jwt.decode(encoded_jwt, settings.SECRET_TOKEN, algorithms=[ALGORITHM])
        return decoded_jwt
    except JWTError:
        return
