"""user 的数据库操作。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.model import User


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def create_user(db: Session, username: str, password: str) -> User:
    """新建用户，明文密码在这里被 passlib 加密后入库。"""
    user = User(username=username, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
