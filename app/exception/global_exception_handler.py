from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.enums.code import Code
from app.schemas.response import ApiResponse
from app.exceptions.app_exception import AppException
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import status
import logging

# Khởi tạo logger
logger = logging.getLogger(__name__)

# Hàm xử lý cho AppException
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.code.status_code,  # Sử dụng status code từ enum Code
        content=ApiResponse(code=exc.code.code, message=exc.code.message, result=None).dict()
    )

# Hàm xử lý cho AccessDeniedException
async def access_denied_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=Code.ACCESS_DENIED.status_code,
        content=ApiResponse(code=Code.ACCESS_DENIED.code, message=Code.ACCESS_DENIED.message, result=None).dict()
    )

# Hàm xử lý cho RuntimeException
async def runtime_exception_handler(request: Request, exc: RuntimeError):
    logger.error(f"Runtime exception: {str(exc)}")
    return JSONResponse(
        status_code=Code.RUNTIME_EXCEPTION.status_code,
        content=ApiResponse(code=Code.RUNTIME_EXCEPTION.code, message=str(exc), result=None).dict()
    )

# Hàm xử lý cho Exception chung
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=Code.INTERNAL_SERVER_ERROR.status_code,
        content=ApiResponse(code=Code.INTERNAL_SERVER_ERROR.code, message=str(exc), result=None).dict()
    )

# Đăng ký các exception handlers trong ứng dụng FastAPI
def register_exception_handlers(app):
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, access_denied_exception_handler)
    app.add_exception_handler(RuntimeError, runtime_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
