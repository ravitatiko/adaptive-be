from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime


class Asset(BaseModel):
    """Asset model for MongoDB"""
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    code: str  # New field for asset code
    name: str
    style: str = "original"
    content: str
    summary: Optional[str] = None  # AI-generated summary
    summary_updated_at: Optional[datetime] = None  # When summary was last updated
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class Module(BaseModel):
    """Module model containing assets"""
    type: str = "module"
    assets: List[str] = []
    
    class Config:
        arbitrary_types_allowed = True


class Course(BaseModel):
    """Course model for MongoDB"""
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str
    modules: List[Module] = []
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
