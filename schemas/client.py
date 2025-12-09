from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class ClientSchema(BaseModel):
    id: str
    name: str
    email: Optional[EmailStr] = None
    status: str  # "active", "inactive", "lead"
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
