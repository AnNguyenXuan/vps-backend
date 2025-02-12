from sqlalchemy.future import select
from app.model.blacklist_token import BlacklistToken
from app.core.database import AsyncSessionLocal
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


class BlacklistTokenRepository:

    async def add_token(self, token: BlacklistToken):
        """ Thêm token vào danh sách blacklist """
        async with AsyncSessionLocal() as session:
            session.add(token)
            await session.commit()
            await session.refresh(token)
            return token

    async def is_token_blacklisted(self, token_id: str) -> bool:
        """ Kiểm tra token có trong blacklist """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(BlacklistToken).where(BlacklistToken.id == token_id)
            )
            token = result.scalar_one_or_none()
            return token is not None

    async def delete_token(self, token_id: str):
        """ Xóa token khỏi blacklist """
        async with AsyncSessionLocal() as session:
            token = await session.get(BlacklistToken, token_id)
            if token:
                await session.delete(token)
                await session.commit()

    async def delete_expired_tokens(self):
        """ Xóa tất cả token đã hết hạn """
        async with AsyncSessionLocal() as session:
            try:
                await session.execute(
                    f"DELETE FROM blacklist_tokens WHERE expires_at < '{datetime.utcnow().isoformat()}'"
                )
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
