# app/schemas/user_permission.py
from pydantic import BaseModel

class UserPermissionBase(BaseModel):
    user_id: int
    permission_id: int
    target_id: int | None = None
    is_active: bool = True
    is_denied: bool = False

class UserPermissionCreate(UserPermissionBase):
    pass

class UserPermissionRead(UserPermissionBase):
    id: int

    class Config:
        orm_mode = True
