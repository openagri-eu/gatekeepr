# For helper functions (e.g., hashing, token generation).

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from app.config.settings import settings


def create_jwt_token(data: dict, token_type: str = "access") -> str:
    # Determine the expiration time based on token type
    if token_type == "access":
        expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    elif token_type == "refresh":
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    elif token_type == "auth":
        expires_delta = timedelta(minutes=settings.AUTH_TOKEN_EXPIRE_MINUTES)
    else:
        raise ValueError("Invalid token type specified.")

    # Create the token with the specified expiration time
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.JWT_SIGNING_KEY, algorithm="HS256")


def decode_jwt_token(token: str):
    try:
        return jwt.decode(token, settings.JWT_SIGNING_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
