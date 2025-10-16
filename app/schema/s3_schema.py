from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, List,  Literal, Annotated

from pydantic import BaseModel, Field, StringConstraints


class S3StatusResponse(BaseModel):
    exists: bool

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {"example": {"exists": True}}
    }

class GenerateKeyRequest(BaseModel):
    placement: Literal["hdd", "ssd"] = Field(..., description="Đích lưu trữ mặc định của keyfile")


class GeneratedKeyfile(BaseModel):
    access_key: Annotated[str, StringConstraints(min_length=3, max_length=200, strip_whitespace=True)]
    secret_key: Annotated[str, StringConstraints(min_length=3, max_length=200, strip_whitespace=True)]
    default_placement: Literal["hdd", "ssd"]

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "access_key": "AKIAEXAMPLE",
                "secret_key": "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY",
                "default_placement": "ssd",
            }
        },
    }

class S3ImportResponse(BaseModel):
    success: bool
    message: Annotated[str, StringConstraints(max_length=500)] | None = None
    normalized: Dict[str, Any] | None = Field(
        default=None,
        description="access_key, secret_key, default_placement"
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Imported S3 credentials successfully",
                "normalized": {
                    "access_key": "AKIAEXAMPLE",
                    "secret_key": "SECRETKEY",
                    "default_placement" : "ssd"
                }
            }
        }
    }


class S3CreateResponse(BaseModel):
    account_id: int
    username: Annotated[str, StringConstraints(min_length=1, max_length=200, strip_whitespace=True)]
    keyfile: GeneratedKeyfile
    download_filename: Annotated[str, StringConstraints(min_length=1, max_length=255, strip_whitespace=True)] = "s3-credentials.json"
    note: Annotated[str, StringConstraints(min_length=1, max_length=500)] | None = Field(
        default="Giữ bí mật secret key; chỉ hiển thị 1 lần."
    )

    model_config = {
        "from_attributes": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
        "json_schema_extra": {
            "example": {
                "account_id": 12,
                "username": "user-42",
                "keyfile": {
                    "version": 1,
                    "endpoint": "https://s3.click",
                    "access_key": "AKIAEXAMPLE",
                    "secret_key": "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY",
                    "region": "us-east-1",
                    "generated_at": "2025-10-08T12:00:00Z"
                },
                "download_filename": "s3-credentials.json",
                "note": "Giữ bí mật secret key; chỉ hiển thị 1 lần."
            }
        }
    }



class S3BucketInfo(BaseModel):
    name: Annotated[str, StringConstraints(min_length=3, max_length=255, strip_whitespace=True)]
    object_count: int = Field(0, ge=0)
    size_bytes: int = Field(0, ge=0)
    created_at: datetime | None = None
    owner: Annotated[str, StringConstraints(min_length=1, max_length=255, strip_whitespace=True)] | None = None

    model_config = {
        "from_attributes": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
        "json_schema_extra": {
            "example": {
                "name": "photos",
                "object_count": 1287,
                "size_bytes": 987654321,
                "created_at": "2025-10-01T09:30:00Z",
                "owner": None
            }
        }
    }


__all__ = [
    "S3StatusResponse",
    "S3CreateResponse",
    "S3ImportResponse",
    "S3BucketInfo",
    "S3KeyFile",
]
