from fastapi import HTTPException, status
from app.repository.user_permission_repository import UserPermissionRepository
from app.model.user_permission import UserPermission
from app.model.user import User
from app.model.permission import Permission
from .user_service import UserService
from .permission_service import PermissionService
from app.schema.user_permission_schema import (
    UserPermissionsAssign, 
    UserPermissionsUpdate, 
    UserPermissionsRead, 
    UserPermissionsReadDetail, 
    UserPermissionsDelete
)



class UserPermissionService:
    def __init__(self):
        self.repository = UserPermissionRepository()
        self.user_service = UserService()
        self.permission_service = PermissionService()

    async def assign_permissions(self, data: UserPermissionsAssign) -> list:
        """
        Gán (assign) quyền cho người dùng.
        """
        user = await self.user_service.get_user_by_id(data.user_id)
        # Nếu user không tồn tại, UserService sẽ raise HTTPException

        assigned_permissions = []
        user_permissions_to_add = []

        for permission_data in data.permissions:
            # Raise HTTPException nếu permission không tồn tại
            permission = await self.permission_service.get_permission_by_id(permission_data.permission_id)
            user_permission = UserPermission(
                user_id=user.id, 
                permission_id=permission.id, 
                record_enabled=False, 
                is_denied=False
            )
            user_permission.target_id = None if permission_data.target == "all" else permission_data.target

            user_permissions_to_add.append(user_permission)
            assigned_permissions.append({
                "permission": permission.name,
                "target": permission_data.target,
                "status": "assigned"
            })

        await self.repository.bulk_insert(user_permissions_to_add)
        return assigned_permissions

    async def set_permission(self, user: User, permissions: list[Permission]) -> list:
        """
        Khởi tạo quyền cho người dùng (ví dụ: cho superadmin).
        Tham số permissions là danh sách các đối tượng Permission.
        """
        user_permissions = []
        for permission in permissions:
            user_permission = UserPermission()
            user_permission.user_id = user.id
            user_permission.permission_id = permission.id
            user_permission.record_enabled = True
            user_permission.is_denied = False
            user_permission.target_id = None

            user_permissions.append(user_permission)

        await self.repository.bulk_insert(user_permissions)
        return user_permissions

    async def find_permissions_by_user(self, user: User) -> list[UserPermission]:
        """
        Lấy danh sách tên quyền của người dùng.
        """
        return await self.repository.find_by_user_id(user.id)

    async def get_permissions_by_user(self, user: User) -> UserPermissionsRead:
        """
        Lấy danh sách quyền của người dùng và chuyển đổi thành schema UserPermissionsRead.
        """
        user_permissions = await self.repository.find_by_user_id(user.id)
        details = []
        for up in user_permissions:
            permission = await self.permission_service.get_permission_by_id(up.permission_id)
            detail = UserPermissionsReadDetail(
                id=up.id,
                permission_id=up.permission_id,
                name=permission.name,
                record_enabled=up.record_enabled,
                is_denied=up.is_denied,
                target=up.target_id if up.target_id is not None else "all"
            )
            details.append(detail)
        return UserPermissionsRead(user_id=user.id, permissions=details)
    
    async def update_permission(self, data: UserPermissionsUpdate) -> list:
        """
        Cập nhật quyền của người dùng.
        Schema update dựa trên các trường:
          - id: id của UserPermission cần cập nhật.
          - record_enabled: cập nhật trạng thái record_enabled.
          - is_denied: cập nhật trạng thái is_denied.
        """
        user = await self.user_service.get_user_by_id(data.user_id)
        existing_user_permissions = await self.repository.find_by_user_id(user.id)
        # Tạo map từ id đến đối tượng UserPermission để tra cứu nhanh
        user_permission_map = {up.id: up for up in existing_user_permissions}
        updated_permissions = []

        for permission_data in data.permissions:
            if permission_data.id not in user_permission_map:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"UserPermission với id '{permission_data.id}' không được gán cho user"
                )
            user_permission = user_permission_map[permission_data.id]
            # Cập nhật các trường nếu có dữ liệu
            if permission_data.record_enabled is not None:
                user_permission.record_enabled = permission_data.record_enabled
            if permission_data.is_denied is not None:
                user_permission.is_denied = permission_data.is_denied

            updated_permissions.append(user_permission)

        await self.repository.bulk_update(updated_permissions)
        return [{"permission_id": up.permission_id, "status": "updated"} for up in updated_permissions]

    async def delete_permissions(self, data: UserPermissionsDelete) -> None:
        """
        Xóa quyền của người dùng.
        Dữ liệu đầu vào bao gồm:
          - user_id: int
          - permissions: list các permission id cần xóa.
        """
        # Lấy thông tin user; nếu không tồn tại, UserService sẽ raise HTTPException
        user = await self.user_service.get_user_by_id(data.user_id)
        
        # Lấy tất cả các quyền đã được gán cho user
        user_permissions = await self.repository.find_by_user_id(user.id)
        
        # Kiểm tra xem user có được gán các permission_id cần thu hồi hay không
        assigned_permission_ids = {up.permission_id for up in user_permissions}
        requested_permission_ids = set(data.permissions)
        missing_permissions = requested_permission_ids - assigned_permission_ids
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User không có các quyền với permission_id: {', '.join(map(str, missing_permissions))}"
            )
        
        # Lọc ra các bản ghi UserPermission cần xóa (có thể có nhiều bản ghi cho cùng 1 permission_id nếu khác target)
        user_permissions_to_delete = [up for up in user_permissions if up.permission_id in requested_permission_ids]
        
        # Thực hiện xóa hàng loạt
        failed_deletes = await self.repository.bulk_delete(user_permissions_to_delete)
        if failed_deletes:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể thu hồi quyền với id: {', '.join(str(up.id) for up in failed_deletes)}"
            )

    async def has_permission(self, user_id: int, permission_name: str, target_id: int | None = None) -> int:
        """
        Kiểm tra quyền của người dùng.
        Trả về:
          1  : nếu có quyền (active và không bị deny)
         -1  : nếu quyền bị deny
          0  : nếu không tìm thấy quyền nào phù hợp
        """
        user_permissions = await self.repository.find_user_permission(user_id, permission_name)
        for up in user_permissions:
            if not up.record_enabled:
                continue
            if up.target_id is None:
                return -1 if up.is_denied else 1
            if up.target_id == target_id:
                return -1 if up.is_denied else 1
        return 0
