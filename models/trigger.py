from sqlalchemy import Column, TIMESTAMP, Text, Boolean, JSON, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class Trigger(Base):
    __tablename__ = 'trigger'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(Text, nullable=False)
    description = Column(Text)
    event_type = Column(Text, nullable=False)
    conditions = Column(JSON, nullable=False)
    action = Column(JSON, nullable=False)
    is_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    runs = relationship('TriggerRun', back_populates='trigger')

class TriggerRun(Base):
    __tablename__ = 'trigger_run'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    trigger_id = Column(UUID(as_uuid=True), ForeignKey('trigger.id'), nullable=False)
    event_type = Column(Text, nullable=False)
    event_payload = Column(JSON, nullable=False)
    started_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    finished_at = Column(TIMESTAMP(timezone=True))
    status = Column(Text, nullable=False)
    error_message = Column(Text)
    trigger = relationship('Trigger', back_populates='runs')
