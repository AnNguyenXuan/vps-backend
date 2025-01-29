from sqlalchemy import Column, Integer, ForeignKey, Boolean
from app.configuration.database import Base

class GroupPermission(Base):
    __tablename__ = "group_permissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    target_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    is_denied = Column(Boolean, default=False)
