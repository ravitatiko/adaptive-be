from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class TransformationStyle(str, Enum):
    """Enum for transformation styles"""
    storytelling = "storytelling"
    visual_cue = "visual_cue"
    summary = "summary"
    original = "original"

class ContentTransformerRequest(BaseModel):
    """Request model for content transformation"""
    assetCode: str = Field(..., min_length=1, description="Asset code identifier")
    style: TransformationStyle = Field(..., description="Transformation style (storytelling, visual_cue, summary, or original)")
    content: str = Field(..., min_length=10, description="Raw content to transform (lecture, case study, or concept)")
    domain: str = Field(..., min_length=2, description="Domain context (e.g., Business, Engineering, Medicine, Education)")
    hobby: str = Field(..., min_length=2, description="Hobby context (e.g., Movies, Cricket, Gaming, Music)")

class ContentTransformerResponse(BaseModel):
    """Response model for content transformation"""
    id: str = Field(..., description="Database document ID")
    assetCode: str = Field(..., description="Asset code identifier")
    style: str = Field(..., description="Transformation style used")
    output: str = Field(..., description="Transformed content based on selected style")
    original_content: str = Field(..., description="Original content that was transformed")
    domain: str = Field(..., description="Domain used for transformation")
    hobby: str = Field(..., description="Hobby used for transformation")
    created_at: str = Field(..., description="Creation timestamp")
    error: Optional[str] = Field(None, description="Error message if any")

class ContentTransformerError(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error message")
    content: str = Field(..., description="Content that failed to transform")
