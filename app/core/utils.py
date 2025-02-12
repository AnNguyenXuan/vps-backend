from fastapi.openapi.utils import get_openapi

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
