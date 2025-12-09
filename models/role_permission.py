from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class RolePermission(Base):
    __tablename__ = "role_permission"
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id"), primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permission.id"), primary_key=True)
