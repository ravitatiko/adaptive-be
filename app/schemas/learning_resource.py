from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class LearningResourceBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    url: str
    resource_type: str = Field(..., max_length=50)  # e.g., 'video', 'article', 'tutorial'
    difficulty_level: str = Field(..., max_length=20)  # e.g., 'beginner', 'intermediate', 'advanced'
    tags: List[str] = []

class LearningResourceCreate(LearningResourceBase):
    pass

class LearningResource(LearningResourceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LearningResourceUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    url: Optional[str] = None
    resource_type: Optional[str] = Field(None, max_length=50)
    difficulty_level: Optional[str] = Field(None, max_length=20)
    tags: Optional[List[str]] = None
