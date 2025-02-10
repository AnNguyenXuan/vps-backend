from app.repository.refresh_token_repository import RefreshTokenRepository
from app.model.refresh_token import RefreshToken
from datetime import datetime


class RefreshTokenService:

    def __init__(self):
        self.repository = RefreshTokenRepository()

    async def create_token(self, token_id: str, expires_at: datetime):
        """ Tạo mới một refresh token """
        token = RefreshToken(id=token_id, expires_at=expires_at)
        return await self.repository.create_token(token)

    async def get_token(self, token_id: str):
        """ Lấy refresh token theo ID """
        return await self.repository.get_token(token_id)

    async def delete_token(self, token_id: str):
        """ Xóa refresh token """
        await self.repository.delete_token(token_id)

    async def delete_expired_tokens(self):
        """ Xóa tất cả các refresh token đã hết hạn """
        await self.repository.delete_expired_tokens()
