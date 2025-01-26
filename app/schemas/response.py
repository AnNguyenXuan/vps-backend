from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.enums.code import Code  # Đảm bảo enum Code được import từ vị trí enum của bạn

T = TypeVar('T')

class ApiResponse(Generic[T], BaseModel):
    code: int
    message: str
    result: Optional[T] = None

    @staticmethod
    def response(code: Code, result: Optional[T] = None) -> JSONResponse:
        response = ApiResponse(code=code.value, message=code.message, result=result)
        return JSONResponse(status_code=code.status_code.value, content=response.dict())
