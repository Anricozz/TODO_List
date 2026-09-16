from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Todo
from app.schemas import TodoCreate, TodoRead, TodoUpdate

router = APIRouter(prefix="/todos", tags=["Todos"])


def get_todo(todo_id: int, db: Session) -> Todo:
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="待办事项不存在",
        )
    return todo


@router.get("", response_model=list[TodoRead])
def list_todos(
    completed: bool | None = Query(default=None),
    search: str | None = Query(default=None, max_length=100),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Todo]:
    statement = select(Todo)

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


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(
    payload: TodoCreate,
    db: Session = Depends(get_db),
) -> Todo:
    todo = Todo(
        title=payload.title.strip(),
        description=payload.description.strip() if payload.description else None,
        priority=payload.priority,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.get("/{todo_id}", response_model=TodoRead)
def read_todo(
    todo_id: int,
    db: Session = Depends(get_db),
) -> Todo:
    return get_todo(todo_id, db)


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: int,
    payload: TodoUpdate,
    db: Session = Depends(get_db),
) -> Todo:
    todo = get_todo(todo_id, db)
    updates = payload.model_dump(exclude_unset=True)

    if "title" in updates and updates["title"] is not None:
        updates["title"] = updates["title"].strip()
    if "description" in updates and updates["description"] is not None:
        updates["description"] = updates["description"].strip() or None

    for field, value in updates.items():
        setattr(todo, field, value)

    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
) -> Response:
    todo = get_todo(todo_id, db)
    db.delete(todo)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
