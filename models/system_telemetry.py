from sqlalchemy import Column, String, Integer, TIMESTAMP, JSON, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class SystemTelemetry(Base):
    __tablename__ = 'system_telemetry'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    metric = Column(String, nullable=False)
    value = Column(Integer, nullable=False)
    meta = Column(JSON, server_default=text("'{}'"))
