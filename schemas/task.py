from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class TaskSchema(BaseModel):
    id: str
    title: str
    description: Optional[str] = ""
    status: str = Field(..., pattern="^(open|in_progress|done|blocked)$")
    priority: str = Field(..., pattern="^(low|normal|high|urgent)$")
    assignee: Optional[str] = None
    tags: List[str] = []
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @validator("tags", pre=True)
    def ensure_tags_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return list(v)
