from fastapi import APIRouter, HTTPException, status
from app.core.security import user_context, authorization
from app.service.group_permission_service import GroupPermissionService
from app.service.group_service import GroupService
from app.schema.group_permission_schema import (
    GroupPermissionsAssign,
    GroupPermissionsUpdate,
    GroupPermissionsDelete,
    GroupPermissionsRead,
)

router = APIRouter(prefix="/group-permissions", tags=["GroupPermission"])

group_service = GroupService()
group_permission_service = GroupPermissionService()


@router.get("/{group_id}", response_model=GroupPermissionsRead)
async def get_permissions_by_group(group_id: int):
    """
    Lấy danh sách quyền của Group.
    """
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    
    # Kiểm tra quyền
    # if not authorization.check_permission(user_current, "view_permissions"):
    #     raise HTTPException(status_code=403, detail="E2021")

    target_group = await group_service.get_group_by_id(group_id)
    return await group_permission_service.get_permissions_by_group(target_group)


@router.post("", status_code=status.HTTP_201_CREATED)
async def assign_permission(payload: GroupPermissionsAssign):
    """
    Gán (assign) danh sách quyền cho Group.
    """
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    
    # Kiểm tra quyền
    # if not authorization.check_permission(user_current, "create_permission"):
    #     raise HTTPException(status_code=403, detail="E2021")

    return await group_permission_service.assign_permissions(payload)


@router.put("") # , response_model=GroupPermissionsRead
async def update_permission(payload: GroupPermissionsUpdate):
    """
    Cập nhật quyền của Group.
    """
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    
    # Kiểm tra quyền
    # if not authorization.check_permission(user_current, "edit_permission"):
    #     raise HTTPException(status_code=403, detail="E2021")

    return await group_permission_service.update_permission(payload)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(payload: GroupPermissionsDelete):
    """
    Xóa danh sách quyền của Group.
    """
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    
    # Kiểm tra quyền
    # if not authorization.check_permission(user_current, "delete_permission"):
    #     raise HTTPException(status_code=403, detail="E2021")

    await group_permission_service.delete_permissions(payload)
