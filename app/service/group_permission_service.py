# service/group_permission_service.py
from fastapi import HTTPException, status
from app.repository.group_permission_repository import GroupPermissionRepository
from app.model.group_permission import GroupPermission
from .group_service import GroupService
from .permission_service import PermissionService
# from app.exception import AppException  # Giả sử bạn có định nghĩa ngoại lệ riêng


class GroupPermissionService:
    def __init__(self):
        self.repository = GroupPermissionRepository()
        self.group_service = GroupService()
        self.permission_service = PermissionService()

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
        # if not group:
        #     raise AppException("E10110")  # Nhóm không tồn tại

        assigned_permissions = []
        group_permissions_to_add = []

        for permission_key, permission_data in data.get("permissions", {}).items():
            # Lấy đối tượng Permission thông qua service
            permission = await self.permission_service.get_permission_by_name(permission_key)
            if not permission:
                continue  # Bỏ qua nếu không tìm thấy quyền

            # Yêu cầu trường 'target' phải có trong dữ liệu
            # if "target" not in permission_data:
            #     raise AppException("E1004")  # Target không được cung cấp

            gp = GroupPermission()
            gp.group = group
            gp.permission = permission
            gp.is_active = permission_data.get("is_active", True)
            gp.is_denied = permission_data.get("is_denied", False)
            gp.target_id = None if permission_data["target"] == "all" else permission_data["target"]

            group_permissions_to_add.append(gp)
            assigned_permissions.append({
                "permission": permission_key,
                "status": "assigned"
            })

        await self.repository.bulk_insert(group_permissions_to_add)
        return assigned_permissions

    async def get_permissions_by_group(self, group) -> list:
        """
        Lấy danh sách tên quyền của Group.
        """
        permissions = await self.repository.find_by_group(group)
        return [gp.permission.name for gp in permissions]

    async def update_permission(self, data: dict) -> list:
        """
        Cập nhật thông tin quyền cho Group.
        Dữ liệu đầu vào bao gồm:
          - group_id: int
          - permissions: dict với key là permission name, value là dict chứa:
                'is_active', 'is_denied', 'target'
        """
        group = await self.group_service.get_group_by_id(data.get("group_id"))
        # if not group:
        #     raise AppException("E10110")  # Nhóm không tồn tại

        updated_permissions = []
        group_permissions_to_update = []

        for permission_key, permission_data in data.get("permissions", {}).items():
            permission = await self.permission_service.get_permission_by_name(permission_key)
            if not permission:
                continue  # Bỏ qua nếu không tìm thấy quyền

            gp = await self.repository.find_one_by_group_and_permission(group, permission)
            # if not gp:
            #     raise AppException("E2023")  # Quyền không tồn tại cho nhóm

            gp.is_active = permission_data.get("is_active", gp.is_active)
            gp.is_denied = permission_data.get("is_denied", gp.is_denied)
            # if "target" not in permission_data:
            #     raise AppException("E1004")
            gp.target_id = None if permission_data["target"] == "all" else permission_data["target"]

            group_permissions_to_update.append(gp)
            updated_permissions.append({
                "permission": permission_key,
                "status": "updated"
            })

        await self.repository.bulk_update(group_permissions_to_update)
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
        # if not group:
        #     raise AppException("E10110")  # Nhóm không tồn tại

        group_permissions_to_delete = []
        for permission_name in data.get("permissions", []):
            permission = await self.permission_service.get_permission_by_name(permission_name)
            if not permission:
                continue  # Bỏ qua nếu quyền không tồn tại

            gp = await self.repository.find_one_by_group_and_permission(group, permission)
            if gp:
                group_permissions_to_delete.append(gp)

        await self.repository.bulk_delete(group_permissions_to_delete)
