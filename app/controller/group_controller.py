from fastapi import APIRouter, HTTPException, Request, status, Query
from typing import List
from app.schema.group_schema import GroupRead  # và các schema khác nếu cần (GroupCreate, GroupUpdate)
from app.service.group_service import GroupService
# from app.service.authorization_service import AuthorizationService  # Bạn cần tự hiện thực
# from app.validators.group_validator import GroupValidator  # Bạn cần tự hiện thực

router = APIRouter(prefix="/api/group", tags=["Group"])

# Khởi tạo các service
group_service = GroupService()
# authorization_service = AuthorizationService()
# group_validator = GroupValidator()


@router.get("", response_model=List[GroupRead])
async def list_groups(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
):
    """
    Lấy danh sách các nhóm theo phân trang.
    Yêu cầu user phải tồn tại và có quyền "view_groups".
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "view_groups"):
    #     raise HTTPException(status_code=403, detail="E2020")

    groups = await group_service.get_paginated_groups(page, limit)
    # Nếu cần chuyển đổi sang DTO (GroupRead) từ entity, bạn có thể làm trong service hoặc ngay đây
    return groups


@router.get("/{id}", response_model=GroupRead)
async def detail_group(id: int):
    """
    Lấy chi tiết thông tin của 1 group theo id.
    Service sẽ raise HTTPException nếu không tìm thấy.
    """
    group = await group_service.get_group_by_id(id)
    return group


@router.post("", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(request: Request):
    """
    Tạo nhóm mới.
    Yêu cầu user phải tồn tại và có quyền "create_group".
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "create_group"):
    #     raise HTTPException(status_code=403, detail="E2021")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Validate dữ liệu đầu vào theo hành động 'create'
    # validated_data = group_validator.validate_group_data(data, "create")
    # try:
    group = await group_service.create_group(data) #.create_group(validated_data)
    # Trong PHP, có thao tác persist + flush. Ở đây, service/repository sẽ tự xử lý lưu dữ liệu.
    return group
    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=str(e))


@router.put("/{id}", response_model=GroupRead)
async def update_group(id: int, request: Request):
    """
    Cập nhật thông tin của group.
    Yêu cầu user phải tồn tại và có quyền "edit_group" cho group có id được chỉ định.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "edit_group", id):
    #     raise HTTPException(status_code=403, detail="E2021")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # validated_data = group_validator.validate_group_data(data, "update")
    try:
        group = await group_service.update_group(id, data) #.update_group(id, validated_data)
        # Service xử lý việc update và lưu thay đổi (tương đương flush)
        return group
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}")
async def delete_group(id: int, request: Request):
    """
    Xóa group.
    Yêu cầu user phải tồn tại và có quyền "delete_group" cho group có id được chỉ định.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "delete_group", id):
    #     raise HTTPException(status_code=403, detail="E2021")

    try:
        result = await group_service.delete_group(id)
        # Service thực hiện xóa và xử lý việc lưu thay đổi
        return result  # Ví dụ: {"message": "Group deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
