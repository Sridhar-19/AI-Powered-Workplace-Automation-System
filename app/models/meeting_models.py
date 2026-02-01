"""
Pydantic models for meeting notes.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date


class ActionItem(BaseModel):
    """Action item model."""
    task: str = Field(..., description="Task description")
    owner: Optional[str] = Field(None, description="Person responsible")
    due_date: Optional[str] = Field(None, description="Due date")
    priority: str = Field(default="medium", description="Priority level")
    status: str = Field(default="pending", description="Status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task": "Prepare Q4 presentation",
                "owner": "John Doe",
                "due_date": "2024-03-15",
                "priority": "high"
            }
        }


class Decision(BaseModel):
    """Decision model."""
    decision: str = Field(..., description="The decision made")
    context: Optional[str] = Field(None, description="Context or reasoning")
    impact: Optional[str] = Field(None, description="Expected impact")
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision": "Approved budget increase of 15%",
                "context": "To support expanded marketing campaign",
                "impact": "Expected 20% increase in customer acquisition"
            }
        }


class MeetingNotes(BaseModel):
    """Complete meeting notes model."""
    meeting_id: Optional[str] = Field(None, description="Meeting ID")
    title: Optional[str] = Field(None, description="Meeting title")
    date: Optional[datetime] = Field(None, description="Meeting date")
    participants: List[str] = Field(default_factory=list)
    decisions: List[Decision] = Field(default_factory=list)
    action_items: List[ActionItem] = Field(default_factory=list)
    key_points: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Q4 Planning Meeting",
                "date": "2024-01-15T10:00:00Z",
                "participants": ["Alice", "Bob", "Charlie"],
                "decisions": [],
                "action_items": [],
                "key_points": ["Discussed Q4 targets", "Reviewed budget"],
                "next_steps": ["Schedule follow-up meeting"]
            }
        }


class MeetingExtractionRequest(BaseModel):
    """Request for meeting notes extraction."""
    text: str = Field(..., description="Meeting transcript or notes")
    meeting_title: Optional[str] = Field(None, description="Meeting title")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Meeting transcript here...",
                "meeting_title": "Weekly Team Sync"
            }
        }
