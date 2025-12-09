from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class ApiToken(Base):
    __tablename__ = "api_token"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token_hash = Column(Text, nullable=False)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    owner_service_id = Column(UUID(as_uuid=True), ForeignKey("service_account.id"), nullable=True)
    scopes = Column(JSON, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    last_used_at = Column(TIMESTAMP(timezone=True), nullable=True)
