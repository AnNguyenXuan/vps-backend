from sqlalchemy.future import select
from sqlalchemy import asc
from app.model.user_permission import UserPermission
from app.configuration.database import AsyncSessionLocal


class UserPermissionRepository:
    async def find_user_permission(self, user_id: int, permission_name: str) -> list:
        """
        Lấy danh sách quyền theo user_id và permission_name,
        ưu tiên bản ghi target_id = None (sắp xếp theo target_id ASC).
        Giả sử mối quan hệ giữa UserPermission và Permission được định nghĩa qua thuộc tính `permission`,
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
