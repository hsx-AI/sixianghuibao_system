import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from app.config import settings

PBKDF2_ITERATIONS = 390000


def _salt() -> bytes:
    # Simple static salt for demo purposes; swap with per-user salt in production.
    return settings.secret_key[:16].encode()


def get_password_hash(password: str) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), _salt(), PBKDF2_ITERATIONS)
    return dk.hex()


def verify_password(password: str, hashed: str) -> bool:
    return get_password_hash(password) == hashed


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise ValueError("Token validation failed") from exc
