# Kiến trúc backend

Được thiết kế dựa trên mô hình MVC, chia thành các lớp tương tác dữ liệu khác nhau, xử lý theo thứ tự các luồng.

---
# Yêu cầu hệ thống

- **Python:** Phiên bản 3.9 hoặc mới hơn. (tôi đang dùng Python 3.13.2)
- **FastAPI:** Framework chính của dự án.
- **SQLAlchemy (Async):** ORM cho các thao tác cơ sở dữ liệu.
- **Pydantic:** Dùng để xác thực và serialize dữ liệu.
- **Database:** PostgreSQL.
- **Các thư viện khác:** `python-jose` (JWT), `passlib` (hashing), `uvicorn` (ASGI server).
---
# Cấu trúc 
```
app/
├── controller/       # Các API endpoint (controllers) xử lý request/response.
├── core/             # Các module cốt lõi: cấu hình, database, CLI (cmd.py), security, exception và utils.
├── model/            # Các model SQLAlchemy định nghĩa cấu trúc bảng.
├── repository/       # Lớp truy cập dữ liệu, quản lý kết nối với database.
├── schema/           # Các Pydantic schema dùng để validate và serialize dữ liệu.
└── service/          # Lớp business logic xử lý nghiệp vụ: authentication, authorization, và các thao tác domain.
```
---
# Cấu trúc lớp core

Lớp core có một số hàm cốt lõi

**config.py** : được dùng để nạp biến môi trường, các biến này sau khi được nạp vào .env sẽ được đọc
```
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
# Load biến môi trường từ .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Cấu hình bảo mật
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE = 60*int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))  # 1 giờ
REFRESH_TOKEN_EXPIRE = 86400*int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 60))  # 60 ngày

JWT_ISSUER = os.getenv("JWT_ISSUER", "https://scime.click")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "https://shop.scime.click")

FERNET_KEY = os.getenv("FERNET_KEY")

CEPH_ADMIN_ENDPOINT = os.getenv("CEPH_ADMIN_ENDPOINT")
CEPH_PUBLIC_ENDPOINT = os.getenv("CEPH_PUBLIC_ENDPOINT")
CEPH_REGION = os.getenv("CEPH_REGION")
CEPH_KEY_TYPE = os.getenv("CEPH_KEY_TYPE")
CEPH_ADMIN_ACCESS_KEY = os.getenv("CEPH_ADMIN_ACCESS_KEY")
CEPH_ADMIN_SECRET_KEY = os.getenv("CEPH_ADMIN_SECRET_KEY")
```
**crypto.py**: được dùng để mã hóa một số thông tin nhạy cảm
```
from cryptography.fernet import Fernet
from app.core import config

cipher = Fernet(config.FERNET_KEY.encode())

def encrypt(text: str) -> str:
    return cipher.encrypt(text.encode()).decode()

def decrypt(cipher_text: str) -> str:
    return cipher.decrypt(cipher_text.encode()).decode()
```
**security**: triển khai JWT bảo mật
```
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar
from app.model.user import User
from app.service.authentication_service import AuthenticationService
from app.service.authorization_service import AuthorizationService

authentication = AuthenticationService()
authorization = AuthorizationService()

user_context: ContextVar[User | None] = ContextVar("user_context", default=None)
payload_context: ContextVar[str | None] = ContextVar("payload_context", default=None)

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header: str | None = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try: 
                user, payload = await authentication.get_current_user(token)
                user_context.set(user)
                payload_context.set(payload)
                if payload['type']!='access':
                    return JSONResponse(
                    status_code=401,
                    content={"detail": 'Invalid token'},
                )
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.detail},
                )
        else:
            user_context.set(None)
            payload_context.set(None)

        response = await call_next(request)
        return response
```
**database.py**: lớp engine kết nối SQL
```
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL


# Tạo engine kết nối với cơ sở dữ liệu
engine = create_async_engine(DATABASE_URL) # thêm echo = True để bật logging SQL

# Tạo session factory
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base cho các model
Base = declarative_base()
```
**exceptions.py**: lớp xử lý các lỗi truy vấn tới database
```
class DuplicateDataError(Exception):
    """Exception khi có lỗi trùng dữ liệu (ví dụ: username hoặc email đã tồn tại)."""
    def __init__(self, message: str = "Dữ liệu đã tồn tại"):
        self.message = message
        super().__init__(self.message)

class NotFoundError(Exception):
    """Exception khi dữ liệu không tồn tại."""
    def __init__(self, message: str = "Dữ liệu không tồn tại"):
        self.message = message
        super().__init__(self.message)
```
---
# Cấu trúc lớp model

Lớp này định nghĩa cấu trúc database

