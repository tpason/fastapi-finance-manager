from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from datetime import datetime, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    return _create_token(data, expires_delta, token_type="access")


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token"""
    return _create_token(data, expires_delta, token_type="refresh")


def _create_token(data: dict, expires_delta: Optional[timedelta], token_type: str) -> str:
    """Create a typed JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire_minutes = (
            settings.ACCESS_TOKEN_EXPIRE_MINUTES
            if token_type == "access"
            else settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    
    to_encode.update({"exp": expire, "type": token_type})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token"""
    return _decode_token(token, expected_type="access")


def decode_refresh_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT refresh token"""
    return _decode_token(token, expected_type="refresh")


def _decode_token(token: str, expected_type: str) -> Optional[dict]:
    """Decode and verify a JWT token of a specific type"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != expected_type:
            return None
        return payload
    except JWTError:
        return None


def is_expired(expired_at_ts: int) -> bool:
    now_ts = int(datetime.now(timezone.utc).timestamp())
    return expired_at_ts <= now_ts
