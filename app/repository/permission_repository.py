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

    async def add(self, permission: Permission) -> Permission:
        """
        Thêm mới một Permission vào cơ sở dữ liệu.
        """
        async with AsyncSessionLocal() as session:
            session.add(permission)
            await session.commit()
            await session.refresh(permission)
        return permission

    async def update(self, permission: Permission) -> Permission:
        """
        Cập nhật một Permission đã có trong cơ sở dữ liệu.
        """
        async with AsyncSessionLocal() as session:
            session.add(permission)
            await session.commit()
            await session.refresh(permission)
        return permission

    async def delete(self, permission: Permission) -> None:
        """
        Xóa một Permission khỏi cơ sở dữ liệu.
        """
        async with AsyncSessionLocal() as session:
            await session.delete(permission)
            await session.commit()

    async def sync_permissions(self, static_permissions: dict) -> None:
        """
        Đồng bộ danh sách quyền giữa cơ sở dữ liệu và danh sách quyền tĩnh.
        Thêm các quyền mới và xóa các quyền không còn tồn tại trong static_permissions.
        """
        async with AsyncSessionLocal() as session:
            # Lấy danh sách quyền hiện có
            result = await session.execute(select(Permission))
            existing_permissions = result.scalars().all()
            existing_names = [perm.name for perm in existing_permissions]

            # Thêm các quyền mới chưa có trong DB
            for name, (description, default_granted) in static_permissions.items():
                if name not in existing_names:
                    new_permission = Permission()
                    new_permission.name = name
                    new_permission.description = description
                    new_permission.default = default_granted
                    session.add(new_permission)

            # Xóa các quyền trong DB mà không có trong static_permissions
            for perm in existing_permissions:
                if perm.name not in static_permissions:
                    await session.delete(perm)

            await session.commit()
