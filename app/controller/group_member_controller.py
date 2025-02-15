from fastapi import APIRouter, HTTPException, status
from app.core.security import user_context, authorization
from typing import List
from app.schema.group_member_schema import GroupMemberBase, GroupMemberCreate, GroupMemberRead
from app.schema.group_schema import GroupRead
from app.schema.user_schema import UserRead
from app.service.group_member_service import GroupMemberService



group_member_service = GroupMemberService()

router = APIRouter(prefix="/group-member", tags=["GroupMember"])


@router.post("/add", status_code=status.HTTP_201_CREATED, response_model=GroupMemberRead)
async def add_user_to_group(data: GroupMemberCreate):
    """
    Thêm user vào group.
    """
    # if not authorization.check_permission(user, "manage_group_members"):
    #     raise HTTPException(status_code=403, detail="The user role is not allowed to perform this action")
    return await group_member_service.add_user_to_group(data)

@router.delete("/remove")
async def remove_user_from_group(data: GroupMemberBase):
    """
    Xóa user khỏi group.
    """
    # user_current = user_context.get()
    # if user_current is None:
    #     raise HTTPException(status_code=401, detail="E2025")
    # if not authorization.check_permission(user, "manage_group_members"):
    #     raise HTTPException(status_code=403, detail="The user role is not allowed to perform this action")
    try:
        await group_member_service.remove_user_from_group(data)
        return {"message": "User removed from group successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/groups", response_model=List[GroupRead])
async def get_groups_for_user_current():
    """
    Lấy danh sách các group mà user hiện tại thuộc về.
    Yêu cầu: Người dùng phải đang đăng nhập".
    """
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    return  await group_member_service.find_groups_by_user(user_current)


@router.get("/user/{id}/groups", response_model=List[GroupRead])
async def get_groups_for_user(id: int):
    """
    Lấy danh sách các group mà user có id được chỉ định thuộc về.
    Yêu cầu: Người dùng hiện tại phải đăng nhập và có quyền "view_group_details".
    """
    # user_current = user_context.get()
    # if not user_current:
    #     raise HTTPException(status_code=401, detail="You have not logged in")
    # if not authorization.check_permission(user, "view_group_details"):
    #     raise HTTPException(status_code=403, detail="There is no access to this resource")
    groups = await group_member_service.get_groups_by_user(id)
    return groups


@router.get("/group/{id}/users", response_model=List[UserRead])
async def get_users_in_group(id: int):
    """
    Lấy danh sách các user thuộc group có id được chỉ định.
    Yêu cầu: Người dùng hiện tại phải tồn tại và có quyền "view_group_details".
    """
    # user_current = user_context.get()
    # if not user_current:
    #     raise HTTPException(status_code=401, detail="You have not logged in")
    # if not authorization.check_permission(user, "view_group_details"):
    #     raise HTTPException(status_code=403, detail="There is no access to this resource")
    users = await group_member_service.get_users_in_group(id)
    return users


@router.post("/check")
async def is_user_in_group(data: GroupMemberBase):
    """
    Kiểm tra xem một user có thuộc group hay không.
    Yêu cầu:
      - Người dùng hiện tại phải tồn tại và có quyền "view_group_details".
      - Dữ liệu JSON chứa 'userId' và 'groupId'.
    """
    # user_current = user_context.get()
    # if not user_current:
    #     raise HTTPException(status_code=401, detail="You have not logged in")
    # if not authorization.check_permission(user, "view_group_details"):
    #     raise HTTPException(status_code=403, detail="The user role is not allowed to perform this action")
    try:
        is_in_group = await group_member_service.is_user_in_group(data)
        return {"is_in_group": is_in_group}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
