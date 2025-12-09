from sqlalchemy import Column, Text, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_type = Column(Text, nullable=False)
    actor_id = Column(Text, nullable=False)
    actor_label = Column(Text)
    action = Column(Text, nullable=False)
    target_type = Column(Text)
    target_id = Column(Text)
    target_label = Column(Text)
    metadata = Column(JSON, nullable=False)
    status = Column(Text, nullable=False)
    error_message = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
