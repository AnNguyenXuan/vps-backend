from fastapi import APIRouter, HTTPException
from app.models.user import User
from app.schemas.users import UserCreate, UserOut
from typing import List

router = APIRouter()

# Tạo mới một người dùng, sử dụng schema UserCreate để validate đầu vào
@router.post("/", response_model=UserOut)
async def create_user(user_create: UserCreate):
    user_obj = await User.create(**user_create.dict())
    return user_obj

# Lấy danh sách tất cả người dùng, trả về danh sách các schema UserOut
@router.get("/", response_model=List[UserOut])
async def get_users():
    users = await User.all()
    return users
