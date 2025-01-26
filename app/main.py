# app/main.py
from fastapi import FastAPI
from app.controller.group import router as group_router
from app.configuration.database import engine, Base
from contextlib import asynccontextmanager

# Import model để SQLAlchemy nhận diện
from app.models.user import User
# from app.models.product import Product

# Lifespan context manager để thay thế @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code trước khi ứng dụng khởi động (startup)
    async with engine.begin() as conn:
        # Tạo bảng nếu chưa tồn tại
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Code sau khi ứng dụng tắt (shutdown)
    # Nếu cần làm sạch hoặc đóng kết nối DB, bạn có thể làm ở đây

# Khởi tạo FastAPI và đăng ký Lifespan event handler
app = FastAPI(lifespan=lifespan)

app.include_router(group_router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI E-Commerce backend!"}
