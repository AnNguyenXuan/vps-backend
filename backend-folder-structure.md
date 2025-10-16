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
# Cấu trúc mẫu lớp 