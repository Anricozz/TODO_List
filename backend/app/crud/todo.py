"""TODO 的数据库操作，全部按 user_id 隔离。"""

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.model import Todo


def list_todos(
    db: Session,
    user_id: int,
    *,
    completed: bool | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 200,
) -> list[Todo]:
    statement = select(Todo).where(Todo.user_id == user_id)

    if completed is not None:
        statement = statement.where(Todo.completed == completed)

    if search:
        keyword = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Todo.title.ilike(keyword),
                Todo.description.ilike(keyword),
            )
        )

    statement = (
        statement.order_by(Todo.completed.asc(), Todo.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_todo(db: Session, user_id: int, todo_id: int) -> Todo | None:
    """只返回属于该用户的待办，别人的记录等同于不存在。"""
    return db.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
    )


def create_todo(
    db: Session,
    user_id: int,
    *,
    title: str,
    description: str | None,
    priority: str,
) -> Todo:
    todo = Todo(
        user_id=user_id,
        title=title,
        description=description,
        priority=priority,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def update_todo(db: Session, todo: Todo, updates: dict[str, Any]) -> Todo:
    for field, value in updates.items():
        setattr(todo, field, value)

    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(db: Session, todo: Todo) -> None:
    db.delete(todo)
    db.commit()
