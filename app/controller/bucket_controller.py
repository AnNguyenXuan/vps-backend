# app/controller/bucket_controller.py
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.core.security import user_context, authorization
from app.service.bucket_service import BucketService
from app.schema.bucket_schema import (
    BucketCreateRequest, 
    BucketCreateResponse,  
    BucketInfo             
)

router = APIRouter(prefix="/bucket", tags=["Object Storage"])
service = BucketService()

# GET /bucket/buckets -> liệt kê bucket người dùng đang sở hữu
@router.get("/buckets", response_model=list[BucketInfo], status_code=status.HTTP_200_OK)
async def list_buckets(
    stats: bool = Query(False, description="Lấy thêm thống kê chi tiết (gọi Admin Ops, chậm hơn)"),
    _=Depends(authorization.require_user)  # đảm bảo đã đăng nhập
):
    user = user_context.get()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Nếu stats=True, service có thể gọi Admin Ops để lấy usage/quota chính xác
    return await service.list_buckets(user.id, with_stats=stats)

# POST /bucket/buckets -> tạo bucket (nếu chưa có user trên RGW thì auto tạo rồi mới tạo bucket)
@router.post("/buckets", response_model=BucketCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_bucket(
    req: BucketCreateRequest,
    _=Depends(authorization.require_user)
):
    user = user_context.get()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await service.create_bucket_for_user(user.id, req)
