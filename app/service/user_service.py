from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repository.user_repository import UserRepository
from app.schema.user_schema import UserCreate, UserUpdate
from app.model.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    
    def __init__(self):
        self.repository = UserRepository()

    async def get_all_active_users(self, db: AsyncSession):
        """ Lấy tất cả người dùng đang hoạt động """
        return await self.repository.get_active_users_paginated(db, page=1, limit=1000)

    async def get_active_users_paginated(self, db: AsyncSession, page: int, limit: int):
        """ Lấy danh sách người dùng đang hoạt động theo phân trang """
        return await self.repository.get_active_users_paginated(db, page, limit)

    async def get_user_by_id(self, db: AsyncSession, user_id: int):
        """ Tìm người dùng theo ID (chỉ lấy user đang hoạt động) """
        user = await self.repository.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def get_user_by_username(self, db: AsyncSession, username: str):
        """ Tìm người dùng theo username (chỉ lấy user đang hoạt động) """
        user = await self.repository.get_user_by_username(db, username)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def get_user_by_email(self, db: AsyncSession, email: str):
        """ Tìm người dùng theo email (chỉ lấy user đang hoạt động) """
        user = await self.repository.get_user_by_email(db, email)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def create_user(self, db: AsyncSession, user_data: UserCreate):
        """ Tạo người dùng mới """
        hashed_password = pwd_context.hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password,
            phone=user_data.phone,
            address=user_data.address,
            is_active=user_data.is_active,
        )
        return await self.repository.create_user(db, new_user)

    async def update_user(self, db: AsyncSession, user_id: int, user_data: UserUpdate):
        """ Cập nhật thông tin người dùng """
        user = await self.get_user_by_id(db, user_id)

        if user_data.username:
            user.username = user_data.username
        if user_data.email:
            user.email = user_data.email
        if user_data.password:
            user.password = pwd_context.hash(user_data.password)
        if user_data.phone:
            user.phone = user_data.phone
        if user_data.address:
            user.address = user_data.address

        return await self.repository.update_user(db, user)

    async def delete_user(self, db: AsyncSession, user_id: int):
        """ Xóa người dùng """
        user = await self.get_user_by_id(db, user_id)

        if user.username == "superadmin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete superadmin")

        return await self.repository.delete_user(db, user)

    async def verify_user_password(self, db: AsyncSession, username: str, password: str):
        """ Kiểm tra mật khẩu đăng nhập """
        user = await self.get_user_by_username(db, username)
        if not pwd_context.verify(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
        return user

    async def change_user_password(self, db: AsyncSession, user_id: int, current_password: str, new_password: str):
        """ Thay đổi mật khẩu người dùng """
        user = await self.get_user_by_id(db, user_id)
        if not pwd_context.verify(current_password, user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")

        user.password = pwd_context.hash(new_password)
        return await self.repository.update_user(db, user)
