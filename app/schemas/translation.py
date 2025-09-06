from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TranslationRequest(BaseModel):
    """Request schema for translation"""
    asset_code: str
    target_language: str  # "hi" for Hindi, "te" for Telugu
    content: str


class TranslationResponse(BaseModel):
    """Response schema for translation"""
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


class TranslationStatus(BaseModel):
    """Translation status schema"""
    asset_code: str
    language: str
    status: str  # "available", "pending", "error"
    translated_content: Optional[str] = None
    error_message: Optional[str] = None
