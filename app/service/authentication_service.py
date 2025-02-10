import os
from datetime import datetime, timedelta
import os
from jose import jwt, JWTError
from dotenv import load_dotenv
from .user_service import UserService
from .blacklist_token_service import BlacklistTokenService
from .refresh_token_service import RefreshTokenService
from app.core.config import SECRET_KEY, ALGORITHM, JWT_ISSUER, JWT_AUDIENCE

load_dotenv()

class AuthenticationService:
    def __init__(self):
        self.user_service = UserService()
        self.blacklist_token_service = BlacklistTokenService()
        self.refresh_token_service = RefreshTokenService()

        # Đọc issuer và audience từ .env (hoặc sử dụng giá trị mặc định)
        self.issuer = JWT_ISSUER
        self.audience = JWT_AUDIENCE

    async def create_token(self, user, token_type: str, refresh_token_id: str | None = None, reuse_count: int = 0) -> str:
        """
        Tạo token JWT.
        - token_type: "access" hoặc "refresh"
        - Với access token, refresh_token_id (ID của refresh token) là bắt buộc.
        - Với refresh token, thêm claim reuseCount.
        """
        now = datetime.utcnow()
        if token_type == "access":
            ttl = 3600  # 1 giờ
            if not refresh_token_id:
                raise ValueError("Refresh Token ID is required for access tokens.")
        elif token_type == "refresh":
            ttl = 5184000  # 2 tháng
        else:
            raise ValueError('Invalid token type. Allowed values are "access" and "refresh".')

        exp = now + timedelta(seconds=ttl)
        jti = os.urandom(32).hex()  # Tạo id duy nhất cho token

        payload = {
            "iss": self.issuer,
            "aud": self.audience,
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
        Nếu không hợp lệ, ném ngoại lệ.
        """
        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
                audience=self.audience,
                issuer=self.issuer,
            )
        except JWTError as e:
            raise Exception("Invalid or expired token") from e

        return payload

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
        stored_token = await self.refresh_token_service.get_token_by_id(jti)
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

    async def logout(self, access_token_string: str) -> None:
        """
        Đăng xuất: vô hiệu hóa Access Token và xóa Refresh Token.
        """
        payload = await self.validate_token(access_token_string)
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
