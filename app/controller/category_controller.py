from fastapi import APIRouter, HTTPException, Request, status
from typing import List
from app.schema.category_schema import CategoryCreate, CategoryRead, CategoryUpdate
from app.service.category_service import CategoryService
# from app.service.authorization_service import AuthorizationService  # Bạn cần tự cài đặt nếu chưa có
# from app.validators.category_validator import CategoryValidator  # Bạn cần tự cài đặt nếu chưa có

# Khởi tạo các service cần thiết
category_service = CategoryService()
# authorization_service = AuthorizationService()
# category_validator = CategoryValidator()

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryRead])
async def list_categories():
    """
    Lấy danh sách tất cả danh mục.
    """
    categories = await category_service.get_all_categories()
    # Nếu cần chuyển đổi sang DTO (CategoryRead) bạn có thể làm:
    # category_dtos = [CategoryRead.from_orm(cat) for cat in categories]
    # return category_dtos
    return categories


@router.get("/{id}", response_model=CategoryRead)
async def get_category(id: int):
    """
    Lấy chi tiết danh mục theo id.
    """
    # Phương thức get_category_by_id của service đã raise HTTPException nếu không tìm thấy
    category = await category_service.get_category_by_id(id)
    return category


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(request: Request):
    """
    Tạo danh mục mới.
    Yêu cầu phải có thông tin người dùng (đã được attach vào request.state.user).
    """
    # Lấy thông tin user từ request (bạn cần đảm bảo middleware hoặc dependency gán user vào request.state)
    user = getattr(request.state, "user", None)
    if not user:
        # E2025: không tìm thấy thông tin user
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "create_category"):
    #     raise HTTPException(status_code=403, detail="E2021")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # # Validate dữ liệu theo hành động 'create'
    # validated_data: CategoryCreate = category_validator.validate_category_data(data, "create")
    try:
        category = await category_service.create_category(data) #create_category(validated_data)
        return category
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{id}", response_model=CategoryRead)
async def update_category(id: int, request: Request):
    """
    Cập nhật danh mục.
    Yêu cầu user phải tồn tại và có quyền "edit_category", đồng thời (theo logic PHP) user.id phải trùng với id.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # # Kiểm tra quyền: truyền thêm id nếu cần thiết
    # if not authorization_service.check_permission(user, "edit_category", id) or getattr(user, "id", None) != id:
    #     raise HTTPException(status_code=403, detail="E2021")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Validate dữ liệu theo hành động 'update'
    # validated_data: CategoryUpdate = category_validator.validate_category_data(data, "update")
    try:
        category = await category_service.update_category(id, data) #.update_category(id, validated_data)
        return category
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_category(id: int, request: Request):
    """
    Xóa danh mục.
    Yêu cầu user phải tồn tại và có quyền "delete_category".
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="E2025")
    # if not authorization_service.check_permission(user, "delete_category"):
    #     raise HTTPException(status_code=403, detail="E2021")

    try:
        await category_service.delete_category(id)
        return {"message": "Category deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}/subcategories", response_model=List[CategoryRead])
async def get_subcategories(id: int):
    """
    Lấy danh sách danh mục con của danh mục có id cho trước.
    """
    # Kiểm tra danh mục cha có tồn tại không (service sẽ raise 404 nếu không tìm thấy)
    await category_service.get_category_by_id(id)
    subcategories = await category_service.get_subcategories_by_parent_id(id)
    # Nếu cần chuyển đổi sang DTO, tương tự như list_categories
    return subcategories
