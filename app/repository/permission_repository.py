from sqlalchemy.future import select
from app.model.permission import Permission
from app.configuration.database import AsyncSessionLocal


class PermissionRepository:
    async def find_all(self) -> list:
        """Lấy tất cả các bản ghi Permission."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Permission))
            return result.scalars().all()

    async def find(self, id: int) -> Permission:
        """Tìm Permission theo ID."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Permission).where(Permission.id == id)
            )
            return result.scalar_one_or_none()

    async def find_one_by(self, filters: dict) -> Permission:
        """
        Tìm một Permission theo các tiêu chí được cung cấp trong dictionary filters.
        Ví dụ: filters = {"name": "view_users"}
        """
        async with AsyncSessionLocal() as session:
            query = select(Permission)
            for attr, value in filters.items():
                query = query.where(getattr(Permission, attr) == value)
            result = await session.execute(query)
            return result.scalar_one_or_none()
