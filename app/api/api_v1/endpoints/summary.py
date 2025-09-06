from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from app.schemas.summary import (
    SummaryRequest, SummaryResponse,
    KeyPointsRequest, KeyPointsResponse,
    SentimentRequest, SentimentResponse,
    TextAnalysisRequest, TextAnalysisResponse
)
from app.services.summary_service import summary_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/summarize", response_model=SummaryResponse)
async def summarize_text(request: SummaryRequest) -> SummaryResponse:
    """
    Summarize text using Google's Generative AI.
    
    - **text**: The text to summarize (minimum 10 characters)
    - **max_length**: Optional maximum length of summary in words (10-1000)
    - **style**: Summary style - concise, detailed, or bullet_points
    """
    try:
        if not settings.google_api_key:
            raise HTTPException(
                status_code=503, 
                detail="Google API key not configured. Please contact administrator."
            )
        
        result = await summary_service.summarize_text(
            text=request.text,
            max_length=request.max_length,
            style=request.style.value
        )
        
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        
        return SummaryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in summarize_text endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/key-points", response_model=KeyPointsResponse)
async def extract_key_points(request: KeyPointsRequest) -> KeyPointsResponse:
    """
    Extract key points from text using Google's Generative AI.
    
    - **text**: The text to analyze (minimum 10 characters)
    - **num_points**: Number of key points to extract (1-20)
    """
    try:
        if not settings.google_api_key:
            raise HTTPException(
                status_code=503, 
                detail="Google API key not configured. Please contact administrator."
            )
        
        result = await summary_service.extract_key_points(
            text=request.text,
            num_points=request.num_points
        )
        
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        
        return KeyPointsResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in extract_key_points endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest) -> SentimentResponse:
    """
    Analyze sentiment of text using Google's Generative AI.
    
    - **text**: The text to analyze (minimum 5 characters)
    """
    try:
        if not settings.google_api_key:
            raise HTTPException(
                status_code=503, 
                detail="Google API key not configured. Please contact administrator."
            )
        
        result = await summary_service.analyze_sentiment(text=request.text)
        
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        
        return SentimentResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_sentiment endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest) -> TextAnalysisResponse:
    """
    Comprehensive text analysis including summary, key points, and sentiment.
    
    - **text**: The text to analyze (minimum 10 characters)
    - **include_summary**: Whether to include text summary
    - **include_key_points**: Whether to include key points extraction
    - **include_sentiment**: Whether to include sentiment analysis
    - **summary_style**: Style for summary (concise, detailed, bullet_points)
    - **max_summary_length**: Optional maximum summary length
    - **num_key_points**: Number of key points to extract
    """
    try:
        if not settings.google_api_key:
            raise HTTPException(
                status_code=503, 
                detail="Google API key not configured. Please contact administrator."
            )
        
        word_count = len(request.text.split())
        result = {"word_count": word_count}
        
        # Generate summary if requested
        if request.include_summary:
            summary_result = await summary_service.summarize_text(
                text=request.text,
                max_length=request.max_summary_length,
                style=request.summary_style.value
            )
            if summary_result.get("error"):
                result["error"] = f"Summary error: {summary_result['error']}"
            else:
                result["summary"] = SummaryResponse(**summary_result)
        
        # Extract key points if requested
        if request.include_key_points:
            key_points_result = await summary_service.extract_key_points(
                text=request.text,
                num_points=request.num_key_points
            )
            if key_points_result.get("error"):
                if "error" in result:
                    result["error"] += f"; Key points error: {key_points_result['error']}"
                else:
                    result["error"] = f"Key points error: {key_points_result['error']}"
            else:
                result["key_points"] = KeyPointsResponse(**key_points_result)
        
        # Analyze sentiment if requested
        if request.include_sentiment:
            sentiment_result = await summary_service.analyze_sentiment(text=request.text)
            if sentiment_result.get("error"):
                if "error" in result:
                    result["error"] += f"; Sentiment error: {sentiment_result['error']}"
                else:
                    result["error"] = f"Sentiment error: {sentiment_result['error']}"
            else:
                result["sentiment"] = SentimentResponse(**sentiment_result)
        
        return TextAnalysisResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_text endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the summarization service.
    """
    return {
        "status": "healthy" if settings.google_api_key else "unhealthy",
        "google_api_configured": bool(settings.google_api_key),
        "service": "text-summarization",
        "version": "1.0.0"
    }

