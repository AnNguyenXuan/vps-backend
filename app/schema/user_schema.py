# app/schemas/user.py
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: str | None = None
    address: str | None = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
