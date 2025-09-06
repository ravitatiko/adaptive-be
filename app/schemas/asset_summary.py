from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AssetSummaryRequest(BaseModel):
    """Request schema for generating asset summary"""
    asset_id: str


class AssetSummaryResponse(BaseModel):
    """Response schema for asset summary generation"""
    id: str = Field(alias="_id")
    code: str
    name: str
    style: str
    content: str
    summary: str
    summary_updated_at: datetime
    
    class Config:
        populate_by_name = True


class AssetSummaryStatus(BaseModel):
    """Status schema for asset summary generation"""
    success: bool
    message: str
    asset_id: str
    summary: Optional[str] = None
    summary_updated_at: Optional[datetime] = None
