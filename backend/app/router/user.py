"""user 路由：注册、登入、刷新 access token、获取当前用户。"""

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import CurrentUser
from app.core.security import (
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.crud import user as user_crud
from app.database import get_db
from app.model import User
from app.schema import (
    AccessTokenOut,
    ApiResponse,
    RefreshTokenRequest,
    TokenPair,
    UserCredentials,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _build_token_pair(user: User) -> TokenPair:
    """同时签发 access token（3 分钟）与 refresh token（6 分钟）。"""
    return TokenPair(
        access_token=create_access_token(user.id, user.username),
        refresh_token=create_refresh_token(user.id, user.username),
        expires_in=settings.access_token_expire_seconds,
        refresh_expires_in=settings.refresh_token_expire_seconds,
        user=UserRead.model_validate(user),
    )


@router.post(
    "/register",
    response_model=ApiResponse[TokenPair],
    status_code=status.HTTP_201_CREATED,
    summary="注册并登入",
)
def register(
    payload: UserCredentials,
    db: Session = Depends(get_db),
) -> ApiResponse[TokenPair]:
    if user_crud.get_user_by_username(db, payload.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已存在",
        )

    try:
        user = user_crud.create_user(
            db,
            username=payload.username,
            password=payload.password,
        )
    except IntegrityError:
        # 并发注册同名用户时由唯一索引兜底；其他完整性错误照常抛出
        db.rollback()
        if user_crud.get_user_by_username(db, payload.username) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="用户名已存在",
            ) from None
        raise

    return ApiResponse.ok(_build_token_pair(user), message="注册成功")


@router.post("/login", response_model=ApiResponse[TokenPair], summary="登入")
def login(
    payload: UserCredentials,
    db: Session = Depends(get_db),
) -> ApiResponse[TokenPair]:
    user = user_crud.get_user_by_username(db, payload.username)
    if user is None or not verify_password(payload.password, user.hashed_password):
        # 不区分“用户不存在”与“密码错误”，避免泄露账号是否存在
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return ApiResponse.ok(_build_token_pair(user), message="登入成功")


@router.post("/refresh", response_model=ApiResponse[AccessTokenOut], summary="刷新 access token")
def refresh_access_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[AccessTokenOut]:
    try:
        token_payload = decode_token(payload.refresh_token, REFRESH_TOKEN_TYPE)
        user_id = int(token_payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user = user_crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # refresh token 本身不轮换、不延长有效期
    return ApiResponse.ok(
        AccessTokenOut(
            access_token=create_access_token(user.id, user.username),
            expires_in=settings.access_token_expire_seconds,
        ),
        message="已刷新登录状态",
    )


@router.get("/me", response_model=ApiResponse[UserRead], summary="获取当前登录用户")
def read_current_user(current_user: CurrentUser) -> ApiResponse[UserRead]:
    return ApiResponse.ok(UserRead.model_validate(current_user))
