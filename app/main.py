from fastapi import FastAPI
from app.controller import routers  # Import danh sách routers
from app.core.security import JWTMiddleware  # Import middleware

app = FastAPI()

app.add_middleware(JWTMiddleware)

# Đăng ký các router
for router in routers:
    app.include_router(router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the backend of Scime E-Commerce!"}
