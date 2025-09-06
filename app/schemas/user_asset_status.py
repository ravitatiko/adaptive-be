from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class AssetStatus(str, Enum):
    """Enum for asset status values"""
    not_started = "not-started"
    in_progress = "in-progress"
    completed = "completed"

class UserAssetStatusBase(BaseModel):
    """Base schema for user asset status"""
    course: str = Field(..., description="Course code identifier")
    asset: str = Field(..., description="Asset code identifier")
    user: str = Field(..., description="User ID")
    status: AssetStatus = Field(..., description="Asset status")
    progress: Optional[int] = Field(default=0, ge=0, le=100, description="Progress percentage (0-100)")

class UserAssetStatusCreate(UserAssetStatusBase):
    """Schema for creating user asset status"""
    pass

class UserAssetStatusUpdate(BaseModel):
    """Schema for updating user asset status"""
    status: AssetStatus = Field(..., description="New asset status")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage (0-100)")

class UserAssetStatusResponse(UserAssetStatusBase):
    """Schema for user asset status response"""
    id: str = Field(..., description="Document ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_accessed: Optional[datetime] = Field(None, description="Last access timestamp")

    class Config:
        from_attributes = True
