from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.users import User  # Import model User
from app.schemas.users import TokenData  # Import TokenData schema
from app.configuration.config import settings  # Import cấu hình settings

# Khai báo các biến cần thiết
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Thiết lập hashing cho password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer là đường dẫn để yêu cầu token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Tạo hàm để hash password
def get_password_hash(password: str):
    return pwd_context.hash(password)

# Hàm để xác thực password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Hàm để xác thực user
def authenticate_user(username: str, password: str):
    user = User.get(username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Hàm để tạo access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Hàm giải mã và kiểm tra token
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = User.get(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Hàm phân quyền cho admin
def get_current_active_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have enough privileges",
        )
    return current_user
