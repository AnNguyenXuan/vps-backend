from __future__ import annotations

from fastapi import APIRouter, HTTPException, status, UploadFile, File

from app.service.s3_service import S3Service
from app.schema.s3_schema import (
    S3StatusResponse,
    S3CreateResponse,
    S3ImportResponse,
    S3BucketInfo,
    GenerateKeyRequest, GeneratedKeyfile
)
from app.core.security import user_context, authorization


router = APIRouter(prefix="/s3", tags=["S3 Storage"])
s3_service = S3Service()


@router.get("/test")
async def s3_status_debug():
    print("[/s3/status-debug] HIT", flush=True)
    return {"ok": True}

@router.get("/status", response_model=S3StatusResponse, status_code=status.HTTP_200_OK)
async def check_s3_status():
    """
    Kiểm tra xem user hiện tại đã có tài khoản S3 chưa.
    """
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")

    if not await authorization.check_permission(user_current, "view_s3_status"):
        raise HTTPException(status_code=403, detail="You have no access to this resource")

    account = await s3_service.get_account_by_user(user_current.id)
    # account = await s3_service.get_account_by_user(user_current.id)
    return {"exists": bool(account)}

@router.post("/generate-key", response_model=GeneratedKeyfile, status_code=status.HTTP_201_CREATED)
async def generate_key(req: GenerateKeyRequest):
    try:
        payload = S3Service.generate_keys_and_pack(req.placement)
        return payload  # client có thể tự tải xuống file .json
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generate key failed: {e}")

@router.post("/import-keys", response_model=S3ImportResponse, status_code=status.HTTP_200_OK)
async def import_s3_keys(file: UploadFile = File(...)):
    """
    Import file key (.json) để kết nối với dịch vụ S3 hiện có.
    Hỗ trợ 2 biến thể:
      - endpoint, access_key, secret_key
    """
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")

    if not await authorization.check_permission(user_current, "import_s3_keys"):
        raise HTTPException(status_code=403, detail="You have no access to this resource")

    content = await file.read()
    result = await s3_service.import_key_file(user_current, content)
    return result


@router.get("/buckets", response_model=list[S3BucketInfo], status_code=status.HTTP_200_OK)
async def list_s3_buckets():
    """
    Liệt kê danh sách bucket S3 mà user hiện tại đang quản lý.
    Bao gồm số lượng object và tổng dung lượng (paginator > 1,000 objects).
    """
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")

    if not await authorization.check_permission(user_current, "view_s3_buckets"):
        raise HTTPException(status_code=403, detail="You have no access to this resource")

    try:
        data = await s3_service.list_buckets(user_current.id)
        return data
    except HTTPException as e:
        print("BUCKETS 403 DETAIL:", e.detail) 
        raise


@router.post("/create", response_model=S3CreateResponse, status_code=status.HTTP_201_CREATED)
async def create_s3_account():
    """
    Tạo mới dịch vụ lưu trữ S3 cho người dùng hiện tại.
    """
    user_current = user_context.get()
    if not user_current:
        raise HTTPException(status_code=401, detail="You have not logged in")

    if not await authorization.check_permission(user_current, "create_s3_account"):
        raise HTTPException(status_code=403, detail="You have no access to this resource")

    result = await s3_service.create_account(user_current)
    return result


