# main.py

from fastapi import FastAPI
from app.configuration.database import engine, Base
from app.controller.category_controller  import router as category_router
from app.controller.group_controller import router as group_router
from app.controller.group_member_controller import router as group_member_router
from app.controller.group_permission_controller import router as group_permission_router
from app.controller.permission_controller import router as permission_router
# from app.controller.product_controller import router as product_router
from app.controller.user_controller import router as user_router
from app.controller.user_permission_controller import router as user_permission_router

from contextlib import asynccontextmanager
from app.configuration.security import JWTMiddleware  # Import middleware

# Import các model để tạo bảng
from app.model.user import User
from app.model.product import Product
from app.model.group import Group
from app.model.permission import Permission
from app.model.group_member import GroupMember
from app.model.category import Category
from app.model.group_permission import GroupPermission
from app.model.user_permission import UserPermission

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: tạo bảng nếu chưa tồn tại
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: xử lý đóng kết nối, nếu cần

app = FastAPI(lifespan=lifespan)

# Thêm JWT Middleware để gán user id vào ContextVar cho mỗi request
app.add_middleware(JWTMiddleware)

# Đăng ký các router
app.include_router(category_router)
app.include_router(group_router)
app.include_router(group_member_router)
app.include_router(group_permission_router)
app.include_router(user_router)
# app.include_router(product_router)
app.include_router(permission_router)
app.include_router(user_permission_router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the backend of Scime E-Commerce!"}
