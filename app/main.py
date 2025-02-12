from fastapi import FastAPI
from app.core.security import JWTMiddleware  # Import middleware
from app.core.utils import custom_openapi
from app.controller import routers  # Import danh sách routers

app = FastAPI()

app.add_middleware(JWTMiddleware)

# Đăng ký các router
for router in routers:
    app.include_router(router)

# Gán custom openapi cho app
app.openapi = lambda: custom_openapi(app)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the backend of Scime E-Commerce!"}
