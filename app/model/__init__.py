from .user import User
from .product import Product
from .group import Group
from .permission import Permission
from .group_member import GroupMember
from .category import Category
from .group_permission import GroupPermission
from .user_permission import UserPermission
from .blacklist_token import BlacklistToken
from .refresh_token import RefreshToken

# Danh sách tất cả model (dùng để import gọn)
all_models = [
    User,
    Product,
    Group,
    Permission,
    GroupMember,
    Category,
    GroupPermission,
    UserPermission,
    BlacklistToken,
    RefreshToken
]
