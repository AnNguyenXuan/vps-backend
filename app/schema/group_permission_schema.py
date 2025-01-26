# app/schemas/group_permission.py
from pydantic import BaseModel

class GroupPermissionBase(BaseModel):
    group_id: int
    permission_id: int
    target_id: int | None = None
    is_active: bool = True
    is_denied: bool = False

class GroupPermissionCreate(GroupPermissionBase):
    pass

class GroupPermissionRead(GroupPermissionBase):
    id: int

    class Config:
        orm_mode = True
