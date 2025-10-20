# app/schema/bucket_schema.py
from __future__ import annotations

import re
from typing import Optional, List
from pydantic import BaseModel, Field, validator


# ---------------------------
# Common sub-schemas
# ---------------------------

class RateLimit(BaseModel):
    rps: int = Field(..., ge=1, description="Requests per second")
    burst: int = Field(..., ge=1, description="Burst size")


# ---------------------------
# Request models
# ---------------------------

class BucketCreateRequest(BaseModel):
    # FE gửi camelCase; BE dùng snake_case + alias để nhận/trả đúng format
    bucket_name: str = Field(..., alias="bucketName", min_length=3, max_length=63)
    capacity_mb: int = Field(..., alias="capacityMB", ge=1, description="Quota cho bucket (MB)")
    storage_class: str = Field("standard", alias="storageClass", description="Tên hiển thị, map sang placement phía RGW/policy")
    rate_limit: Optional[RateLimit] = Field(None, alias="rateLimit")

    # Chuẩn hoá & kiểm tra tên bucket theo quy ước S3
    @validator("bucket_name")
    def validate_bucket_name(cls, v: str) -> str:
        name = v.strip().lower()

        # 1) độ dài: đã ràng buộc bằng Field, vẫn check lại cho rõ nghĩa
        if not (3 <= len(name) <= 63):
            raise ValueError("bucketName must be 3-63 characters")

        # 2) pattern cơ bản: chữ thường, số, dấu chấm, dấu gạch ngang; bắt đầu & kết thúc bằng chữ/số
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]{1,61})[a-z0-9]", name):
            raise ValueError("bucketName may contain lowercase letters, numbers, dots, and hyphens; must start/end with letter or number")

        # 3) không cho phép '..'
        if ".." in name:
            raise ValueError("bucketName must not contain consecutive periods")

        # 4) không được giống IPv4
        if re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", name):
            raise ValueError("bucketName must not be formatted like an IP address")

        return name

    class Config:
        allow_population_by_field_name = True


# ---------------------------
# Response models
# ---------------------------

class BucketInfo(BaseModel):
    # Thông tin tối thiểu để hiển thị ở danh sách
    name: str
    region: Optional[str] = None
    endpoint: Optional[str] = None
    storage_class: Optional[str] = Field(None, alias="storageClass")
    quota_mb: Optional[int] = Field(None, alias="quotaMB")
    object_count: Optional[int] = Field(None, alias="objectCount")
    size_bytes: Optional[int] = Field(None, alias="sizeBytes")
    updated_at: Optional[str] = Field(None, alias="updatedAt")  # ISO8601 nếu có

    class Config:
        allow_population_by_field_name = True


class BucketSummary(BaseModel):
    name: str
    endpoint: str
    region: str
    storage_class: Optional[str] = Field(None, alias="storageClass")
    quota_mb: Optional[int] = Field(None, alias="quotaMB")

    class Config:
        allow_population_by_field_name = True


class AccountSummary(BaseModel):
    already_existed: bool = Field(..., alias="alreadyExisted")

    class Config:
        allow_population_by_field_name = True


class BucketCreateResponse(BaseModel):
    created: bool
    bucket: BucketSummary
    account: AccountSummary

    class Config:
        allow_population_by_field_name = True
