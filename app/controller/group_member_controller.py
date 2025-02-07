from fastapi import APIRouter, HTTPException, Request, status
from typing import List

# Giả sử các schema (DTO) đã được định nghĩa với Pydantic, ví dụ:
from app.schema.group_member_schema import GroupMemberRead  # DTO cho GroupMember
from app.schema.group_schema import GroupRead              # DTO cho Group
from app.schema.user_schema import UserRead                # DTO cho User

# Import service và validator
from app.service.group_member_service import GroupMemberService
# from app.service.authorization_service import AuthorizationService
# from app.validators.group_member_validator import GroupMemberValidator



group_member_service = GroupMemberService()
# authorization_service = AuthorizationService()
# group_member_validator = GroupMemberValidator()

router = APIRouter(prefix="/api/group-member", tags=["GroupMember"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_user_to_group(request: Request):
    """
    Thêm user vào group.
    Yêu cầu: 
      - Người dùng phải tồn tại (user được gán vào request.state.user).
      - Phải có quyền "manage_group_members".
      - Dữ liệu JSON chứa các tham số cần thiết (ví dụ: userId, groupId).
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "manage_group_members"):
    #     raise HTTPException(status_code=403, detail="E2021")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # validated_data = group_member_validator.validate_group_member_data(data)
    group_member = await group_member_service.add_user_to_group(data) #.add_user_to_group(validated_data)
    # Giả sử GroupMemberRead là Pydantic model với orm_mode=True để chuyển đổi entity sang DTO
    return {
        "message": "User added to group successfully",
        "group_member": GroupMemberRead.from_orm(group_member)
    }


@router.post("/remove")
async def remove_user_from_group(request: Request):
    """
    Xóa user khỏi group.
    Yêu cầu:
      - Người dùng hiện tại phải tồn tại và có quyền "manage_group_members".
      - Dữ liệu JSON chứa ít nhất 2 trường 'userId' và 'groupId'.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "manage_group_members"):
    #     raise HTTPException(status_code=403, detail="E2021")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    if "userId" not in data or "groupId" not in data:
        raise HTTPException(status_code=400, detail="Missing parameters")

    try:
        await group_member_service.remove_user_from_group(data)
        return {"message": "User removed from group successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/groups", response_model=List[GroupRead])
async def get_groups_for_user_current(request: Request):
    """
    Lấy danh sách các group mà user hiện tại thuộc về.
    Yêu cầu: Người dùng phải tồn tại và có quyền "view_group_details".
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "view_group_details"):
    #     raise HTTPException(status_code=403, detail="E2021")

    groups = await group_member_service.find_groups_by_user(user)
    return groups


@router.get("/user/{id}/groups", response_model=List[GroupRead])
async def get_groups_for_user(id: int, request: Request):
    """
    Lấy danh sách các group mà user có id được chỉ định thuộc về.
    Yêu cầu: Người dùng hiện tại phải tồn tại và có quyền "view_group_details".
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "view_group_details"):
    #     raise HTTPException(status_code=403, detail="E2021")

    groups = await group_member_service.get_groups_by_user(id)
    return groups


@router.get("/group/{id}/users", response_model=List[UserRead])
async def get_users_in_group(id: int, request: Request):
    """
    Lấy danh sách các user thuộc group có id được chỉ định.
    Yêu cầu: Người dùng hiện tại phải tồn tại và có quyền "view_group_details".
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "view_group_details"):
    #     raise HTTPException(status_code=403, detail="E2021")

    users = await group_member_service.get_users_in_group(id)
    return users


@router.post("/check")
async def is_user_in_group(request: Request):
    """
    Kiểm tra xem một user có thuộc group hay không.
    Yêu cầu:
      - Người dùng hiện tại phải tồn tại và có quyền "view_group_details".
      - Dữ liệu JSON chứa 'userId' và 'groupId'.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "view_group_details"):
    #     raise HTTPException(status_code=403, detail="E2021")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    if "userId" not in data or "groupId" not in data:
        raise HTTPException(status_code=400, detail="Missing parameters")

    try:
        is_in_group = await group_member_service.is_user_in_group(data)
        return {"is_in_group": is_in_group}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
