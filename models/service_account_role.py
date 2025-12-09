from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class ServiceAccountRole(Base):
    __tablename__ = "service_account_role"
    service_id = Column(UUID(as_uuid=True), ForeignKey("service_account.id"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id"), primary_key=True)
