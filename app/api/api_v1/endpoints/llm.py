"""
LLM API endpoints for content generation.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.llm_service import (
    LLMRequest, 
    LLMResponse, 
    ResultType, 
    LLMProvider,
    llm_service,
    generate_quiz,
    generate_explanation,
    generate_story,
    generate_custom_content
)
#from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


class GenerateContentRequest(BaseModel):
    """Request model for content generation endpoint."""
    content: str = Field(description="The input content/description to process")
    result_type: ResultType = Field(description="Type of result to generate")
    additional_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional parameters for generation")
    provider: Optional[LLMProvider] = LLMProvider.GOOGLE
    max_tokens: Optional[int] = Field(default=1000, ge=100, le=4000)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)


class QuizGenerationRequest(BaseModel):
    """Specific request model for quiz generation."""
    content: str = Field(description="Content to create quiz from")
    num_questions: Optional[int] = Field(default=5, ge=1, le=20)
    difficulty: Optional[str] = Field(default="medium", pattern="^(easy|medium|hard)$")
    num_options: Optional[int] = Field(default=4, ge=2, le=6)


class ExplanationRequest(BaseModel):
    """Request model for explanation generation."""
    content: str = Field(description="Content to explain")
    style: Optional[str] = Field(default="clear and engaging")
    audience: Optional[str] = Field(default="general learners")


class StoryRequest(BaseModel):
    """Request model for story generation."""
    content: str = Field(description="Concept to explain through story")
    audience: Optional[str] = Field(default="students")
    length: Optional[str] = Field(default="medium", pattern="^(short|medium|long)$")


class CustomContentRequest(BaseModel):
    """Request model for custom content generation."""
    content: str = Field(description="Input content")
    custom_prompt: str = Field(description="Custom prompt template")
    additional_instructions: Optional[str] = Field(default="")


@router.post("/generate", response_model=LLMResponse)
async def generate_content(
    request: GenerateContentRequest,
    #current_user: User = Depends(get_current_user)
) -> LLMResponse:
    """
    Generate content using LLM based on input content and result type.
    
    This is the main endpoint for flexible content generation.
    """
    try:
        llm_request = LLMRequest(
            content=request.content,
            result_type=request.result_type,
            additional_params=request.additional_params,
            provider=request.provider,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        response = await llm_service.generate_content(llm_request)
        
        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=f"Content generation failed: {response.error_message}"
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating content: {str(e)}"
        )


@router.post("/generate/quiz", response_model=LLMResponse)
async def generate_quiz_endpoint(
    request: QuizGenerationRequest,
    #current_user: User = Depends(get_current_user)
) -> LLMResponse:
    """
    Generate a multiple choice quiz from the provided content.
    
    Example usage:
    - Content: "Photosynthesis is the process by which plants convert sunlight into energy..."
    - Result: Structured quiz with multiple choice questions
    """
    try:
        response = await generate_quiz(
            content=request.content,
            num_questions=request.num_questions,
            difficulty=request.difficulty
        )
        
        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=f"Quiz generation failed: {response.error_message}"
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating quiz: {str(e)}"
        )


@router.post("/generate/explanation", response_model=LLMResponse)
async def generate_explanation_endpoint(
    request: ExplanationRequest,
    #current_user: User = Depends(get_current_user)
) -> LLMResponse:
    """
    Generate a clear explanation of the provided content.
    
    Example usage:
    - Content: "Machine Learning"
    - Style: "beginner-friendly"
    - Result: Comprehensive explanation tailored to the audience
    """
    try:
        response = await generate_explanation(
            content=request.content,
            style=request.style,
            audience=request.audience
        )
        
        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=f"Explanation generation failed: {response.error_message}"
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating explanation: {str(e)}"
        )


@router.post("/generate/story", response_model=LLMResponse)
async def generate_story_endpoint(
    request: StoryRequest,
    #current_user: User = Depends(get_current_user)
) -> LLMResponse:
    """
    Generate a story that explains the concept in an engaging way.
    
    Example usage:
    - Content: "How databases work"
    - Audience: "high school students"
    - Result: Educational story with characters and plot
    """
    try:
        response = await generate_story(
            content=request.content,
            audience=request.audience,
            length=request.length
        )
        
        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=f"Story generation failed: {response.error_message}"
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating story: {str(e)}"
        )


@router.post("/generate/custom", response_model=LLMResponse)
async def generate_custom_content_endpoint(
    request: CustomContentRequest,
    #current_user: User = Depends(get_current_user)
) -> LLMResponse:
    """
    Generate content using a custom prompt template.
    
    This allows for maximum flexibility in content generation.
    
    Example usage:
    - Content: "Python functions"
    - Custom Prompt: "Create a beginner tutorial with examples and exercises"
    - Result: Custom formatted content based on the prompt
    """
    try:
        response = await generate_custom_content(
            content=request.content,
            custom_prompt=request.custom_prompt,
            additional_instructions=request.additional_instructions
        )
        
        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=f"Custom content generation failed: {response.error_message}"
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating custom content: {str(e)}"
        )


@router.get("/result-types")
async def get_supported_result_types(
    #current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get all supported result types and their descriptions.
    """
    return {
        "result_types": {
            "quiz_mcq": {
                "name": "Multiple Choice Quiz",
                "description": "Generate structured quiz with multiple choice questions",
                "parameters": ["num_questions", "difficulty", "num_options"]
            },
            "explanation": {
                "name": "Explanation",
                "description": "Generate clear explanation of concepts",
                "parameters": ["style", "audience"]
            },
            "summary": {
                "name": "Summary",
                "description": "Create concise summary of content",
                "parameters": ["length"]
            },
            "story": {
                "name": "Story",
                "description": "Create engaging story that explains concepts",
                "parameters": ["audience", "length"]
            },
            "meme_description": {
                "name": "Meme Description",
                "description": "Create humorous meme-based explanation",
                "parameters": []
            },
            "analogy": {
                "name": "Analogy",
                "description": "Create relatable analogy for complex concepts",
                "parameters": []
            },
            "code_example": {
                "name": "Code Example",
                "description": "Generate practical code examples",
                "parameters": ["language"]
            },
            "step_by_step": {
                "name": "Step-by-Step Guide",
                "description": "Create detailed step-by-step instructions",
                "parameters": []
            },
            "custom": {
                "name": "Custom",
                "description": "Generate content with custom prompt",
                "parameters": ["custom_prompt", "additional_instructions"]
            }
        },
        "providers": ["google", "openai", "anthropic", "local"],
        "common_parameters": {
            "max_tokens": "Maximum tokens for generation (100-4000)",
            "temperature": "Creativity level (0.0-2.0)",
            "provider": "LLM provider to use"
        }
    }


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for LLM service."""
    return {
        "status": "healthy",
        "service": "llm_service",
        "version": "1.0.0"
    }
