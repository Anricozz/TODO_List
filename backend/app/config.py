#本项目采用pydantic_settings库来读取.env，而非load_dotenv。
#.env存储了MYSQL连接信息，其余还存有全局参数
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

#以下为默认值，若本地无.env文件则套用以下值作为环境变量

    # 敏感字段：必填，漏配就启动失败
    database_url: str

    # 非敏感字段：
    app_name: str = "FocusList API"
    api_prefix: str = "/api/v1"
    cors_origins: str = (
        "http://127.0.0.1:5500,http://localhost:5500,"
        "http://127.0.0.1:8000,http://localhost:8000"
    )

    # JWT 相关配置：access token 3 分钟、refresh token 6 分钟（固定，不续期）
    # jwt_secret 只是本地开发默认值，部署时必须用 .env 覆盖
    jwt_secret: str = "focuslist-dev-only-secret-please-change-me-in-env-file"
    jwt_algorithm: str = "HS256"
    access_token_expire_seconds: int = 180
    refresh_token_expire_seconds: int = 360

#格式辅助，可用于浏览器'同源规则'的处理
    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
