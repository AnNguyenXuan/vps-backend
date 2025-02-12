from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated

class LoginRequest(BaseModel):
    username: Annotated[
        str,
        StringConstraints(min_length=3, max_length=20, strip_whitespace=True)
    ] = Field(..., example="superadmin")
    password: Annotated[
        str,
        StringConstraints(min_length=6, max_length=18)
    ] = Field(..., example="123456")

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "superadmin",
                "password": "123456"
            }
        }
    }


# TokenResponse thay thế cho LoginResponse để phù hợp với controller
class TokenResponse(BaseModel):
    accessToken: str = Field(
        ...,
        example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    )
    refreshToken: str = Field(
        ...,
        example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }
    }


class ChangePasswordRequest(BaseModel):
    currentPassword: str = Field(..., example="123456")
    newPassword: str = Field(..., example="NewStrongP@ss1")

    model_config = {
        "json_schema_extra": {
            "example": {
                "currentPassword": "123456",
                "newPassword": "NewStrongP@ss1"
            }
        }
    }


class VerifyPasswordRequest(BaseModel):
    password: str = Field(..., example="123456")

    model_config = {
        "json_schema_extra": {
            "example": {
                "password": "123456"
            }
        }
    }


class RefreshTokenRequest(BaseModel):
    refreshToken: str = Field(
        ...,
        example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }
    }


class AccessTokenResponse(BaseModel):
    accessToken: str = Field(
        ...,
        example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }
    }


class RefreshTokenResponse(BaseModel):
    refreshToken: str = Field(
        ...,
        example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }
    }
