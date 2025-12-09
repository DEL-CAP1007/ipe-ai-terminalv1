from sqlalchemy import Column, String, Text, ARRAY, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class Entity(Base):
    __tablename__ = 'entity'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    canonical_id = Column(Text, nullable=False)
    entity_type = Column(Text, nullable=False)
    title = Column(Text)
    summary = Column(Text)
    tags = Column(ARRAY(Text), default=list)
    status = Column(Text)
    priority = Column(Text)
    assignee = Column(Text)
    owner = Column(Text)
    due_date = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)

    index = relationship('EntityIndex', uselist=False, back_populates='entity')
    embedding = relationship('EntityEmbedding', uselist=False, back_populates='entity')
