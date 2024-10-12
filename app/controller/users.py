from fastapi import APIRouter, HTTPException
from app.models.users import User  # Import model User
from app.schemas.users import UserCreate, UserOut
from typing import List

router = APIRouter()

# Tạo mới một người dùng, sử dụng schema UserCreate để validate đầu vào
@router.post("/", response_model=UserOut)
async def create_user(user_create: UserCreate):
    user_obj = await User.create(**user_create.dict())  # Tạo người dùng từ dữ liệu schema
    return user_obj  # Trả về đối tượng user dưới dạng UserOut

# Lấy danh sách tất cả người dùng, trả về danh sách các schema UserOut
@router.get("/", response_model=List[UserOut])
async def get_users():
    users = await User.all()
    return users
