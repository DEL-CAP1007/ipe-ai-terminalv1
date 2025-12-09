from sqlalchemy import Column, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.types import TypeDecorator
import numpy as np

class Vector(TypeDecorator):
    impl = Base.metadata.bind.dialect.type_descriptor('vector(1536)')
    cache_ok = True
    def process_bind_param(self, value, dialect):
        if isinstance(value, list):
            return np.array(value, dtype=np.float32)
        return value
    def process_result_value(self, value, dialect):
        return list(value) if value is not None else None

class EntityEmbedding(Base):
    __tablename__ = 'entity_embedding'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    entity_id = Column(UUID(as_uuid=True), ForeignKey('entity.id', ondelete='CASCADE'), nullable=False, unique=True)
    embedding = Column(Vector)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    entity = relationship('Entity', back_populates='embedding')

# Add to Entity model:
# embedding = relationship('EntityEmbedding', uselist=False, back_populates='entity')