Hàm khởi tạo /app/model/__init__.py
```
from .user import User
from .product import Product
from .group import Group
from .permission import Permission
from .group_member import GroupMember
from .category import Category
from .group_permission import GroupPermission
from .user_permission import UserPermission
from .blacklist_token import BlacklistToken
from .refresh_token import RefreshToken
from .product_option import ProductOption
from .s3_account import S3Account 
# Danh sách tất cả model (dùng để import gọn)
all_models = [
    User,
    S3Account,
    Product,
    Group,
    Permission,
    GroupMember,
    Category,
    GroupPermission,
    UserPermission,
    BlacklistToken,
    RefreshToken,
    ProductOption
]
```
Khi tạo một bảng mới, ta tạo 1 file quy ước <tên_bảng>.py

Ví dụ như bảng users dưới đây
```
from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    username = Column(String(20), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, unique=True, index=True)
    phone = Column(String(15), nullable=True)
    address = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
```
---
# Cấu trúc lớp repository

Lớp này được sử dụng để kết nối đến database

Ta sẽ luôn cần khai báo 2 core **exceptions** và **database** để xử lý kết nối và lỗi. Ngoài ra tùy thuộc vào thiết kế database, có thể sẽ cần gọi cả các bảng khác vào để thực hiện các truy vấn chồng chéo.

Ví dụ như lớp user_repository.py dưới đây
```
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.model.user import User
from app.core.database import AsyncSessionLocal
from app.core.exceptions import DuplicateDataError

class UserRepository:

    async def create_user(self, new_user: User):
        """Tạo mới người dùng với xử lý lỗi trùng dữ liệu"""
        async with AsyncSessionLocal() as session:
            try:
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                return new_user
            except IntegrityError:
                await session.rollback()
                raise DuplicateDataError("Username hoặc Email đã tồn tại")

    async def update_user(self, user: User):
        """Cập nhật thông tin người dùng"""
        async with AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def delete_user(self, user: User) -> bool:
        """Xóa người dùng và trả về True nếu thành công, False nếu thất bại"""
        async with AsyncSessionLocal() as session:
            try:
                await session.delete(user)
                await session.commit()
                return True  # Xóa thành công
            except SQLAlchemyError:
                await session.rollback()  # Rollback nếu có lỗi
                return False  # Xóa thất bại

    async def get_active_users_paginated(self, page: int, limit: int):
        """Lấy danh sách user đang hoạt động (is_active=True) với phân trang"""
        offset = (page - 1) * limit
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User)
                .where(User.is_active == True)
                .order_by(User.id.asc())
                .offset(offset)
                .limit(limit)
            )
            return result.scalars().all()

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Tìm user theo ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """Tìm user theo username"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.username == username))
            return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Tìm user theo email"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
```
---
# Cấu trúc lớp service 

Lớp service cung cấp các thao tác xử lý nghiệp vụ

Ví dụ như lớp user_service dưới đây, cung cấp các lớp nghiệp vụ phục vụ cho các người dùng admin hay user
```
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
            superadmin = await self.repository.create_user(new_user)
            return superadmin
        except DuplicateDataError:
            return None

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
```
---
# Cấu trúc lớp schema

Lớp schema là một lớp đệm cung cấp cấu trúc dữ liệu cho lớp controller trước khi đẩy xuống lớp service. Điều này đảm bảo cấu trúc dữ liệu không bị lỗi và có thể dễ dàng mở rộng cấu trúc nếu muốn. Dựa vào lớp này, frontend có thể chuẩn hóa dữ liệu gửi về theo yêu cầu ở backend.

