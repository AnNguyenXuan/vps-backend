from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict

import boto3
from fastapi import HTTPException, status

from app.repository.s3_repository import S3Repository
from app.core.crypto import decrypt
from app.core import config
from .s3_admin_service import S3AdminService

from datetime import timezone

import secrets, string

from starlette.concurrency import run_in_threadpool

from botocore.config import Config
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError


ALLOWED_PLACEMENTS = {"hdd", "ssd"}

def _rand_access_key(n: int = 20) -> str:
    # A-Z0-9
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))

def _rand_secret_key(n: int = 40) -> str:
    # a-zA-Z0-9
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))


class S3Service:
    """
    Service nghiệp vụ dùng bởi controller:
      - create_account(user): ensure RGW user/key qua S3AdminService, rồi lưu DB
      - import_key_file(user, file_bytes): lưu/ghi đè credential
      - list_buckets(user_id): liệt kê bucket + thống kê
      - get_account_by_user(user_id): lấy record từ DB

    KHÔNG import schema; trả dict đúng shape để controller serialize bằng response_model.
    """

    def __init__(self, admin_service: S3AdminService | None = None):
        self.repository = S3Repository()
        # Dùng trực tiếp giá trị đã cấu hình
        self.data_endpoint = config.CEPH_PUBLIC_ENDPOINT
        self.key_type = config.CEPH_KEY_TYPE
        self.region = config.CEPH_REGION
        if not (self.data_endpoint and self.region):
            raise RuntimeError("Missing CEPH_PUBLIC_ENDPOINT or CEPH_REGION in configuration.")

        # Admin service (DI-friendly), mặc định đọc config trực tiếp
        self.admin = admin_service or S3AdminService()

    # -------------------- Public methods (controller dùng) --------------------
    async def get_account_by_user(self, user_id: int):
        account = await self.repository.find_by_user(user_id)
        if not account or not getattr(account, "is_active", True):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="S3 account not found or inactive",
            )
        return account

    @staticmethod
    def generate_keys_and_pack(placement: str) -> dict:
        placement = str(placement).lower()
        if placement not in ALLOWED_PLACEMENTS:
            raise ValueError("placement must be 'hdd' or 'ssd'")
        ak = _rand_access_key()
        sk = _rand_secret_key()

        return {
            "access_key": ak,
            "secret_key": sk,
            "default_placement": placement,
        }

    async def import_key_file(self, user, file_bytes: bytes):
        """
        Nhận file JSON:
          - endpoint, access_key, secret_key
        Lưu vào DB rồi trả dict.
        """
        try:
            data = json.loads(file_bytes)
            access_key = data.get("access_key")
            secret_key = data.get("secret_key")
            placement = data.get("default_placement")
            if not (access_key and secret_key):
                raise ValueError("missing fields")
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid key file format")

        uid = f"user-{user.id}"
        display_name = f"user-{user.id}-{access_key}"
        key_type = self.key_type
        print(data, uid, display_name)
        try:
            account = await run_in_threadpool (
                self.admin.create_user,
                uid=uid,
                display_name=display_name,
                key_type=key_type,
                access_key=access_key,
                secret_key=secret_key,
                #default_placement=placement,
            )
        except RuntimeError as e:
            raise HTTPException(status_code=502, detail=str(e))

        await self.repository.create_or_update(
            user_id=user.id,
            endpoint=self.data_endpoint,
            access_key=access_key,
            secret_key=secret_key,
            placement_type=placement,
        )

        return {
            "success": True,
            "message": "Imported S3 credentials successfully",
            "normalized": {
                "endpoint": self.data_endpoint,
                "access_key": access_key,
                "secret_key": secret_key,
                "default-placement": placement,
                "region": self.region,
            },
        }

    async def list_buckets(self, user_id: int) -> list[dict]:
        """
        Liệt kê bucket + đếm object & tổng dung lượng.
        Trả list[dict] theo shape S3BucketInfo.
        """
        account = await self.repository.find_by_user(user_id)
        access_key = decrypt(account.access_key)
        print(access_key)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No S3 account found")

        try:
            cfg = Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},  # quan trọng khi endpoint là IP/host nội bộ
                retries={"max_attempts": 3, "mode": "standard"},
                connect_timeout=3,
                read_timeout=10,
            )

            s3 = boto3.client(
                "s3",
                aws_access_key_id=decrypt(account.access_key),
                aws_secret_access_key=decrypt(account.secret_key),
                endpoint_url=account.endpoint.rstrip("/"),
                region_name=(getattr(self, "region", None) or "us-east-1"),
                config=cfg,
                # verify=False,  # bật nếu đang test HTTPS tự ký
            )

            resp = s3.list_buckets()
            buckets = resp.get("Buckets", []) or []

        except EndpointConnectionError as e:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Endpoint not reachable: {e}")
        except NoCredentialsError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing S3 credentials")
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            msg = e.response.get("Error", {}).get("Message")
            http_status = e.response.get("ResponseMetadata", {}).get("HTTPStatusCode") or status.HTTP_502_BAD_GATEWAY
            raise HTTPException(http_status, f"S3 error {code}: {msg}")
        except Exception as e:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Cannot connect to S3 endpoint: {e}")

        results: list[dict] = []
        paginator = s3.get_paginator("list_objects_v2")

        for b in buckets:
            name = b["Name"]
            created_at = b.get("CreationDate")
            key_count = 0
            total_size = 0

            try:
                for page in paginator.paginate(Bucket=name):
                    for obj in (page.get("Contents") or []):
                        key_count += 1
                        total_size += obj.get("Size", 0)
            except ClientError:
                # bucket vừa bị xoá/không đủ quyền → bỏ qua
                continue

            results.append({
                "name": name,
                "object_count": key_count,
                "size_bytes": total_size,
                "created_at": (created_at and created_at.astimezone(timezone.utc).isoformat()),
                "owner": None,
            })

        return results