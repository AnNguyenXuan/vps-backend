from __future__ import annotations
from typing import Any, Dict, Optional
from urllib.parse import quote
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
from app.core import config


def _build_url(base: str, path: str, params: Optional[Dict[str, Any]]) -> str:
    """
    Ghép URL theo chuẩn:
      - KHÔNG dùng urljoin (dễ làm mất /admin/...)
      - Query sort theo key, RFC3986 encode (safe='-_.~'), luôn có format=json
    """
    base = base.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    p = {"format": "json", **(params or {})}
    qs = "&".join(
        f"{quote(str(k), safe='-_.~')}={quote(str(v), safe='-_.~')}"
        for k, v in sorted(p.items())
    )
    return f"{base}{path}?{qs}" if qs else f"{base}{path}"


class _CephAdminClient:
    """
    HTTP client ký AWS SigV4 để gọi Ceph RGW Admin Ops API.
    VD base_admin_url: http://rgw:7480  (KHÔNG thêm /admin ở đây; path sẽ thêm sau)
    """

    def __init__(
        self,
        base_admin_url: str,
        access_key: str,
        secret_key: str,
        region: str = "us-east-1",
        *,
        verify_tls: bool = True,
        timeout: tuple[float, float] = (3.1, 10.0),
    ):
        self.base_admin_url = base_admin_url.rstrip("/")
        self.creds = Credentials(access_key, secret_key)
        self.region = region
        self.verify_tls = verify_tls
        self.timeout = timeout
        self.session = requests.Session()
        # Tránh vô tình dùng HTTP(S)_PROXY/NO_PROXY từ môi trường
        self.session.trust_env = False

    def _signed_request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = _build_url(self.base_admin_url, path, params)

        # Tạo AWSRequest và ĐẶT x-amz-content-sha256 TRƯỚC khi ký
        aws_req = AWSRequest(method=method.upper(), url=url, data=b"")
        aws_req.headers["x-amz-content-sha256"] = "UNSIGNED-PAYLOAD"

        # Ký SigV4 (service 's3')
        SigV4Auth(self.creds, "s3", self.region).add_auth(aws_req)

        # Gửi đi với headers đã ký nguyên vẹn
        headers = dict(aws_req.headers.items())
        return self.session.request(
            method=method.upper(),
            url=url,
            headers=headers,
            timeout=self.timeout,
            verify=self.verify_tls,
        )

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self._signed_request("GET", path, params)

    def put(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self._signed_request("PUT", path, params)

    def post(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return self._signed_request("POST", path, params)


class S3AdminService:
    """
    Bao bọc Admin Ops API: tạo RGW user, lấy user, generate key,...
    Đọc cấu hình từ app.core.config.
    """

    def __init__(self):
        admin_endpoint = config.CEPH_ADMIN_ENDPOINT    
        admin_ak = config.CEPH_ADMIN_ACCESS_KEY
        admin_sk = config.CEPH_ADMIN_SECRET_KEY
        region = getattr(config, "CEPH_REGION", "us-east-1")
        verify = getattr(config, "CEPH_ADMIN_VERIFY_TLS", True)
        timeout = getattr(config, "CEPH_ADMIN_TIMEOUT", (3.1, 10.0))

        if not (admin_endpoint and admin_ak and admin_sk and region):
            raise RuntimeError("Missing Ceph Admin configuration (CEPH_ADMIN_* / CEPH_REGION).")

        self.client = _CephAdminClient(
            base_admin_url=admin_endpoint,
            access_key=admin_ak,
            secret_key=admin_sk,
            region=region,
            verify_tls=verify,
            timeout=timeout,
        )

    async def get_user(self, uid: str) -> Dict[str, Any]:
        r = self.client.get("/user", {"uid": uid, "stats": "false"})
        if r.status_code != 200:
            raise RuntimeError(f"Cannot fetch user info: {r.status_code} {r.text}")
        return await r.json()

    async def create_user(self, uid: str, display_name: str, key_type: str, access_key: str, secret_key: str, user_caps: str) -> Dict: 
        params = {
            "uid" : uid,
            "display-name" : display_name,
            "key-type": key_type,
            "access-key" : access_key,
            "secret-key" : secret_key,
            "user_caps": user_caps,
            #"default-placement" : default_placement
        }
        """
        Đảm bảo user RGW tồn tại (idempotent).
        - PUT /admin/user?uid&display-name
        - Sau đó GET /admin/user?uid&stats=false để lấy info
        """
        r = self.client.put("/user", params=params)
        if r.status_code not in (200, 201, 409):
            raise RuntimeError(f"Failed to create Ceph user: {r.status_code} {r.text}")

        info = self.client.get("/user",params={"format": "json", "uid": uid, "stats": "false"})
        info.raise_for_status()

        return await info.json()
    
    def remove_user(self, uid: str) -> Dict[str, Any]:
        r = self.client.get("/user", {"uid": uid, "stats": "false"})
        if r.status_code != 200:
            raise RuntimeError(f"Cannot remove user info: {r.status_code} {r.text}")
        return r.json()