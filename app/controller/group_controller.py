from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from app.core.security import user_context, authorization
from app.schema.group_schema import GroupCreate, GroupUpdate, GroupRead
from app.service.group_service import GroupService




router = APIRouter(prefix="/group", tags=["Group"])

# Khởi tạo các service
group_service = GroupService()


@router.get("", response_model=List[GroupRead])
async def list_groups(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
):
    """
    Lấy danh sách các nhóm theo phân trang.
    Yêu cầu user phải tồn tại và có quyền "view_groups".
    """
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    if not await authorization.check_permission(user_current, "view_groups"):
        raise HTTPException(status_code=403, detail="You have no access to this resource")

    return await group_service.get_paginated_groups(page, limit)


@router.get("/{id}", response_model=GroupRead)
async def detail_group(id: int):
    """
    Lấy chi tiết thông tin của 1 group theo id.
    Service sẽ raise HTTPException nếu không tìm thấy.
    """
    return await group_service.get_group_by_id(id)


@router.post("", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(group: GroupCreate):
    """
    Tạo nhóm mới.
    Yêu cầu user phải tồn tại và có quyền "create_group".
    """
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    if not await authorization.check_permission(user_current, "create_group"):
        raise HTTPException(status_code=403, detail="The user role is not allowed to perform this action")

    return await group_service.create_group(group)


@router.put("/{id}", response_model=GroupRead)
async def update_group(id: int, group_update: GroupUpdate):
    """
    Cập nhật thông tin của group.
    Yêu cầu user phải tồn tại và có quyền "edit_group" cho group có id được chỉ định.
    """
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    if not await authorization.check_permission(user_current, "edit_group", id):
        raise HTTPException(status_code=403, detail="The user role is not allowed to perform this action")

    return await group_service.update_group(id, group_update)


@router.delete("/{id}")
async def delete_group(id: int):
    """
    Xóa group.
    Yêu cầu user phải tồn tại và có quyền "delete_group" cho group có id được chỉ định.
    """
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    if not await authorization.check_permission(user_current, "delete_group", id):
        raise HTTPException(status_code=403, detail="The user role is not allowed to perform this action")

    return await group_service.delete_group(id)
