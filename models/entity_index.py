from sqlalchemy import (
    Column, String, Text, ARRAY, TIMESTAMP, ForeignKey, func
)
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import relationship
from .base import Base

class EntityIndex(Base):
    __tablename__ = 'entity_index'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    entity_id = Column(UUID(as_uuid=True), ForeignKey('entity.id', ondelete='CASCADE'), nullable=False, unique=True)
    entity_type = Column(Text, nullable=False)
    canonical_id = Column(Text, nullable=False)
    title = Column(Text)
    summary = Column(Text)
    tags = Column(ARRAY(Text), default=list)
    status = Column(Text)
    priority = Column(Text)
    assignee = Column(Text)
    owner = Column(Text)
    due_date = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)
    search_vector = Column(TSVECTOR)

    entity = relationship('Entity', back_populates='index')

# Add back_populates to Entity model:
# index = relationship('EntityIndex', uselist=False, back_populates='entity')
