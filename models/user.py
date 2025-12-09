from sqlalchemy import Column, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base

class User(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, unique=True, nullable=False)
    display_name = Column(Text, nullable=False)
    password_hash = Column(Text, nullable=True)
    auth_provider = Column(Text, nullable=False, default="local")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