Ví dụ như lớp user_schema dưới đây.
```
from pydantic import BaseModel, EmailStr, field_validator, StringConstraints
from typing_extensions import Annotated
import re
from datetime import datetime


class UserBase(BaseModel):
    username: Annotated[
        str, 
        StringConstraints(
            min_length=3, 
            max_length=20, 
            strip_whitespace=True
        )
    ]
    email: EmailStr | None = None
    phone: Annotated[
        str, 
        StringConstraints(min_length=10, max_length=15, pattern=r"^[0-9]+$")
    ] | None = None
    address: Annotated[str, StringConstraints(max_length=255)] | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        """
        - Chỉ chứa chữ cái, số và dấu gạch dưới (_)
        - Không bắt đầu hoặc kết thúc bằng dấu gạch dưới
        """
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError("Username chỉ được chứa chữ cái, số và dấu gạch dưới (_)")
        if value.startswith("_") or value.endswith("_"):
            raise ValueError("Username không được bắt đầu hoặc kết thúc bằng dấu gạch dưới (_)")
        return value


class UserCreate(UserBase):
    password: Annotated[str, StringConstraints(min_length=6, max_length=18)]

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        """
        - Mật khẩu từ 6-18 ký tự.
        - Phải chứa ít nhất 1 chữ hoa, 1 chữ thường, 1 số và 1 ký tự đặc biệt.
        - Không chứa khoảng trắng.
        """
        if " " in value:
            raise ValueError("Mật khẩu không được chứa khoảng trắng")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ cái viết hoa")
        if not re.search(r"[a-z]", value):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ cái viết thường")
        if not re.search(r"\d", value):
            raise ValueError("Mật khẩu phải chứa ít nhất một số")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Mật khẩu phải chứa ít nhất một ký tự đặc biệt")
        return value

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "phone": "0987654321",
                "address": "123 Đường ABC, Quận 1, TP.HCM",
                "password": "StrongP@ss1"
            }
        }
    }


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
        "json_schema_extra": {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john.doe@example.com",
                "phone": "0987654321",
                "address": "123 Đường ABC, Quận 1, TP.HCM",
                "created_at": "2025-01-01T12:00:00",
                "updated_at": "2025-02-01T12:00:00"
            }
        }
    }


class UserUpdate(UserBase):
    password: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if value:  # Chỉ kiểm tra nếu có giá trị mới
            if " " in value:
                raise ValueError("Mật khẩu không được chứa khoảng trắng")
            if not re.search(r"[A-Z]", value):
                raise ValueError("Mật khẩu phải chứa ít nhất một chữ cái viết hoa")
            if not re.search(r"[a-z]", value):
                raise ValueError("Mật khẩu phải chứa ít nhất một chữ cái viết thường")
            if not re.search(r"\d", value):
                raise ValueError("Mật khẩu phải chứa ít nhất một số")
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
                raise ValueError("Mật khẩu phải chứa ít nhất một ký tự đặc biệt")
        return value

    model_config = {
        "from_attributes": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
        "json_schema_extra": {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "phone": "0987654321",
                "address": "123 Đường ABC, Quận 1, TP.HCM",
                "password": "NewStrongP@ss1"
            }
        }
    }
```
---
# Cấu trúc lớp controller

Khởi tạo các router, mỗi khi xây 1 lớp router mới, cần khai báo router đó vào hàm **app/controller/__init__.py**

Ví dụ như dưới đây : 
```
from .category_controller import router as category_router
from .group_controller import router as group_router
from .group_member_controller import router as group_member_router
from .group_permission_controller import router as group_permission_router
from .permission_controller import router as permission_router
# from .product_controller import router as product_router
from .user_controller import router as user_router
from .user_permission_controller import router as user_permission_router
from .security_controller import router as security_router
from .s3_controller import router as s3_router

routers = [
    security_router,
    category_router,
    group_router,
    group_member_router,
    group_permission_router,
    permission_router,
    # product_router,
    user_router,
    s3_router,
    user_permission_router,
]
```

Các endpoint API của mỗi dịch vụ được định nghĩa theo cấu trúc <tên_dịch_vụ>_controller.py

Ví dụ ta cung cấp API cho user_controller.py
```
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
```
Một điểm lưu ý của lớp này, đó chính là các quá trình login logout hay truy vấn một số tài nguyên quan trọng cần thông qua API xác thực **security_controller.py**
```
from fastapi import APIRouter, HTTPException, status
from app.core.security import authentication, user_context, payload_context
from app.service.user_service import UserService
from app.schema.auth_schema import (
    LoginRequest,
    TokenResponse,
    AccessTokenResponse,
    RefreshTokenResponse,
    ChangePasswordRequest,
    VerifyPasswordRequest,
    RefreshTokenRequest
)

user_service = UserService()

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    current_user = user_context.get()
    if current_user is not None:
        raise HTTPException(status_code=403, detail="You have already logged in")
    access_token, refresh_token = await authentication.login(request)
    return {"accessToken": access_token, "refreshToken": refresh_token}

@router.post("/refresh-token", response_model=AccessTokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    try:
        access_token = await authentication.refresh_access_token(request.refreshToken)
        return {"accessToken": access_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/logout", status_code=status.HTTP_200_OK)
async def logout():
    try:
        await authentication.logout(payload_context.get())
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(request: ChangePasswordRequest):
    current_user = user_context.get()
    if current_user is None:
        raise HTTPException(status_code=401, detail="You have not logged in")
    try:
        await user_service.change_user_password(current_user, request.currentPassword, request.newPassword)
        return {"message": "Password changed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-password", status_code=status.HTTP_200_OK)
async def verify_password(request: VerifyPasswordRequest):
    current_user = user_context.get()
    if current_user is None:
        raise HTTPException(status_code=401, detail="You have not logged in")
    await user_service.verify_user_password(current_user.username, request.password)
    return {"message": "Password is correct"}

@router.post("/refresh-refresh-token", response_model=RefreshTokenResponse)
async def refresh_refresh_token(request: RefreshTokenRequest):
    try:
        new_refresh_token = await authentication.refresh_refresh_token(request.refreshToken)
        return {"refreshToken": new_refresh_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```
---



