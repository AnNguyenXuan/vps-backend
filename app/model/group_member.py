from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.configuration.database import Base

class GroupMember(Base):
    __tablename__ = "group_members"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)

    __table_args__ = (UniqueConstraint("user_id", "group_id", name="unique_user_group"),)
