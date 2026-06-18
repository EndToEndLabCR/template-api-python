from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt

from src.app.config.app_config import AppConfig

app_config = AppConfig.instance()
SECRET_KEY = app_config.get_config("security.jwt.secret_key", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = app_config.get_config("security.jwt.access_token_expire_minutes", 60)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.

    Args:
        data: Payload to encode (e.g. {"sub": user_id}).
        expires_delta: Optional custom expiry duration.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT access token.

    Args:
        token: The encoded JWT string.

    Returns:
        Decoded payload dictionary.

    Raises:
        jwt.PyJWTError: If token is invalid or expired.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
