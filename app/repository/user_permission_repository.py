from sqlalchemy.future import select
from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError
from app.model.user_permission import UserPermission
from app.core.database import AsyncSessionLocal


class UserPermissionRepository:
    async def find_user_permission(self, user_id: int, permission_name: str) -> list:
        """
        Lấy danh sách UserPermission theo user_id và permission_name,
        ưu tiên bản ghi có target_id = None (sắp xếp theo target_id ASC).
        Giả sử mối quan hệ giữa UserPermission và Permission được định nghĩa qua thuộc tính `permission`
        và Permission có trường `name`.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserPermission)
                .join(UserPermission.permission)
                .where(UserPermission.user_id == user_id)
                .where(UserPermission.permission.has(name=permission_name))
                .order_by(asc(UserPermission.target_id))
            )
            return result.scalars().all()

    async def add(self, user_permission: UserPermission) -> UserPermission:
        """
        Thêm một bản ghi UserPermission.
        """
        async with AsyncSessionLocal() as session:
            session.add(user_permission)
            await session.commit()
            await session.refresh(user_permission)
        return user_permission

    async def bulk_insert(self, user_permissions: list) -> None:
        """
        Thêm nhiều bản ghi UserPermission cùng lúc.
        """
        async with AsyncSessionLocal() as session:
            try:
                session.add_all(user_permissions)
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                raise

    async def find_by_user_id(self, user_id: int) -> list:
        """
        Lấy danh sách UserPermission theo user_id.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserPermission).where(UserPermission.user_id == user_id)
            )
            return result.scalars().all()

    async def find_one_by_user_and_permission(self, user_id: int, permission_id: int) -> UserPermission:
        """
        Tìm một bản ghi UserPermission dựa vào user_id và permission_id.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserPermission).where(
                    UserPermission.user_id == user_id,
                    UserPermission.permission_id == permission_id
                )
            )
            return result.scalar_one_or_none()

    async def update(self, user_permission: UserPermission) -> UserPermission:
        """
        Cập nhật một bản ghi UserPermission.
        """
        async with AsyncSessionLocal() as session:
            try:
                session.add(user_permission)
                await session.commit()
                await session.refresh(user_permission)
            except SQLAlchemyError:
                await session.rollback()
                raise
        return user_permission

    async def delete(self, user_permission: UserPermission) -> None:
        """
        Xóa một bản ghi UserPermission.
        """
        async with AsyncSessionLocal() as session:
            try:
                await session.delete(user_permission)
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                raise

    async def bulk_delete(self, user_permissions: list) -> None:
        """
        Xóa nhiều bản ghi UserPermission cùng lúc.
        """
        async with AsyncSessionLocal() as session:
            try:
                for up in user_permissions:
                    await session.delete(up)
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                raise
