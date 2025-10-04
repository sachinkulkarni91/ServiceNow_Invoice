
from pydantic import BaseModel, Field
from typing import List, Optional

class ResolutionNoteOut(BaseModel):
    root_cause: str
    fix_applied: str
    validation: str
    preventive_action: str

class IncidentIn(BaseModel):
    number: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    latest_comments: List[str] = Field(default_factory=list)


class IncidentSummaryOut(BaseModel):
    issue: str
    actions_taken: List[str]


class WorkNotesOut(BaseModel):
    issue: str
    actions_taken: List[str]

class TextOut(BaseModel):
    text: str
