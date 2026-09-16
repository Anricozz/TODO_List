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

#格式辅助，可用于浏览器'同源规则'的处理
    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
