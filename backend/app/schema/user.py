"""user 的请求体与响应体（注册、登入、token）。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserCredentials(BaseModel):
    """注册与登入共用的请求体。"""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("username")
    @classmethod
    def username_must_not_be_blank(cls, value: str) -> str:
        username = value.strip()
        if len(username) < 3:
            raise ValueError("用户名长度需为 3-50 个字符")
        return username


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime


class TokenPair(BaseModel):
    """注册 / 登入成功后返回的 access token 与 refresh token。"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int
    user: UserRead


class AccessTokenOut(BaseModel):
    """用 refresh token 换到的新 access token。"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)
