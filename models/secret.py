from sqlalchemy import Column, String, Text, LargeBinary, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Secret(Base):
    __tablename__ = "secret"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, unique=True, nullable=False)
    value_encrypted = Column(LargeBinary, nullable=False)
    scope = Column(Text, nullable=False)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    owner_service_id = Column(UUID(as_uuid=True), ForeignKey("service_account.id"), nullable=True)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)
