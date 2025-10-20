from app.repository.bucket_repository import BucketAccountRepository
from app.core.crypto import encrypt, decrypt
from app.core import config
from app.core.utils import CephAdminClient
import boto3
from botocore.config import Config
from fastapi import HTTPException

class BucketService:
    def __init__(self):
        self.repo = BucketAccountRepository()
        self.admin = CephAdminClient(
            endpoint=config.CEPH_ADMIN_ENDPOINT,
            access_key=config.CEPH_ADMIN_ACCESS_KEY,
            secret_key=config.CEPH_ADMIN_SECRET_KEY,
        )

    async def _ensure_account(self, user_id: int):
        acct = await self.repo.get_by_user(user_id)
        if acct:
            return acct
        # Tạo user RGW qua Admin Ops → lấy key
        rgw_user = self.admin.ensure_user(user_id=str(user_id))
        access = rgw_user["keys"][0]["access_key"]
        secret = rgw_user["keys"][0]["secret_key"]
        return await self.repo.upsert(user_id, encrypt(access), encrypt(secret))

    def _client_for(self, acct):
        cfg = Config(signature_version="s3v4", s3={"addressing_style":"path"})
        return boto3.client(
            "s3",
            aws_access_key_id=decrypt(acct.access_key_enc),
            aws_secret_access_key=decrypt(acct.secret_key_enc),
            endpoint_url=config.CEPH_PUBLIC_ENDPOINT,
            region_name=config.CEPH_REGION,
            config=cfg
        )

    async def create_bucket_for_user(self, user_id: int, req):
        acct = await self._ensure_account(user_id)
        s3 = self._client_for(acct)

        # 1) create bucket (idempotent)
        try:
            s3.create_bucket(
                Bucket=req.bucketName,
                CreateBucketConfiguration={"LocationConstraint": config.CEPH_REGION}
            )
        except s3.exceptions.BucketAlreadyOwnedByYou:
            pass
        except s3.exceptions.BucketAlreadyExists as e:
            raise HTTPException(status_code=409, detail="Bucket name already exists") from e

        # 2) quota + metadata đều set TRỰC TIẾP trên Ceph
        self.admin.set_bucket_quota(uid=str(user_id),
                                    bucket=req.bucketName,
                                    max_size_kb=req.capacityMB * 1024)

        # (tuỳ chọn) gắn tag để lần sau FE đọc lại nhanh bằng S3
        if req.storageClass or req.capacityMB:
            s3.put_bucket_tagging(
                Bucket=req.bucketName,
                Tagging={"TagSet":[
                    {"Key":"storageClass","Value":req.storageClass or "standard"},
                    {"Key":"quotaMB","Value":str(req.capacityMB)}
                ]}
            )

        # (tuỳ chọn) rate-limit: lưu ở tags hoặc Redis/DB khác nếu cần áp vào Nginx/Envoy
        # self.admin.set_ratelimit(...)

        return {
            "created": True,
            "bucket": {
                "name": req.bucketName,
                "endpoint": config.CEPH_PUBLIC_ENDPOINT,
                "region": config.CEPH_REGION
            },
            "account": {
                "alreadyExisted": True  # hoặc False nếu vừa tạo
            }
        }

    async def list_buckets(self, user_id: int):
        acct = await self._ensure_account(user_id)
        s3 = self._client_for(acct)

        resp = s3.list_buckets()  # các bucket "OwnedByYou"
        buckets = []
        for b in resp.get("Buckets", []):
            name = b["Name"]
            item = {"name": name, "region": config.CEPH_REGION}
            # (nhanh) lấy tag nếu có
            try:
                t = s3.get_bucket_tagging(Bucket=name)
                tags = {kv["Key"]: kv["Value"] for kv in t.get("TagSet", [])}
                if "storageClass" in tags: item["storageClass"] = tags["storageClass"]
                if "quotaMB" in tags: item["quotaMB"] = int(tags["quotaMB"])
            except s3.exceptions.from_code("NoSuchTagSet"):
                pass
            # (nếu cần) số liệu usage/quota chuẩn: Admin Ops /admin/bucket?bucket=...&uid=...&stats=true
            # stats = self.admin.get_bucket_stats(uid=str(user_id), bucket=name)
            buckets.append(item)
        return buckets
