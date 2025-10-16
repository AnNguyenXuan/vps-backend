from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.security import JWTMiddleware  # Import middleware
from app.core.utils import custom_openapi
from app.controller import routers  # Import danh sách routers

app = FastAPI()

@app.on_event("startup")
async def _print_routes():
    print("\n=== ROUTES AVAILABLE ===", flush=True)
    for r in app.routes:
        try:
            print("PATH:", r.path, "METHODS:", getattr(r, "methods", None), flush=True)
        except Exception as e:
            print("ROUTE PRINT ERR:", repr(e), flush=True)
    print("========================\n", flush=True)

# --- Bật CORS ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.1.3:5173",  # IP máy chạy frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Có thể thay bằng ["*"] nếu chỉ test nội bộ
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(JWTMiddleware)

# Đăng ký các router
for router in routers:
    app.include_router(router)

# Gán custom openapi cho app
app.openapi = lambda: custom_openapi(app)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the backend of Scime E-Commerce!"}


