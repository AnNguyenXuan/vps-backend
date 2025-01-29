from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schema.group_permission_schema import GroupPermissionCreate, GroupPermissionRead
from app.service.group_permission_service import create_new_group_permission, fetch_group_permission_by_id
from app.configuration.database import get_db

router = APIRouter(prefix="/group-permissions", tags=["Group Permissions"])

@router.post("/", response_model=GroupPermissionRead, status_code=status.HTTP_201_CREATED)
async def create_group_permission(group_permission: GroupPermissionCreate, db: AsyncSession = Depends(get_db)):
    return await create_new_group_permission(db, group_permission)

@router.get("/{group_permission_id}", response_model=GroupPermissionRead)
async def get_group_permission(group_permission_id: int, db: AsyncSession = Depends(get_db)):
    group_permission = await fetch_group_permission_by_id(db, group_permission_id)
    if not group_permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group permission not found")
    return group_permission
