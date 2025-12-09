from sqlalchemy import Column, TIMESTAMP, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class EntityRelation(Base):
    __tablename__ = 'entity_relation'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    from_entity_id = Column(UUID(as_uuid=True), ForeignKey('entity.id', ondelete='CASCADE'), nullable=False)
    from_type = Column(Text, nullable=False)
    from_canonical = Column(Text, nullable=False)
    to_entity_id = Column(UUID(as_uuid=True), ForeignKey('entity.id', ondelete='CASCADE'), nullable=False)
    to_type = Column(Text, nullable=False)
    to_canonical = Column(Text, nullable=False)
    relation_type = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    from_entity = relationship('Entity', foreign_keys=[from_entity_id])
    to_entity = relationship('Entity', foreign_keys=[to_entity_id])
