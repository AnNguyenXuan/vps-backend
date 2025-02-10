from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from contextvars import ContextVar
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# ContextVar lưu trữ user id (hoặc None nếu không có)
current_user_id: ContextVar[int | None] = ContextVar("current_user_id", default=None)

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header: str | None = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                # Nếu ở hệ thống PHP bạn dùng claim 'uid', thì thay "sub" bằng "uid"
                user_id = payload.get("sub") or payload.get("uid")
                if not user_id:
                    raise HTTPException(status_code=401, detail="Invalid token: missing user id")
                current_user_id.set(user_id)
            except JWTError:
                current_user_id.set(None)
                # Bạn có thể lựa chọn: raise HTTPException(status_code=401, detail="Invalid or expired token")
        else:
            current_user_id.set(None)

        response = await call_next(request)
        return response
