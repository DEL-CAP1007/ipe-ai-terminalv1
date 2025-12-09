from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class PipelineStep(BaseModel):
    id: str
    name: str
    order: int
    status: str

class PipelineSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    status: str
    owner: Optional[str] = None
    tags: List[str] = []
    steps: List[PipelineStep] = []
    created_at: datetime
    updated_at: datetime
