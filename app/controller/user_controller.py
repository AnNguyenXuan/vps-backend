from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.schema.user_schema import UserCreate, UserRead, UserUpdate
from app.service.user_service import UserService
from app.service.authorization_service import AuthorizationService
from app.configuration.database import get_db
from app.models.user_model import User

user_service = UserService()
auth_service = AuthorizationService()
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserRead])
async def list_users(
    db: AsyncSession = Depends(get_db),
    user_current: User = Depends(auth_service.get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
):
    if not auth_service.check_permission(user_current, "view_users"):
        raise HTTPException(status_code=403, detail="E2020")

    users = await user_service.get_active_users_with_pagination(db, page, limit)
    return users


@router.get("/me", response_model=UserRead)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    if not user:
        raise HTTPException(status_code=404, detail="E2002")
    return user


@router.get("/{id}", response_model=UserRead)
async def get_user(
    id: int,
    db: AsyncSession = Depends(get_db),
    user_current: User = Depends(auth_service.get_current_user),
):
    if not auth_service.check_permission(user_current, "view_user_details", id):
        raise HTTPException(status_code=403, detail="E2020")

    user = await user_service.get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_service.create_user(db, user)


@router.put("/{id}", response_model=UserRead)
async def update_user(
    id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    user_current: User = Depends(auth_service.get_current_user),
):
    if not auth_service.check_permission(user_current, "edit_user", id) and user_current.id != id:
        raise HTTPException(status_code=403, detail="E2021")

    updated_user = await user_service.update_user(db, id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return updated_user


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_user(
    id: int,
    db: AsyncSession = Depends(get_db),
    user_current: User = Depends(auth_service.get_current_user),
):
    if not auth_service.check_permission(user_current, "delete_user"):
        raise HTTPException(status_code=403, detail="E2021")

    success = await user_service.delete_user(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted"}
