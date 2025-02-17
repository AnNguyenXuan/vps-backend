from fastapi import HTTPException, status
from app.repository.group_permission_repository import GroupPermissionRepository
from app.model.group_permission import GroupPermission
from app.model.group import Group
from app.model.permission import Permission
from .group_service import GroupService
from .permission_service import PermissionService
from app.schema.group_permission_schema import (
    GroupPermissionsAssign,
    GroupPermissionsUpdate,
    GroupPermissionsRead,
    GroupPermissionsReadDetail,
    GroupPermissionsDelete
)



class GroupPermissionService:
    def __init__(self):
        self.repository = GroupPermissionRepository()
        self.group_service = GroupService()
        self.permission_service = PermissionService()

    async def assign_permissions(self, data: GroupPermissionsAssign) -> list:
        """
        Gán (assign) quyền cho group.
        """
        group = await self.group_service.get_group_by_id(data.group_id)

        assigned_permissions = []
        group_permissions_to_add = []

        for permission_data in data.permissions:
            permission = await self.permission_service.get_permission_by_id(permission_data.permission_id)
            group_permission = GroupPermission(
                group_id=group.id,
                permission_id=permission.id,
                record_enabled=False,
                is_denied=False
            )
            group_permission.target_id = None if permission_data.target == "all" else permission_data.target

            group_permissions_to_add.append(group_permission)
            assigned_permissions.append({
                "permission": permission.name,
                "target": permission_data.target,
                "status": "assigned"
            })

        await self.repository.bulk_insert(group_permissions_to_add)
        return assigned_permissions

    async def set_permission(self, group: Group, permissions: list[Permission]) -> list:
        """
        Khởi tạo quyền cho group.
        """
        group_permissions = []
        group_permissions_to_add = []
        for permission in permissions:
            if not hasattr(permission, "id"):
                raise ValueError("Each item in permissions array must be an instance of Permission.")

            group_permission = GroupPermission()
            group_permission.group_id = group.id
            group_permission.permission_id = permission.id
            group_permission.record_enabled = True
            group_permission.is_denied = False
            group_permission.target_id = None

            group_permissions_to_add.append(group_permission)
            group_permissions.append(group_permission)

        await self.repository.bulk_insert(group_permissions_to_add)
        return group_permissions

    async def find_permissions_by_group(self, group: Group) -> list[GroupPermission]:
        """
        Lấy danh sách quyền của group.
        """
        return await self.repository.find_by_group_id(group.id)

    async def get_permissions_by_group(self, group: Group) -> GroupPermissionsRead:
        """
        Lấy danh sách quyền của group và chuyển đổi thành schema GroupPermissionsRead.
        """
        group_permissions = await self.repository.find_by_group_id(group.id)
        details = []
        for gp in group_permissions:
            permission = await self.permission_service.get_permission_by_id(gp.permission_id)
            detail = GroupPermissionsReadDetail(
                id=gp.id,
                permission_id=gp.permission_id,
                name=permission.name,
                record_enabled=gp.record_enabled,
                is_denied=gp.is_denied,
                target=gp.target_id if gp.target_id is not None else "all"
            )
            details.append(detail)
        return GroupPermissionsRead(group_id=group.id, permissions=details)

    async def update_permission(self, data: GroupPermissionsUpdate) -> list:
        """
        Cập nhật quyền của group.
        """
        group = await self.group_service.get_group_by_id(data.group_id)
        existing_group_permissions = await self.repository.find_by_group_id(group.id)

        group_permission_map = {gp.id: gp for gp in existing_group_permissions}
        updated_permissions = []

        for permission_data in data.permissions:
            if permission_data.id not in group_permission_map:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"GroupPermission với id '{permission_data.id}' không được gán cho group"
                )
            group_permission = group_permission_map[permission_data.id]

            if permission_data.record_enabled is not None:
                group_permission.record_enabled = permission_data.record_enabled
            if permission_data.is_denied is not None:
                group_permission.is_denied = permission_data.is_denied

            updated_permissions.append(group_permission)

        await self.repository.bulk_update(updated_permissions)
        return [{"permission_id": gp.permission_id, "status": "updated"} for gp in updated_permissions]

    async def delete_permissions(self, data: GroupPermissionsDelete) -> None:
        """
        Xóa quyền của group.
        """
        group = await self.group_service.get_group_by_id(data.group_id)

        group_permissions = await self.repository.find_by_group_id(group.id)
        assigned_permission_ids = {gp.permission_id for gp in group_permissions}
        requested_permission_ids = set(data.permissions)
        missing_permissions = requested_permission_ids - assigned_permission_ids

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group không có các quyền với permission_id: {', '.join(map(str, missing_permissions))}"
            )

        group_permissions_to_delete = [gp for gp in group_permissions if gp.permission_id in requested_permission_ids]

        failed_deletes = await self.repository.bulk_delete(group_permissions_to_delete)
        if failed_deletes:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể thu hồi quyền với id: {', '.join(str(gp.id) for gp in failed_deletes)}"
            )

    async def has_permission(self, group_id: int, permission_name: str, target_id: int | None = None) -> int:
        """
        Kiểm tra quyền của group.
        """
        group_permissions = await self.repository.find_group_permission(group_id, permission_name)
        for gp in group_permissions:
            if not gp.record_enabled:
                continue
            if gp.target_id is None:
                return -1 if gp.is_denied else 1
            if gp.target_id == target_id:
                return -1 if gp.is_denied else 1
        return 0
