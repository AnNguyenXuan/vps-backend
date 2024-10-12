from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.api.endpoints import users

app = FastAPI()

# Đăng ký các endpoints từ user router
app.include_router(users.router)

# Kết nối với cơ sở dữ liệu PostgreSQL
register_tortoise(
    app,
    db_url="postgres://Thang:123456@localhost:5432/dbname",
    modules={"models": ["app.models.users"]},  # Đường dẫn tới model user
    generate_schemas=True,
    add_exception_handlers=True,
)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
