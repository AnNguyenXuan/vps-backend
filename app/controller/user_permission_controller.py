from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schema.user_permission_schema import UserPermissionCreate, UserPermissionRead
from app.service.user_permission_service import create_new_user_permission, fetch_user_permission_by_id
from app.configuration.database import get_db

router = APIRouter(prefix="/user-permissions", tags=["User Permissions"])

@router.post("/", response_model=UserPermissionRead, status_code=status.HTTP_201_CREATED)
async def create_user_permission(user_permission: UserPermissionCreate, db: AsyncSession = Depends(get_db)):
    return await create_new_user_permission(db, user_permission)

@router.get("/{user_permission_id}", response_model=UserPermissionRead)
async def get_user_permission(user_permission_id: int, db: AsyncSession = Depends(get_db)):
    user_permission = await fetch_user_permission_by_id(db, user_permission_id)
    if not user_permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User permission not found")
    return user_permission
