from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class SummaryStyle(str, Enum):
    """Enum for summary styles."""
    CONCISE = "concise"
    DETAILED = "detailed"
    BULLET_POINTS = "bullet_points"

class SummaryRequest(BaseModel):
    """Request model for text summarization."""
    text: str = Field(..., min_length=10, description="Text to summarize")
    max_length: Optional[int] = Field(None, ge=10, le=1000, description="Maximum length of summary in words")
    style: SummaryStyle = Field(SummaryStyle.CONCISE, description="Style of summary")

class SummaryResponse(BaseModel):
    """Response model for text summarization."""
    summary: Optional[str] = Field(None, description="Generated summary")
    word_count: int = Field(0, description="Word count of summary")
    original_word_count: int = Field(0, description="Word count of original text")
    compression_ratio: float = Field(0, description="Compression ratio (original/summary)")
    style: str = Field(..., description="Style used for summary")
    max_length: Optional[int] = Field(None, description="Maximum length requested")
    error: Optional[str] = Field(None, description="Error message if any")

class KeyPointsRequest(BaseModel):
    """Request model for key points extraction."""
    text: str = Field(..., min_length=10, description="Text to extract key points from")
    num_points: int = Field(5, ge=1, le=20, description="Number of key points to extract")

class KeyPointsResponse(BaseModel):
    """Response model for key points extraction."""
    key_points: List[str] = Field([], description="List of extracted key points")
    word_count: int = Field(0, description="Word count of original text")
    extracted_count: int = Field(0, description="Number of key points extracted")
    error: Optional[str] = Field(None, description="Error message if any")

class SentimentRequest(BaseModel):
    """Request model for sentiment analysis."""
    text: str = Field(..., min_length=5, description="Text to analyze sentiment")

class SentimentResponse(BaseModel):
    """Response model for sentiment analysis."""
    sentiment: Optional[str] = Field(None, description="Overall sentiment (positive/negative/neutral)")
    confidence: int = Field(0, ge=0, le=100, description="Confidence level (0-100%)")
    explanation: str = Field("", description="Brief explanation of sentiment")
    word_count: int = Field(0, description="Word count of analyzed text")
    error: Optional[str] = Field(None, description="Error message if any")

class TextAnalysisRequest(BaseModel):
    """Request model for comprehensive text analysis."""
    text: str = Field(..., min_length=10, description="Text to analyze")
    include_summary: bool = Field(True, description="Include text summary")
    include_key_points: bool = Field(True, description="Include key points extraction")
    include_sentiment: bool = Field(True, description="Include sentiment analysis")
    summary_style: SummaryStyle = Field(SummaryStyle.CONCISE, description="Style for summary")
    max_summary_length: Optional[int] = Field(None, ge=10, le=1000, description="Maximum summary length")
    num_key_points: int = Field(5, ge=1, le=20, description="Number of key points to extract")

class TextAnalysisResponse(BaseModel):
    """Response model for comprehensive text analysis."""
    summary: Optional[SummaryResponse] = Field(None, description="Text summary")
    key_points: Optional[KeyPointsResponse] = Field(None, description="Key points extraction")
    sentiment: Optional[SentimentResponse] = Field(None, description="Sentiment analysis")
    word_count: int = Field(0, description="Word count of original text")
    error: Optional[str] = Field(None, description="Error message if any")

