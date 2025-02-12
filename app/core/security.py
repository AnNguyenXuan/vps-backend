from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar
from app.model.user import User
from app.service.authentication_service import AuthenticationService
from app.service.authorization_service import AuthorizationService


authentication = AuthenticationService()
authorization = AuthorizationService()

user_context: ContextVar[User | None] = ContextVar("user_context", default=None)
payload_context: ContextVar[str | None] = ContextVar("payload_context", default=None)

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header: str | None = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try: 
                user, payload = await authentication.get_current_user(token)
                user_context.set(user)
                payload_context.set(payload)
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.detail},
                )
        else:
            user_context.set(None)
            payload_context.set(None)

        response = await call_next(request)
        return response
