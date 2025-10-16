# Kiến trúc backend

Được thiết kế dựa trên mô hình MVC, chia thành các lớp tương tác dữ liệu khác nhau, xử lý theo thứ tự các luồng.

---
# Cấu trúc 
```
app/
├── controller/       # Các API endpoint (controllers) xử lý request/response.
├── core/             # Các module cốt lõi: cấu hình, database, CLI (cmd.py), security, exception và utils.
├── model/            # Các model SQLAlchemy định nghĩa cấu trúc bảng.
├── repository/       # Lớp truy cập dữ liệu, quản lý kết nối với database.
├── schema/           # Các Pydantic schema dùng để validate và serialize dữ liệu.
└── service/          # Lớp business logic xử lý nghiệp vụ: authentication, authorization, và các thao tác domain.
```
---
# Cấu trúc lớp controller

Khởi tạo các router, mỗi khi xây 1 lớp router mới, cần khai báo router đó vào hàm **app/controller/__init__.py**

Ví dụ như dưới đây : 
```
from .category_controller import router as category_router
from .group_controller import router as group_router
from .group_member_controller import router as group_member_router
from .group_permission_controller import router as group_permission_router
from .permission_controller import router as permission_router
# from .product_controller import router as product_router
from .user_controller import router as user_router
from .user_permission_controller import router as user_permission_router
from .security_controller import router as security_router
from .s3_controller import router as s3_router

routers = [
    security_router,
    category_router,
    group_router,
    group_member_router,
    group_permission_router,
    permission_router,
    # product_router,
    user_router,
    s3_router,
    user_permission_router,
]
```

Các endpoint API của mỗi dịch vụ được định nghĩa theo cấu trúc <tên_dịch_vụ>_controller.py

