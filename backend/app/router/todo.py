"""TODO 路由：全部接口都需要登录，且只能读写自己的待办。"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.crud import todo as todo_crud
from app.database import get_db
from app.model import Todo
from app.schema import ApiResponse, TodoCreate, TodoRead, TodoUpdate

router = APIRouter(prefix="/todos", tags=["Todos"])


def _get_owned_todo(db: Session, user_id: int, todo_id: int) -> Todo:
    todo = todo_crud.get_todo(db, user_id, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="待办事项不存在",
        )
    return todo


@router.get("", response_model=ApiResponse[list[TodoRead]], summary="获取任务列表")
def list_todos(
    current_user: CurrentUser,
    completed: bool | None = Query(default=None),
    search: str | None = Query(default=None, max_length=100),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
) -> ApiResponse[list[TodoRead]]:
    todos = todo_crud.list_todos(
        db,
        current_user.id,
        completed=completed,
        search=search,
        skip=skip,
        limit=limit,
    )
    return ApiResponse.ok([TodoRead.model_validate(todo) for todo in todos])


@router.post(
    "",
    response_model=ApiResponse[TodoRead],
    status_code=status.HTTP_201_CREATED,
    summary="新建任务",
)
def create_todo(
    payload: TodoCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> ApiResponse[TodoRead]:
    description = payload.description.strip() if payload.description else None
    todo = todo_crud.create_todo(
        db,
        current_user.id,
        title=payload.title.strip(),
        description=description or None,
        priority=payload.priority,
    )
    return ApiResponse.ok(TodoRead.model_validate(todo), message="任务已创建")


@router.get("/{todo_id}", response_model=ApiResponse[TodoRead], summary="获取单个任务")
def read_todo(
    todo_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> ApiResponse[TodoRead]:
    todo = _get_owned_todo(db, current_user.id, todo_id)
    return ApiResponse.ok(TodoRead.model_validate(todo))


@router.patch("/{todo_id}", response_model=ApiResponse[TodoRead], summary="修改任务")
def update_todo(
    todo_id: int,
    payload: TodoUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> ApiResponse[TodoRead]:
    todo = _get_owned_todo(db, current_user.id, todo_id)
    updates = payload.model_dump(exclude_unset=True)

    if "title" in updates and updates["title"] is not None:
        updates["title"] = updates["title"].strip()
    if "description" in updates and updates["description"] is not None:
        updates["description"] = updates["description"].strip() or None

    todo = todo_crud.update_todo(db, todo, updates)
    return ApiResponse.ok(TodoRead.model_validate(todo), message="任务已更新")


@router.delete("/{todo_id}", response_model=ApiResponse[None], summary="删除任务")
def delete_todo(
    todo_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> ApiResponse[None]:
    todo = _get_owned_todo(db, current_user.id, todo_id)
    todo_crud.delete_todo(db, todo)
    return ApiResponse.ok(None, message="任务已删除")
