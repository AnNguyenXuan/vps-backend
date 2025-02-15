from sqlalchemy import Column, Integer, ForeignKey, Boolean, UniqueConstraint
from app.core.database import Base

class GroupPermission(Base):
    __tablename__ = "group_permissions"
    __table_args__ = (
        UniqueConstraint("group_id", "permission_id", "target_id", name="uq_group_permission"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("groups.id"), index=True, nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), index=True, nullable=False)
    target_id = Column(Integer, nullable=True)
    record_enabled = Column(Boolean, default=False, nullable=False)
    is_denied = Column(Boolean, default=False, nullable=False)
