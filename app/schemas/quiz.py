"""
Quiz schemas for API validation and serialization.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid


class QuizQuestion(BaseModel):
    """Schema for a single quiz question."""
    question: str = Field(..., description="The question text")
    options: List[str] = Field(..., min_items=2, max_items=6, description="Answer options")
    correct_answer: int = Field(..., ge=0, description="Index of correct answer (0-based)")
    explanation: Optional[str] = Field(None, description="Explanation for the correct answer")
    
    @validator('correct_answer')
    def validate_correct_answer(cls, v, values):
        """Validate that correct_answer index is within options range."""
        if 'options' in values and v >= len(values['options']):
            raise ValueError('correct_answer index must be within options range')
        return v


class QuizBase(BaseModel):
    """Base schema for quiz."""
    title: str = Field(..., max_length=255, description="Quiz title")
    description: Optional[str] = Field(None, description="Quiz description")
    difficulty: Optional[str] = Field("medium", pattern="^(easy|medium|hard)$", description="Quiz difficulty level")
    questions: List[QuizQuestion] = Field(..., min_items=1, description="List of quiz questions")
    estimated_time_minutes: Optional[int] = Field(None, ge=1, description="Estimated time to complete quiz")


class QuizCreate(QuizBase):
    """Schema for creating a quiz."""
    course_id: str = Field(..., min_length=24, max_length=24, description="MongoDB ObjectId of the course")
    module_code: Optional[str] = Field(None, description="Module code reference (optional)")
    
    @validator('course_id')
    def validate_object_id(cls, v):
        """Validate MongoDB ObjectId format."""
        if v and len(v) != 24:
            raise ValueError('Must be a valid 24-character MongoDB ObjectId')
        return v


class QuizUpdate(BaseModel):
    """Schema for updating a quiz."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    questions: Optional[List[QuizQuestion]] = Field(None, min_items=1)
    estimated_time_minutes: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class QuizResponse(QuizBase):
    """Schema for quiz response."""
    id: str
    course_id: str
    module_code: Optional[str]
    total_questions: int
    is_active: bool
    is_deleted: bool
    generated_by_ai: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class QuizListResponse(BaseModel):
    """Schema for quiz list response."""
    quizzes: List[QuizResponse]
    total: int
    page: int
    size: int
    pages: int


# Quiz Generation Schemas
class QuizGenerationRequest(BaseModel):
    """Schema for quiz generation request."""
    course_id: str = Field(..., min_length=24, max_length=24, description="MongoDB ObjectId of the course")
    module_code: Optional[str] = Field(None, description="Module code reference (optional)")
    overwrite: bool = Field(False, description="Whether to overwrite existing quizzes")
    num_questions: Optional[int] = Field(5, ge=1, le=20, description="Number of questions to generate")
    difficulty: Optional[str] = Field("medium", pattern="^(easy|medium|hard)$", description="Quiz difficulty level")
    
    @validator('course_id')
    def validate_object_id(cls, v):
        """Validate MongoDB ObjectId format."""
        if v and len(v) != 24:
            raise ValueError('Must be a valid 24-character MongoDB ObjectId')
        return v


class QuizGenerationResponse(BaseModel):
    """Schema for quiz generation response."""
    success: bool
    message: str
    generated_quizzes: List[QuizResponse] = []
    skipped_modules: List[str] = []
    errors: List[str] = []


# Quiz Attempt Schemas
class QuizAttemptAnswer(BaseModel):
    """Schema for a single quiz answer."""
    question_index: int = Field(..., ge=0, description="Index of the question")
    selected_answer: int = Field(..., ge=0, description="Index of selected answer")


class QuizAttemptCreate(BaseModel):
    """Schema for creating a quiz attempt."""
    quiz_id: str = Field(..., description="UUID of the quiz")
    user_program_id: str = Field(..., description="User program enrollment ID")
    answers: List[QuizAttemptAnswer] = Field(..., min_items=1, description="List of answers")


class QuizAttemptResponse(BaseModel):
    """Schema for quiz attempt response."""
    id: str
    quiz_id: str
    user_id: str
    user_program_id: str
    answers: List[Dict[str, Any]]
    score: int
    max_score: int
    percentage: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    time_taken_seconds: Optional[int]
    is_completed: bool
    
    class Config:
        from_attributes = True


# Course and Module Integration Schemas
class CourseModuleInfo(BaseModel):
    """Schema for course and module information."""
    course_id: str
    course_title: str
    module_id: Optional[str] = None
    module_title: Optional[str] = None
    module_code: Optional[str] = None
    assets_content: Optional[str] = None


class QuizGenerationStatus(BaseModel):
    """Schema for quiz generation status."""
    course_id: str
    total_modules: int
    modules_with_quizzes: int
    modules_without_quizzes: int
    last_generated: Optional[datetime] = None
