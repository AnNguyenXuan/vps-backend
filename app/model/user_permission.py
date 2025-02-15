from sqlalchemy import Column, Integer, ForeignKey, Boolean, UniqueConstraint
from app.core.database import Base

class UserPermission(Base):
    __tablename__ = "user_permissions"
    __table_args__ = (
        UniqueConstraint("user_id", "permission_id", "target_id", name="uq_user_permission"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), index=True, nullable=False)
    target_id = Column(Integer, nullable=True)
    record_enabled = Column(Boolean, default=False, nullable=False)
    is_denied = Column(Boolean, default=False, nullable=False)
