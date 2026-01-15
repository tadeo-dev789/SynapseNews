from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
import uuid

class New(SQLModel, table = True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    original_title : str
    url : str
    category: str
    
    ai_summary : Optional[str] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)