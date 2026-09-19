from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import model  # noqa: F401  建表前先导入模型，保证元数据已注册
from app.config import settings
from app.database import Base, engine
from app.router import todo, user
from app.schema import ApiResponse

#建表用
@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix=settings.api_prefix)
app.include_router(todo.router, prefix=settings.api_prefix)


@app.get("/", tags=["System"], response_model=ApiResponse[dict[str, str]])
def root() -> ApiResponse[dict[str, str]]:
    return ApiResponse.ok(
        {
            "name": settings.app_name,
            "docs": "/docs",
            "api_prefix": settings.api_prefix,
        }
    )


@app.get("/health", tags=["System"], response_model=ApiResponse[dict[str, str]])
def health() -> ApiResponse[dict[str, str]]:
    return ApiResponse.ok({"status": "ok"})
