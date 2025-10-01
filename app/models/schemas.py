from pydantic import BaseModel, Field
from typing import List, Optional

class IncidentIn(BaseModel):
    number: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    latest_comments: List[str] = Field(default_factory=list)

class SummaryOut(BaseModel):
    summary: str
    key_facts: List[str] = Field(default_factory=list)

class TextOut(BaseModel):
    text: str
