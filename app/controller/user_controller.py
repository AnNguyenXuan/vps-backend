from fastapi import APIRouter, HTTPException, status, Query
from app.schema.user_schema import UserCreate, UserRead, UserUpdate
from app.service.user_service import UserService
from app.core.security import user_context, authorization



user_service = UserService()
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserRead])
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    ):
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    if not await authorization.check_permission(user_current, "view_users"):
        raise HTTPException(status_code=403, detail="You have no access to this resource")
    users = await user_service.get_active_users_paginated(page, limit)
    return users

@router.get("/me", response_model=UserRead)
async def get_current_user():
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    return user_current

@router.get("/{id}", response_model=UserRead)
async def get_user(id: int):
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    if not await authorization.check_permission(user_current, "view_user_details", id):
        raise HTTPException(status_code=403, detail="You have no access to this resource")
    user = await user_service.get_user_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    return await user_service.create_user(user)

@router.put("/{id}", response_model=UserRead)
async def update_user(
    id: int,
    user_update: UserUpdate,
    ):
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    if not await authorization.check_permission(user_current, "edit_user", id) and user_current.id != id:
        raise HTTPException(status_code=403, detail="The user role is not allowed to perform this action")
    updated_user = await user_service.update_user(id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_user(
    id: int,
    ):
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")
    if not await authorization.check_permission(user_current, "delete_user"):
        raise HTTPException(status_code=403, detail="The user role is not allowed to perform this action")
    success = await user_service.delete_user(id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
