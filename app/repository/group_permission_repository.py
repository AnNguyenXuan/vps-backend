from sqlalchemy.future import select
from sqlalchemy import asc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from app.model.permission import Permission
from app.model.group_permission import GroupPermission
from app.core.database import AsyncSessionLocal


class GroupPermissionRepository:
    async def find_group_permission(self, group_id: int, permission_name: str) -> list:
        """
        Lấy danh sách GroupPermission theo group_id và permission_name,
        ưu tiên bản ghi có target_id = None (sắp xếp theo target_id ASC).
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(GroupPermission)
                .join(Permission, GroupPermission.permission_id == Permission.id)
                .where(GroupPermission.group_id == group_id)
                .where(Permission.name == permission_name)
                .order_by(asc(GroupPermission.target_id))
            )
            return result.scalars().all()

    async def find_by_group_id(self, group_id: int) -> list[GroupPermission]:
        """
        Lấy danh sách GroupPermission theo group_id, sắp xếp theo id (tăng dần).
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(GroupPermission)
                .where(GroupPermission.group_id == group_id)
                .order_by(GroupPermission.id.asc())
            )
            return result.scalars().all()

    async def bulk_insert(self, group_permissions: list) -> None:
        """
        Thêm nhiều bản ghi GroupPermission cùng lúc, bỏ qua các bản ghi trùng lặp dựa theo unique constraint.
        """
        async with AsyncSessionLocal() as session:
            try:
                records = [
                    {
                        "group_id": gp.group_id,
                        "permission_id": gp.permission_id,
                        "target_id": gp.target_id,
                        "record_enabled": gp.record_enabled,
                        "is_denied": gp.is_denied
                    }
                    for gp in group_permissions
                ]
                stmt = insert(GroupPermission).values(records)
                stmt = stmt.on_conflict_do_nothing(index_elements=["group_id", "permission_id", "target_id"])
                await session.execute(stmt)
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                raise

    async def bulk_update(self, group_permissions: list[GroupPermission]) -> None:
        """
        Cập nhật nhiều bản ghi GroupPermission cùng lúc.
        Sử dụng session.merge để đảm bảo đối tượng được cập nhật đúng trong session mới.
        """
        async with AsyncSessionLocal() as session:
            for gp in group_permissions:
                await session.merge(gp)
            await session.commit()

    async def bulk_delete(self, group_permissions: list[GroupPermission]) -> list[GroupPermission]:
        """
        Xóa nhiều bản ghi GroupPermission cùng lúc.
        Nếu có bản ghi lỗi, nó sẽ không bị xóa nhưng các bản ghi hợp lệ khác vẫn được xóa.
        Trả về danh sách các bản ghi bị lỗi khi xóa.
        """
        async with AsyncSessionLocal() as session:
            failed_deletes = []
            try:
                for gp in group_permissions:
                    try:
                        await session.delete(gp)
                    except SQLAlchemyError:
                        failed_deletes.append(gp)
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                raise
        return failed_deletes
