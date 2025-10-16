# Web Bán Hàng (FastAPI Backend)

**Version:** 0.0.1  
**Author:** [Nguyễn Hữu Thắng]  
**Date:** [17/2/2025]

---

## Giới thiệu

Đây là phiên bản backend được chuyển từ project PHP/Symfony ban đầu sang FastAPI. Mục đích chính của dự án này là học hỏi và làm quen với FastAPI cũng như kiến trúc hiện đại trong phát triển ứng dụng web. Dự án ban đầu được phát triển trong khuôn khổ môn học “Phát triển ứng dụng web” bằng PHP (Symfony) và có phần frontend được xây dựng bằng React.

**Lưu ý:**

- Dự án đang trong giai đoạn chuyển đổi; hiện tại chỉ một số module cơ bản đã được chuyển sang FastAPI.  
- Nhiều file và tính năng (được biểu thị bằng `...` trong cấu trúc thư mục) vẫn chưa được chuyển đổi. Khi có thời gian, tôi sẽ bổ sung và hoàn thiện thêm.
- Đối với mục đích học tập FastAPI, những file hiện có đã cung cấp đủ kiến thức cần thiết; các phần mở rộng chỉ nhằm hoàn thiện dự án khi triển khai thực tế.

---

## Tài nguyên tham khảo

