from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar
from app.model.user import User
from app.service.authentication_service import AuthenticationService


authentication = AuthenticationService()

# ContextVar lưu trữ user (hoặc None nếu không có)
current_user: ContextVar[User | None] = ContextVar("current_user", default=None)

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header: str | None = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            user = await authentication.get_current_user(token)
            current_user.set(user)
        else:
            current_user.set(None)

        response = await call_next(request)
        return response
