import os
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Cấu hình bảo mật
SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

JWT_ISSUER = os.getenv("JWT_ISSUER", "https://scime.click")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "https://shop.scime.click")
