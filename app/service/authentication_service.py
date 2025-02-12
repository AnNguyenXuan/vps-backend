import os
from fastapi import HTTPException
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.model.user import User
from .user_service import UserService
from .blacklist_token_service import BlacklistTokenService
from .refresh_token_service import RefreshTokenService
from app.core.config import SECRET_KEY, ALGORITHM, JWT_ISSUER, JWT_AUDIENCE, ACCESS_TOKEN_EXPIRE, REFRESH_TOKEN_EXPIRE
from app.schema.auth_schema import (
    LoginRequest,
    TokenResponse,
    AccessTokenResponse,
    RefreshTokenResponse,
    ChangePasswordRequest,
    VerifyPasswordRequest,
    RefreshTokenRequest
)


class AuthenticationService:
    def __init__(self):
        self.user_service = UserService()
        self.blacklist_token_service = BlacklistTokenService()
        self.refresh_token_service = RefreshTokenService()

    async def create_token(self, user, token_type: str, refresh_token_id: str | None = None, reuse_count: int = 0) -> str:
        """
        Tạo token JWT.
        - token_type: "access" hoặc "refresh"
        - Với access token, refresh_token_id (ID của refresh token) là bắt buộc.
        - Với refresh token, thêm claim reuseCount.
        """
        now = datetime.utcnow()
        if token_type == "access":
            ttl = ACCESS_TOKEN_EXPIRE
            if not refresh_token_id:
                raise ValueError("Refresh Token ID is required for access tokens.")
        elif token_type == "refresh":
            ttl = REFRESH_TOKEN_EXPIRE
        else:
            raise ValueError('Invalid token type. Allowed values are "access" and "refresh".')

        exp = now + timedelta(seconds=ttl)
        jti = os.urandom(32).hex()  # Tạo id duy nhất cho token

        payload = {
            "iss": JWT_ISSUER,
            "aud": JWT_AUDIENCE,
            "iat": now,
            "exp": exp,
            "jti": jti,
            "uid": user.id,
            "username": user.username,
            "email": user.email,
            "isActive": user.is_active,
            "type": token_type,
        }
        if token_type == "access":
            payload["refreshId"] = refresh_token_id
        elif token_type == "refresh":
            payload["reuseCount"] = reuse_count

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        # Nếu tạo refresh token, lưu thông tin vào refresh_token_service
        if token_type == "refresh":
            # Giả sử refresh_token_service.create_token là một hàm async nhận (jti, expires_at)
            await self.refresh_token_service.create_token(jti, exp)

        return token

    async def validate_token(self, token: str) -> dict:
        """
        Xác thực JWT token và trả về payload nếu hợp lệ.
        Nếu không hợp lệ hoặc hết hạn, ném ngoại lệ.
        """
        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
                audience=JWT_AUDIENCE,
                issuer=JWT_ISSUER,
            )

            # Kiểm tra thời gian hết hạn của token
            exp_timestamp = payload.get("exp")
            if not exp_timestamp or datetime.utcfromtimestamp(exp_timestamp) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Token has expired")

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        return payload


    async def get_current_user(self, token: str) -> User:
        payload = await self.validate_token(token)
        if "jti" in payload:
            if await self.blacklist_token_service.is_token_blacklisted(payload["jti"]):
                raise HTTPException(status_code=401, detail="You have logged out.")
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
        if "uid" in payload:
            user_id = payload["uid"]
            return (await self.user_service.get_user_by_id(user_id), payload)
        else:
            raise HTTPException(status_code=401, detail="Invalid token")

    async def refresh_access_token(self, refresh_token_string: str) -> str:
        """
        Cấp lại Access Token từ Refresh Token.
        """
        payload = await self.validate_token(refresh_token_string)
        if payload.get("type") != "refresh":
            raise Exception("Invalid token type for access token refresh.")

        jti = payload.get("jti")
        user_id = payload.get("uid")

        # Kiểm tra Refresh Token trong DB
        stored_token = await self.refresh_token_service.get_token(jti)
        if not stored_token:
            raise Exception("Refresh token not found or invalid.")
        if stored_token.expires_at < datetime.utcnow():
            raise Exception("Refresh token has expired.")

        # Lấy thông tin người dùng
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            raise Exception("User not found.")

        # Tạo Access Token mới, sử dụng refresh token id từ refresh token hiện tại
        return await self.create_token(user, "access", refresh_token_id=jti)

    async def login(self, request: LoginRequest):
        "Đăng nhập cho người dùng."
        user = await self.user_service.verify_user_password(request.username, request.password)
        refresh_token = await self.create_token(user, "refresh")
        refresh_id = await self.extract_token_id(refresh_token)
        if not refresh_id:
            raise HTTPException(status_code=500, detail="Unable to extract Refresh Token ID")
        access_token = await self.create_token(user, "access", refresh_id)
        return access_token, refresh_token

    async def logout(self, payload: dict) -> None:
        """
        Đăng xuất: vô hiệu hóa Access Token và xóa Refresh Token.
        """
        jti = payload.get("jti")
        exp_timestamp = payload.get("exp")
        refresh_id = payload.get("refreshId")
        if not refresh_id:
            raise Exception("Refresh Token ID is missing in the Access Token.")

        expires_at = datetime.utcfromtimestamp(exp_timestamp)
        await self.blacklist_token_service.add_token(jti, expires_at)
        await self.refresh_token_service.delete_token(refresh_id)

    async def extract_token_id(self, token_string: str) -> str | None:
        """
        Trích xuất token id (jti) từ token.
        """
        try:
            payload = await self.validate_token(token_string)
            return payload.get("jti")
        except Exception:
            return None

    async def refresh_refresh_token(self, refresh_token_string: str) -> str:
        """
        Tạo Refresh Token mới dựa trên Refresh Token cũ với reuseCount tăng thêm 1.
        """
        payload = await self.validate_token(refresh_token_string)
        if payload.get("type") != "refresh":
            raise Exception("Invalid token type for refresh.")

        jti = payload.get("jti")
        reuse_count = payload.get("reuseCount", 0)
        user_id = payload.get("uid")

        # Kiểm tra tính hợp lệ của refresh token trong DB
        stored_token = await self.refresh_token_service.get_token_by_id(jti)
        if not stored_token or reuse_count > 12:
            raise Exception("Invalid or overused Refresh Token.")
        if stored_token.expires_at < datetime.utcnow():
            raise Exception("Refresh Token has expired.")

        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            raise Exception("User not found.")

        # Tạo refresh token mới với reuseCount tăng thêm 1
        return await self.create_token(user, "refresh", reuse_count=reuse_count + 1)
