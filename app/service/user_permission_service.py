from fastapi import HTTPException, status
from app.repository.user_permission_repository import UserPermissionRepository
from app.model.user_permission import UserPermission
from app.configuration.database import AsyncSessionLocal
from app.exception import AppException  # Giả sử bạn có định nghĩa ngoại lệ riêng


class UserPermissionService:
    def __init__(self, repository: UserPermissionRepository, entity_manager, user_service, permission_service):
        self.repository = repository
        self.entity_manager = entity_manager  # Có thể là AsyncSessionLocal hoặc một đối tượng quản lý session riêng
        self.user_service = user_service
        self.permission_service = permission_service

    async def assign_permissions(self, data: dict) -> list:
        """
        Gán (assign) quyền cho người dùng.
        Dữ liệu đầu vào bao gồm:
          - user_id: int
          - permissions: dict, với key là permission name,
            value là dict chứa:
              'is_active' (mặc định True),
              'is_denied' (mặc định False),
              'target': nếu bằng "all" thì target_id = None, ngược lại target_id = giá trị target.
        """
        user = await self.user_service.get_user_by_id(data.get("user_id"))
        if not user:
            raise AppException("E1004")  # Người dùng không tồn tại

        assigned_permissions = []

        async with AsyncSessionLocal() as session:
            for permission_key, permission_data in data.get("permissions", {}).items():
                permission = await self.permission_service.get_permission_by_name(permission_key)
                if not permission:
                    continue  # Bỏ qua nếu không tìm thấy quyền

                user_permission = UserPermission()
                user_permission.user = user
                user_permission.permission = permission
                user_permission.is_active = permission_data.get("is_active", True)
                user_permission.is_denied = permission_data.get("is_denied", False)
                if "target" in permission_data:
                    if permission_data["target"] == "all":
                        user_permission.target_id = None
                    else:
                        user_permission.target_id = permission_data["target"]
                else:
                    raise AppException("E1004")
                session.add(user_permission)
                assigned_permissions.append({
                    "permission": permission_key,
                    "status": "assigned"
                })

            await session.commit()

        return assigned_permissions

    async def set_permission(self, user, permissions: list) -> list:
        """
        Khởi tạo quyền cho người dùng (ví dụ: cho superadmin).
        Tham số permissions là danh sách các đối tượng Permission.
        """
        user_permissions = []

        async with AsyncSessionLocal() as session:
            for permission in permissions:
                # Kiểm tra đối tượng permission phải là instance của Permission
                if not hasattr(permission, "id"):
                    raise ValueError("Each item in permissions array must be an instance of Permission.")

                user_permission = UserPermission()
                user_permission.user = user
                user_permission.permission = permission
                user_permission.is_active = True
                user_permission.is_denied = False
                user_permission.target_id = None

                session.add(user_permission)
                user_permissions.append(user_permission)

            await session.commit()

        return user_permissions

    async def find_permissions_by_user(self, user) -> list:
        """
        Lấy danh sách các quyền (UserPermission) của người dùng.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserPermission).where(UserPermission.user_id == user.id)
            )
            return result.scalars().all()

    async def get_permissions_by_user(self, user) -> list:
        """
        Lấy danh sách tên quyền của người dùng.
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserPermission).where(UserPermission.user_id == user.id)
            )
            permissions = result.scalars().all()
        result_list = [up.permission.name for up in permissions]
        return result_list

    async def update_permission(self, data: dict) -> list:
        """
        Cập nhật quyền của người dùng.
        Dữ liệu đầu vào bao gồm:
          - user_id: int
          - permissions: dict với key là permission name,
            value là dict chứa:
              'is_active', 'is_denied', 'target'
        """
        user = await self.user_service.get_user_by_id(data.get("user_id"))
        if not user:
            raise AppException("E1004")  # Người dùng không tồn tại

        updated_permissions = []

        async with AsyncSessionLocal() as session:
            for permission_key, permission_data in data.get("permissions", {}).items():
                permission = await self.permission_service.get_permission_by_name(permission_key)
                if not permission:
                    continue  # Nếu quyền không tồn tại, bỏ qua

                # Tìm bản ghi UserPermission hiện tại
                result = await session.execute(
                    select(UserPermission).where(
                        UserPermission.user_id == user.id,
                        UserPermission.permission_id == permission.id
                    )
                )
                user_permission = result.scalar_one_or_none()
                if not user_permission:
                    raise AppException("E2023")  # Quyền không tồn tại cho người dùng

                user_permission.is_active = permission_data.get("is_active", user_permission.is_active)
                user_permission.is_denied = permission_data.get("is_denied", user_permission.is_denied)
                if "target" in permission_data:
                    if permission_data["target"] == "all":
                        user_permission.target_id = None
                    else:
                        user_permission.target_id = permission_data["target"]
                else:
                    raise AppException("E1004")
                session.add(user_permission)
                updated_permissions.append({
                    "permission": permission_key,
                    "status": "updated"
                })

            await session.commit()

        return updated_permissions

    async def has_permission(self, user_id: int, permission_name: str, target_id: int = None) -> int:
        """
        Kiểm tra quyền của người dùng.
        Trả về:
          1  : nếu có quyền (active và không bị deny)
         -1  : nếu quyền bị deny
          0  : nếu không tìm thấy quyền nào phù hợp
        """
        user_permissions = await self.repository.find_user_permission(user_id, permission_name)
        for up in user_permissions:
            if not up.is_active:
                continue
            if up.target_id is None:
                return -1 if up.is_denied else 1
            if up.target_id == target_id:
                return -1 if up.is_denied else 1
        return 0

    async def delete_permissions(self, data: dict) -> None:
        """
        Xóa quyền của người dùng.
        Dữ liệu đầu vào bao gồm:
          - user_id: int
          - permissions: list các permission name cần xóa.
        """
        user = await self.user_service.get_user_by_id(data.get("user_id"))
        if not user:
            raise AppException("E1004")  # Người dùng không tồn tại

        async with AsyncSessionLocal() as session:
            for permission_name in data.get("permissions", []):
                permission = await self.permission_service.get_permission_by_name(permission_name)
                if not permission:
                    continue  # Bỏ qua nếu quyền không tồn tại

                result = await session.execute(
                    select(UserPermission).where(
                        UserPermission.user_id == user.id,
                        UserPermission.permission_id == permission.id
                    )
                )
                user_permission = result.scalar_one_or_none()
                if user_permission:
                    await session.delete(user_permission)
            await session.commit()
