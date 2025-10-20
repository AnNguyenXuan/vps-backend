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
CEPH_USER_CAPS = os.getenv("CEPH_USER_CAPS")