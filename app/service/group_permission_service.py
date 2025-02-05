from fastapi import HTTPException, status
from app.repository.group_permission_repository import GroupPermissionRepository
from app.model.group_permission import GroupPermission
from app.configuration.database import AsyncSessionLocal
from app.exception import AppException  # Giả sử bạn có định nghĩa ngoại lệ riêng


class GroupPermissionService:
    def __init__(self, repository: GroupPermissionRepository, group_service, permission_service):
        self.repository = repository
        self.group_service = group_service
        self.permission_service = permission_service

    async def assign_permissions(self, data: dict) -> list:
        """
        Gán (assign) danh sách quyền cho Group.
        Dữ liệu đầu vào bao gồm:
            - group_id: int
            - permissions: dict với key là permission name, value là dict chứa:
                  'is_active' (mặc định True),
                  'is_denied' (mặc định False),
                  'target': nếu bằng "all" thì target_id = None, ngược lại target_id = giá trị target.
        """
        group = await self.group_service.get_group_by_id(data.get("group_id"))
        if not group:
            raise AppException("E10110")  # Nhóm không tồn tại

        assigned_permissions = []

        # Mở phiên làm việc để thêm các bản ghi mới
        async with AsyncSessionLocal() as session:
            # Duyệt từng quyền trong data
            for permission_key, permission_data in data.get("permissions", {}).items():
                permission = await self.permission_service.get_permission_by_name(permission_key)
                if not permission:
                    continue  # Bỏ qua nếu không tìm thấy quyền

                group_permission = GroupPermission()
                group_permission.group = group
                group_permission.permission = permission
                group_permission.is_active = permission_data.get("is_active", True)
                group_permission.is_denied = permission_data.get("is_denied", False)

                if "target" in permission_data:
                    if permission_data["target"] == "all":
                        group_permission.target_id = None
                    else:
                        group_permission.target_id = permission_data["target"]
                else:
                    raise AppException("E1004")  # Target không được cung cấp

                session.add(group_permission)
                assigned_permissions.append({
                    "permission": permission_key,
                    "status": "assigned"
                })

            await session.commit()

        return assigned_permissions

    async def get_permissions_by_group(self, group) -> list:
        """
        Lấy danh sách tên quyền của Group.
        """
        permissions = await self.repository.find_by_group(group)
        result = []
        for gp in permissions:
            # Giả sử rằng đối tượng Permission được load qua quan hệ và có thuộc tính name
            result.append(gp.permission.name)
        return result

    async def update_permission(self, data: dict) -> list:
        """
        Cập nhật thông tin quyền cho Group.
        Dữ liệu đầu vào bao gồm:
            - group_id: int
            - permissions: dict với key là permission name, value là dict chứa:
                  'is_active', 'is_denied', 'target'
        """
        group = await self.group_service.get_group_by_id(data.get("group_id"))
        if not group:
            raise AppException("E10110")  # Nhóm không tồn tại

        updated_permissions = []

        async with AsyncSessionLocal() as session:
            for permission_key, permission_data in data.get("permissions", {}).items():
                permission = await self.permission_service.get_permission_by_name(permission_key)
                if not permission:
                    continue  # Bỏ qua nếu quyền không tồn tại

                group_permission = await self.repository.find_one_by_group_and_permission(group, permission)
                if not group_permission:
                    raise AppException("E2023")  # Quyền không tồn tại cho nhóm

                # Cập nhật trạng thái
                group_permission.is_active = permission_data.get("is_active", group_permission.is_active)
                group_permission.is_denied = permission_data.get("is_denied", group_permission.is_denied)

                if "target" in permission_data:
                    if permission_data["target"] == "all":
                        group_permission.target_id = None
                    else:
                        group_permission.target_id = permission_data["target"]
                else:
                    raise AppException("E1004")

                session.add(group_permission)
                updated_permissions.append({
                    "permission": permission_key,
                    "status": "updated"
                })

            await session.commit()

        return updated_permissions

    async def has_permission(self, group_id: int, permission_name: str, target_id: int = None) -> int:
        """
        Kiểm tra quyền của Group.
        Trả về:
            1  : nếu có quyền (active và không bị deny)
           -1  : nếu quyền bị deny
            0  : nếu không tìm thấy quyền nào phù hợp
        """
        group_permissions = await self.repository.find_group_permission(group_id, permission_name)
        for gp in group_permissions:
            if not gp.is_active:
                continue

            if gp.target_id is None:
                return -1 if gp.is_denied else 1

            if gp.target_id == target_id:
                return -1 if gp.is_denied else 1

        return 0

    async def delete_permissions(self, data: dict) -> None:
        """
        Xóa danh sách quyền của Group.
        Dữ liệu đầu vào bao gồm:
            - group_id: int
            - permissions: list các permission name cần xóa.
        """
        group = await self.group_service.get_group_by_id(data.get("group_id"))
        if not group:
            raise AppException("E10110")  # Nhóm không tồn tại

        permissions_list = data.get("permissions", [])

        async with AsyncSessionLocal() as session:
            for permission_name in permissions_list:
                permission = await self.permission_service.get_permission_by_name(permission_name)
                if not permission:
                    continue  # Bỏ qua nếu quyền không tồn tại

                group_permission = await self.repository.find_one_by_group_and_permission(group, permission)
                if group_permission:
                    await session.delete(group_permission)

            await session.commit()
