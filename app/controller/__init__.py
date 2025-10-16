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
