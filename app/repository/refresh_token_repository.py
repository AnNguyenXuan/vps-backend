from sqlalchemy.future import select
from app.model.refresh_token import RefreshToken
from app.core.database import AsyncSessionLocal
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


class RefreshTokenRepository:

    async def create_token(self, token: RefreshToken):
        """ Thêm refresh token vào cơ sở dữ liệu """
        async with AsyncSessionLocal() as session:
            session.add(token)
            await session.commit()
            await session.refresh(token)
            return token

    async def get_token(self, token_id: str):
        """ Lấy refresh token theo ID """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(RefreshToken).where(RefreshToken.id == token_id)
            )
            return result.scalar_one_or_none()

    async def delete_token(self, token_id: str):
        """ Xóa refresh token khỏi database """
        async with AsyncSessionLocal() as session:
            token = await session.get(RefreshToken, token_id)
            if token:
                await session.delete(token)
                await session.commit()

    async def delete_expired_tokens(self):
        """ Xóa tất cả các refresh token đã hết hạn """
        async with AsyncSessionLocal() as session:
            try:
                await session.execute(
                    f"DELETE FROM refresh_tokens WHERE expires_at < '{datetime.utcnow().isoformat()}'"
                )
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
