from pydantic import BaseModel, EmailStr, field_validator, StringConstraints
from typing_extensions import Annotated
import re
from datetime import datetime


class UserBase(BaseModel):
    username: Annotated[
        str, 
        StringConstraints(
            min_length=3, 
            max_length=20, 
            strip_whitespace=True
        )
    ]
    email: EmailStr
    phone: Annotated[
        str, 
        StringConstraints(min_length=10, max_length=15, pattern=r"^[0-9]+$")
    ] | None = None
    address: Annotated[str, StringConstraints(max_length=255)] | None = None
    is_active: bool = True

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        """
        - Chỉ chứa chữ cái, số và dấu gạch dưới (_)
        - Không bắt đầu hoặc kết thúc bằng dấu gạch dưới
        """
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError("Username chỉ được chứa chữ cái, số và dấu gạch dưới (_)")
        if value.startswith("_") or value.endswith("_"):
            raise ValueError("Username không được bắt đầu hoặc kết thúc bằng dấu gạch dưới (_)")
        return value


class UserCreate(UserBase):
    password: Annotated[str, StringConstraints(min_length=6, max_length=18)]

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        """
        - Mật khẩu từ 6-18 ký tự.
        - Phải chứa ít nhất 1 chữ hoa, 1 chữ thường, 1 số và 1 ký tự đặc biệt.
        - Không chứa khoảng trắng.
        """
        if " " in value:
            raise ValueError("Mật khẩu không được chứa khoảng trắng")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ cái viết hoa")
        if not re.search(r"[a-z]", value):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ cái viết thường")
        if not re.search(r"\d", value):
            raise ValueError("Mật khẩu phải chứa ít nhất một số")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Mật khẩu phải chứa ít nhất một ký tự đặc biệt")
        return value

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "phone": "0987654321",
                "address": "123 Đường ABC, Quận 1, TP.HCM",
                "is_active": True,
                "password": "StrongP@ss1"
            }
        }
    }


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
        "json_schema_extra": {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john.doe@example.com",
                "phone": "0987654321",
                "address": "123 Đường ABC, Quận 1, TP.HCM",
                "is_active": True,
                "created_at": "2025-01-01T12:00:00",
                "updated_at": "2025-02-01T12:00:00"
            }
        }
    }


class UserUpdate(UserBase):
    password: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if value:  # Chỉ kiểm tra nếu có giá trị mới
            if " " in value:
                raise ValueError("Mật khẩu không được chứa khoảng trắng")
            if not re.search(r"[A-Z]", value):
                raise ValueError("Mật khẩu phải chứa ít nhất một chữ cái viết hoa")
            if not re.search(r"[a-z]", value):
                raise ValueError("Mật khẩu phải chứa ít nhất một chữ cái viết thường")
            if not re.search(r"\d", value):
                raise ValueError("Mật khẩu phải chứa ít nhất một số")
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
                raise ValueError("Mật khẩu phải chứa ít nhất một ký tự đặc biệt")
        return value

    model_config = {
        "from_attributes": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
        "json_schema_extra": {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "phone": "0987654321",
                "address": "123 Đường ABC, Quận 1, TP.HCM",
                "is_active": True,
                "password": "NewStrongP@ss1"
            }
        }
    }
