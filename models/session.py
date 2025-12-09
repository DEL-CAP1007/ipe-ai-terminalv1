from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class Session(Base):
    __tablename__ = "session"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("service_account.id"), nullable=True)
    user = relationship("User")
    service = relationship("ServiceAccount")
    created_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_active_at = Column(DateTime(timezone=True), nullable=False)
    user_agent = Column(Text, nullable=True)
    client_ip = Column(Text, nullable=True)
