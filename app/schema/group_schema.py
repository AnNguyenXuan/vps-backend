# app/schemas/group.py
from pydantic import BaseModel

class GroupBase(BaseModel):
    name: str
    description: str | None = None

class GroupCreate(GroupBase):
    pass

class GroupRead(GroupBase):
    id: int

    class Config:
        orm_mode = True
