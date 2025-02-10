from app.repository.blacklist_token_repository import BlacklistTokenRepository
from app.model.blacklist_token import BlacklistToken
from datetime import datetime


class BlacklistTokenService:

    def __init__(self):
        self.repository = BlacklistTokenRepository()

    async def add_token(self, token_id: str, expires_at: datetime):
        """ Thêm token vào danh sách blacklist """
        token = BlacklistToken(id=token_id, expires_at=expires_at)
        return await self.repository.add_token(token)

    async def is_token_blacklisted(self, token_id: str) -> bool:
        """ Kiểm tra token có trong blacklist không """
        return await self.repository.is_token_blacklisted(token_id)

    async def delete_token(self, token_id: str):
        """ Xóa token khỏi danh sách blacklist """
        await self.repository.delete_token(token_id)

    async def delete_expired_tokens(self):
        """ Xóa tất cả token đã hết hạn """
        await self.repository.delete_expired_tokens()
