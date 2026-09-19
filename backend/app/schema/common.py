"""通用响应封装：所有接口成功时统一返回 code / message / data。"""

from typing import Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")

SUCCESS_CODE = 0


class ApiResponse(BaseModel, Generic[DataT]):
    code: int = SUCCESS_CODE
    message: str = "success"
    data: DataT | None = None

    @classmethod
    def ok(cls, data: DataT | None = None, message: str = "success") -> "ApiResponse[DataT]":
        return cls(code=SUCCESS_CODE, message=message, data=data)
