from sqlalchemy.future import select
from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from app.model.permission import Permission
from app.model.user_permission import UserPermission
from app.core.database import AsyncSessionLocal
from app.core.exceptions import NotFoundError


class UserPermissionRepository:
    async def find_user_permission(self, user_id: int, permission_name: str) -> list:
        """
        Lấy danh sách UserPermission theo user_id và permission_name,
        ưu tiên bản ghi có target_id = None (sắp xếp theo target_id ASC).
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserPermission)
                .join(Permission, UserPermission.permission_id == Permission.id)
                .where(UserPermission.user_id == user_id)
                .where(Permission.name == permission_name)
                .order_by(asc(UserPermission.target_id))
            )
            return result.scalars().all()

    async def find_by_user_id(self, user_id: int) -> list[UserPermission]:
        """
        Lấy danh sách UserPermission theo user_id, sắp xếp theo id (tăng dần).
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserPermission)
                .where(UserPermission.user_id == user_id)
                .order_by(UserPermission.id.asc())
            )
            return result.scalars().all()

    async def bulk_insert(self, user_permissions: list) -> None:
        """
        Thêm nhiều bản ghi UserPermission cùng lúc, bỏ qua các bản ghi trùng lặp dựa theo unique constraint.
        """
        async with AsyncSessionLocal() as session:
            try:
                # Chuyển danh sách đối tượng thành danh sách dict
                records = [
                    {
                        "user_id": up.user_id,
                        "permission_id": up.permission_id,
                        "target_id": up.target_id,
                        "record_enabled": up.record_enabled,
                        "is_denied": up.is_denied
                    }
                    for up in user_permissions
                ]
                stmt = insert(UserPermission).values(records)
                # Xác định các cột để kiểm tra xung đột và bỏ qua nếu đã tồn tại
                stmt = stmt.on_conflict_do_nothing(index_elements=["user_id", "permission_id", "target_id"])
                await session.execute(stmt)
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                raise

    async def bulk_update(self, user_permissions: list[UserPermission]) -> None:
        """
        Cập nhật nhiều bản ghi UserPermission cùng lúc.
        Sử dụng session.merge để đảm bảo đối tượng được cập nhật đúng trong session mới.
        """
        async with AsyncSessionLocal() as session:
            try:
                for up in user_permissions:
                    session.merge(up)
                await session.commit()
                print("ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha")
            except SQLAlchemyError:
                await session.rollback()
                raise

    async def bulk_delete(self, user_permissions: list[UserPermission]) -> list[UserPermission]:
        """
        Xóa nhiều bản ghi UserPermission cùng lúc.
        Nếu có bản ghi lỗi, nó sẽ không bị xóa nhưng các bản ghi hợp lệ khác vẫn được xóa.
        Trả về danh sách các bản ghi bị lỗi khi xóa.
        """
        async with AsyncSessionLocal() as session:
            failed_deletes = []  # Danh sách các bản ghi không thể xóa
            try:
                for up in user_permissions:
                    try:
                        await session.delete(up)  # Xóa từng bản ghi
                    except SQLAlchemyError:
                        failed_deletes.append(up)  # Ghi lại bản ghi gây lỗi
                await session.commit()  # Chỉ commit nếu ít nhất một bản ghi hợp lệ được xóa
            except SQLAlchemyError:
                await session.rollback()  # Rollback toàn bộ nếu có lỗi nghiêm trọng
                raise
        return failed_deletes
