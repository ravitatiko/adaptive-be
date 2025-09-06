from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime


class TranslationAsset(BaseModel):
    """Translation asset model for MongoDB - extends existing asset schema"""
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str
    style: str = "original"
    content: str
    code: str
    language: str = "en"  # Default language is English
    source_asset_id: Optional[str] = None  # Reference to original English asset
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class TranslationRequest(BaseModel):
    """Request model for translation"""
    asset_code: str
    target_language: str  # "hi" for Hindi, "te" for Telugu
    content: str


class TranslationResponse(BaseModel):
    """Response model for translation"""
    id: str = Field(alias="_id")
    name: str
    style: str
    content: str
    code: str
    language: str
    source_asset_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
