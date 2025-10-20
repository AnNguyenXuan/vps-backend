from fastapi.openapi.utils import get_openapi
import secrets, string
import requests
from app.core import config

class CephAdminClient:
    def __init__(self, endpoint: str, access_key: str, secret_key: str):
        self.endpoint = endpoint.rstrip("/")
        self.auth = (access_key, secret_key)

    def ensure_user(self, user_id: str):
        # GET user, nếu 404 thì tạo
        r = requests.get(f"{self.endpoint}/admin/user", params={"uid": user_id}, auth=self.auth, timeout=5)
        if r.status_code == 200:
            return r.json()
        # create user
        r = requests.put(f"{self.endpoint}/admin/user", params={"uid": user_id, "display-name": f"user-{user_id}"}, auth=self.auth, timeout=10)
        r.raise_for_status()
        return r.json()

    def set_bucket_quota(self, uid: str, bucket: str, max_size_kb: int, max_objects: int | None = None):
        payload = {"enabled": True, "max_size_kb": max_size_kb}
        if max_objects is not None: payload["max_objects"] = max_objects
        r = requests.put(
            f"{self.endpoint}/admin/user?quota&uid={uid}&bucket={bucket}",
            json=payload, auth=self.auth, timeout=10
        )
        r.raise_for_status()

    def save_bucket_ratelimit_metadata(self, uid: str, bucket: str, rps: int, burst: int):
        # Tuỳ cách bạn muốn lưu: ở đây demo PUT bucket tags qua Admin Ops metadata (hoặc lưu DB riêng)
        # Có thể thay bằng DB table `s3_bucket_config` nếu bạn muốn enforce ở proxy.
        return True


def custom_openapi(app):
    """
    Hàm custom_openapi nhận đối tượng app FastAPI,
    tạo lại schema OpenAPI với security scheme cho JWT.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Scime",                # Thay đổi tên API theo ý bạn
        version="0.0.1",               # Phiên bản API
        description="Đây là phần backend cho trang web thương mại điện tử",  # Mô tả API
        routes=app.routes,
    )

    # Định nghĩa security scheme cho JWT
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Áp dụng security cho tất cả các endpoint
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

def _rand_access_key(n: int = 20) -> str:
    # A-Z0-9
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))

def _rand_secret_key(n: int = 40) -> str:
    # a-zA-Z0-9
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))