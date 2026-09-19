"""密码加密（passlib）与 JWT（PyJWT）工具。"""

from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import jwt
from passlib.context import CryptContext

from app.config import settings

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

TokenType = Literal["access", "refresh"]

# 使用 pbkdf2_sha256：passlib 自带的纯 Python 实现，无需额外编译依赖
password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(raw_password: str) -> str:
    """把明文密码转成哈希值，数据库只保存哈希。"""
    return password_context.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    """校验明文密码与数据库中的哈希是否匹配。"""
    return password_context.verify(raw_password, hashed_password)


def _create_token(
    user_id: int,
    username: str,
    token_type: TokenType,
    expires_seconds: int,
) -> str:
    issued_at = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "username": username,
        "type": token_type,
        "iat": issued_at,
        "exp": issued_at + timedelta(seconds=expires_seconds),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: int, username: str) -> str:
    """签发 access token（默认 3 分钟）。"""
    return _create_token(
        user_id,
        username,
        ACCESS_TOKEN_TYPE,
        settings.access_token_expire_seconds,
    )


def create_refresh_token(user_id: int, username: str) -> str:
    """签发 refresh token（默认 6 分钟，不轮换、不续期）。"""
    return _create_token(
        user_id,
        username,
        REFRESH_TOKEN_TYPE,
        settings.refresh_token_expire_seconds,
    )


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    """校验签名、有效期与 token 类型；失败时抛出 jwt.InvalidTokenError 子类。"""
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("token type mismatch")
    return payload
