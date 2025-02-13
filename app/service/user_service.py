from fastapi import HTTPException, status
from app.repository.user_repository import UserRepository
from app.schema.user_schema import UserCreate, UserUpdate
from app.model.user import User
from passlib.context import CryptContext
from app.core.exceptions import DuplicateDataError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    
    def __init__(self):
        self.repository = UserRepository()

    async def get_active_users_paginated(self, page: int, limit: int):
        """Lấy danh sách người dùng đang hoạt động theo phân trang"""
        return await self.repository.get_active_users_paginated(page, limit)

    async def get_user_by_id(self, user_id: int):
        """Tìm người dùng theo ID (chỉ lấy user đang hoạt động)"""
        user = await self.repository.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def get_user_by_username(self, username: str):
        """Tìm người dùng theo username (chỉ lấy user đang hoạt động)"""
        user = await self.repository.get_user_by_username(username)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def get_user_by_email(self, email: str):
        """Tìm người dùng theo email (chỉ lấy user đang hoạt động)"""
        user = await self.repository.get_user_by_email(email)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def create_superadmin(self, password: str):
        """Tạo superadmin"""
        hashed_password = pwd_context.hash(password)
        new_user = User(username="superadmin", password=hashed_password)
        try:
            await self.repository.create_user(new_user)
            return True
        except DuplicateDataError:
            return False

    async def change_superadmin_password(self, new_password: str):
        """Thay đổi mật khẩu superadmin"""
        try:
            user = await self.get_user_by_username("superadmin")
            user.password = pwd_context.hash(new_password)
            await self.repository.update_user(user)
            return True
        except Exception:
            return False

    async def create_user(self, user_data: UserCreate):
        """Tạo người dùng mới"""
        # Chuyển Pydantic model thành dictionary
        data = user_data.model_dump()
        if data["username"] in ["superadmin", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create user with username: superadmin, admin"
            )
        # Hash mật khẩu trước khi tạo instance của User
        data["password"] = pwd_context.hash(data["password"])
        # Sử dụng dictionary unpacking để map dữ liệu
        new_user = User(**data)
        try:
            return await self.repository.create_user(new_user)
        except DuplicateDataError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def update_user(self, user_id: int, user_data: UserUpdate):
        """Cập nhật thông tin người dùng"""
        user = await self.get_user_by_id(user_id)
        # Chỉ lấy các trường có giá trị được cập nhật
        update_data = user_data.model_dump(exclude_unset=True)

        # Kiểm tra và xử lý riêng trường username
        if "username" in update_data:
            if update_data["username"] in ["superadmin", "admin"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot update username: superadmin, admin"
                )
        # Nếu có cập nhật password thì hash lại mật khẩu
        if "password" in update_data:
            update_data["password"] = pwd_context.hash(update_data["password"])

        # Cập nhật các trường có trong update_data vào instance User hiện tại
        for key, value in update_data.items():
            setattr(user, key, value)
        return await self.repository.update_user(user)

    async def delete_user(self, user_id: int):
        """Xóa người dùng"""
        user = await self.get_user_by_id(user_id)
        if user.username == "superadmin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete superadmin"
            )
        return await self.repository.delete_user(user)

    async def verify_user_password(self, username: str, password: str):
        """Kiểm tra mật khẩu đăng nhập"""
        user = await self.get_user_by_username(username)
        if not pwd_context.verify(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The password is incorrect"
            )
        return user

    async def change_user_password(self, user: User, current_password: str, new_password: str):
        """Thay đổi mật khẩu người dùng"""
        if not pwd_context.verify(current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        user.password = pwd_context.hash(new_password)
        return await self.repository.update_user(user)