- **Backend (PHP/Symfony):** [Shop Backend Repository](https://github.com/nguyen-huu-thang/shop-backend.git)
- **Frontend (React):** [Shop Frontend Repository](https://github.com/nguyen-huu-thang/shop-frontend.git)

---

## Yêu cầu hệ thống

- **Python:** Phiên bản 3.9 hoặc mới hơn. (tôi đang dùng Python 3.13.2)
- **FastAPI:** Framework chính của dự án.
- **SQLAlchemy (Async):** ORM cho các thao tác cơ sở dữ liệu.
- **Pydantic:** Dùng để xác thực và serialize dữ liệu.
- **Database:** PostgreSQL.
- **Các thư viện khác:** `python-jose` (JWT), `passlib` (hashing), `uvicorn` (ASGI server).

---

## Cấu trúc dự án

```
app/
├── controller/       # Các API endpoint (controllers) xử lý request/response.
├── core/             # Các module cốt lõi: cấu hình, database, CLI (cmd.py), security, exception và utils.
├── model/            # Các model SQLAlchemy định nghĩa cấu trúc bảng.
├── repository/       # Lớp truy cập dữ liệu, quản lý kết nối với database.
├── schema/           # Các Pydantic schema dùng để validate và serialize dữ liệu.
└── service/          # Lớp business logic xử lý nghiệp vụ: authentication, authorization, và các thao tác domain.
```

**Lưu ý:** Một số module được đánh dấu bằng `...` chưa được chuyển đổi từ PHP sang Python. Khi có thời gian, tôi sẽ bổ sung thêm các file tương ứng theo thiết kế ban đầu.

---

## Hướng dẫn cài đặt

### 1. Clone dự án từ GitHub

```bash
git clone https://github.com/nguyen-huu-thang/sample-fastAPI.git
cd sample-fastAPI
```

### 2. Tạo và kích hoạt Virtual Environment (Tùy chọn thêm nếu bạn muốn dùng Virtual Environment)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường

Tạo file `.env` ở thư mục gốc với nội dung tương tự:

```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/sample_fastapi

SECRET_KEY=your_secret_key

ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=60

JWT_SECRET=nNGw5zr...
JWT_ISSUER=https://example.com
JWT_AUDIENCE=https://shop.example.com

FERNET_KEY=twHSLK6K9pYq1YIf6XfhITS9s520l8UIA0uWKHht+NZSe0PHGHJzoTE8XbZmZ+9B

CEPH_ADMIN_ENDPOINT = "https://ceph-admin.yourdomain.com/admin"
CEPH_PUBLIC_ENDPOINT = "https://ceph-admin.yourdomain.com"
CEPH_REGION = "us-east-1"
CEPH_ADMIN_ACCESS_KEY = "admin-access"
CEPH_ADMIN_SECRET_KEY = "admin-secret"
```
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"


### 5. Khởi tạo hệ thống nhanh với `init_all`

Bạn có thể sử dụng lệnh sau để thực hiện toàn bộ quá trình khởi tạo hệ thống:

```bash
python app/core/cmd init_all
```

Lệnh này sẽ:

1. Khởi tạo database.
2. Tạo superadmin (nếu chưa tồn tại).
3. Đồng bộ quyền tĩnh vào DB.
4. Cấp toàn bộ quyền cho superadmin.

### 6. Chạy server phát triển

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Truy cập ứng dụng tại: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Một số điểm đặc biệt

### Quản lý Session và Repository

- **Không sử dụng `Depends(get_db)` trong controller:**  
  Việc quản lý kết nối cơ sở dữ liệu được thực hiện trong repository thông qua các context manager (`async with AsyncSessionLocal() as session`). Điều này giữ cho controller "sạch" và tập trung vào xử lý request/response, đồng thời đảm bảo việc quản lý session được thực hiện chặt chẽ và tập trung.

- **Sử dụng user_context để lưu thông tin người dùng hiện tại:**  
  Thay vì phải truyền thông tin người dùng qua các tầng hoặc đối số hàm, sử dụng user_context để lưu thông tin người dùng đang đăng nhập. Điều này giúp việc truy cập vào dữ liệu người dùng trở nên đơn giản và không phụ thuộc vào việc truyền tham số, đồng thời đảm bảo rằng ở mọi tầng của ứng dụng, thông tin người dùng có thể được truy cập một cách dễ dàng và an toàn mà không làm giảm tính rõ ràng của code.
  
### Bảo mật và phân quyền

- **Xác thực bằng JWT:**  
  Sử dụng JWT để xác thực người dùng với các claim quan trọng như `iss`, `aud`, `iat`, `exp`, `jti` và `refreshId`.
- **Phân quyền linh hoạt:**  
  Kiểm tra quyền của người dùng thông qua các service riêng biệt (`AuthorizationService`, `UserPermissionService`, `GroupPermissionService`), giúp xác định quyền truy cập dựa trên cả người dùng và nhóm.
- **Token Management:**  
  Refresh token, token rotation và token blacklist được quản lý riêng biệt nhằm đảm bảo an toàn khi người dùng đăng nhập, đăng xuất và làm mới token.

### Các tính năng có thể phát triển thêm

- **Caching quyền truy cập:**  
  Triển khai cache (ví dụ: sử dụng Redis) cho kết quả truy vấn quyền trong một khoảng thời gian ngắn nhằm giảm số lần truy vấn đến DB.
- **Migrations chuyên nghiệp:**  
  Khi dự án chuyển sang môi trường production, chuyển từ `Base.metadata.create_all` sang Alembic để quản lý migrations an toàn và có lịch sử thay đổi.
- **Xử lý Exception nâng cao:**  
  Tạo module chuyên dụng để xử lý Exception, trả về mã lỗi chi tiết (code lỗi riêng biệt ngoài mã HTTP) giúp dễ dàng debug và giám sát.
- **Rate Limiting và Monitoring:**  
  Tích hợp các giải pháp giới hạn tốc độ và hệ thống logging, monitoring để tăng cường bảo mật và theo dõi các hành vi bất thường.

---

## Tương lai phát triển

Dự án hiện đang trong giai đoạn chuyển đổi và tập trung vào việc học FastAPI. Các phần còn thiếu (được biểu thị bởi `...`) sẽ được chuyển đổi và bổ sung thêm khi có thời gian. Mục tiêu của dự án này là cung cấp một nền tảng học tập và chuyển đổi kiến thức từ PHP sang FastAPI, chứ không nhằm mục đích hoàn thiện toàn bộ hệ thống ngay từ đầu.

---

## Liên hệ

Nếu bạn có ý kiến đóng góp hay câu hỏi, vui lòng liên hệ qua:  
**Email:** `nguyenhuuthang011@gmail.com`
**GitHub:** [https://github.com/nguyen-huu-thang](https://github.com/nguyen-huu-thang)

---

**License:** [Specify License]
