from fastapi import APIRouter, HTTPException, Request, status, Query
from typing import List
from app.service.product_service import ProductService
# from app.service.authorization_service import AuthorizationService
# from app.exception import AppException
from app.schema.product_schema import ProductDto, ProductOptionDto

router = APIRouter(prefix="/api/products", tags=["Product"])

product_service = ProductService()
# authorization_service = AuthorizationService()


@router.get("", response_model=List[ProductDto])
async def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1)
):
    """
    Lấy danh sách sản phẩm theo phân trang.

    Nếu `page` hoặc `limit` không hợp lệ, sẽ trả về lỗi 400.
    """
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid pagination parameters")
    products = await product_service.get_paginated_product_dtos(page, limit)
    return products


@router.get("/{id}", response_model=ProductDto)
async def detail_product(id: int):
    """
    Lấy thông tin chi tiết sản phẩm theo ID.

    Nếu không tìm thấy sản phẩm, trả về lỗi 404.
    """
    try:
        product = await product_service.get_product_dto_by_id(id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=ProductDto, status_code=status.HTTP_201_CREATED)
async def create_product(request: Request):
    """
    Tạo sản phẩm mới.

    Yêu cầu:
      - Thông tin người dùng có trong `request.state.user`.
      - Người dùng có quyền "create_product".
      - Payload JSON chứa các thông tin cần thiết.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "create_product"):
    #     raise HTTPException(status_code=403, detail="E2021")
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    try:
        product = await product_service.create_product(data)
        return product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{id}", response_model=ProductDto)
async def update_product(request: Request, id: int):
    """
    Cập nhật thông tin sản phẩm.

    Yêu cầu:
      - Thông tin user có trong `request.state.user`.
      - Người dùng có quyền "edit_product" cho sản phẩm có ID được chỉ định.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "edit_product", id):
    #     raise HTTPException(status_code=403, detail="E2021")
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    try:
        product = await product_service.update_product(id, data)
        return product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}")
async def delete_product(id: int, request: Request):
    """
    Xóa sản phẩm (soft-delete).

    Yêu cầu:
      - Thông tin user có trong `request.state.user`.
      - Người dùng có quyền "delete_product".
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "delete_product"):
    #     raise HTTPException(status_code=403, detail="E2021")
    try:
        await product_service.delete_product(id)
        return {"message": "Product deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/by-category/{categoryId}", response_model=List[ProductDto])
async def get_products_by_category(categoryId: int):
    """
    Lấy danh sách sản phẩm theo category ID.

    Nếu không tìm thấy sản phẩm nào, trả về lỗi 404.
    """
    products = await product_service.getProductsByCategoryId(categoryId)
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this category")
    return products


@router.api_route("/{id}/attribute", methods=["POST", "PUT"])
async def update_attributes(request: Request, id: int):
    """
    Cập nhật hoặc tạo mới các thuộc tính và tùy chọn của sản phẩm.

    Yêu cầu:
      - Thông tin user có trong `request.state.user`.
      - Người dùng có quyền "edit_product" cho sản phẩm đó.
      - Payload JSON chứa các thuộc tính cần cập nhật.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "edit_product", id):
    #     raise HTTPException(status_code=403, detail="E2021")
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    try:
        await product_service.update_or_create_product_attributes_and_options(id, data)
        return {"message": "Attributes and options updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{id}/find-option", response_model=ProductOptionDto)
async def find_option(request: Request, id: int):
    """
    Tìm tùy chọn của sản phẩm dựa trên chuỗi JSON mô tả các thuộc tính.

    Nếu không tìm thấy sản phẩm hoặc tùy chọn không phù hợp, trả về lỗi tương ứng.
    """
    try:
        # Lấy toàn bộ nội dung request dưới dạng bytes và chuyển thành chuỗi UTF-8
        json_bytes = await request.body()
        json_string = json_bytes.decode("utf-8")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    try:
        product = await product_service.get_product_by_id(id)
    except Exception:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        product_option = await product_service.find_product_option_by_json(product, json_string)
        return product_option
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}/option-default")
async def get_option_default(id: int):
    """
    Lấy tùy chọn mặc định của sản phẩm theo ID.

    Nếu không tìm thấy sản phẩm, trả về lỗi 404.
    """
    try:
        product = await product_service.get_product_by_id(id)
    except Exception:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        product_option_default = await product_service.getOptionDefault(product)
        return product_option_default
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/options/{optionId}")
async def get_option_values(optionId: int):
    """
    Lấy các giá trị cho tùy chọn sản phẩm theo option ID.

    Nếu không tìm thấy giá trị nào, trả về lỗi 404.
    """
    try:
        values = await product_service.getValuesByOptionId(optionId)
        if not values:
            raise HTTPException(status_code=404, detail="No values found for the given option ID")
        return values
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
