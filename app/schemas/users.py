from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str  # Bổ sung password cho user khi tạo

class UserOut(BaseModel):
    id: int
    username: str
    email: str

class TokenData(BaseModel):
    username: Optional[str] = None
