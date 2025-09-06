"""
Quiz API endpoints for quiz generation and management.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.mongodb import get_database
from app.api.api_v1.endpoints.auth import get_current_user
from app.models.user import User as UserModel
from app.schemas.quiz import (
    QuizCreate, QuizUpdate, QuizResponse, QuizListResponse,
    QuizGenerationRequest, QuizGenerationResponse,
    QuizAttemptCreate, QuizAttemptResponse,
    QuizGenerationStatus
)
from app.services.quiz_service import QuizService

router = APIRouter()


# Quiz Generation Endpoints
@router.post("/generate", response_model=QuizGenerationResponse)
async def generate_quizzes(
    request: QuizGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorDatabase = Depends(get_database)
    # current_user: UserModel = Depends(get_current_user)  # Temporarily disabled for testing
) -> QuizGenerationResponse:
    """
    Generate quizzes for a course or specific module.
    
    **Parameters:**
    - **course_id**: MongoDB ObjectId of the course (required)
    - **module_code**: Module code reference (optional)
    - **overwrite**: Whether to overwrite existing quizzes (default: false)
    - **num_questions**: Number of questions per quiz (default: 5)
    - **difficulty**: Quiz difficulty level (easy/medium/hard)
    
    **Logic:**
    - If module_code provided: Generate quiz for that specific module
    - If module_code not provided and overwrite=true: Generate quizzes for ALL modules
    - If module_code not provided and overwrite=false: Generate quizzes only for modules without existing quizzes
    
    **Example Usage:**
    ```json
    {
        "course_id": "507f1f77bcf86cd799439011",
        "module_code": "MOD001",
        "overwrite": false,
        "num_questions": 5,
        "difficulty": "medium"
    }
    ```
    """
    try:
        quiz_service = QuizService()
        result = await quiz_service.generate_quizzes_for_course(db, request)
        
        return QuizGenerationResponse(
            success=result["success"],
            message=result["message"],
            generated_quizzes=[QuizResponse(**quiz) for quiz in result["generated_quizzes"]],
            skipped_modules=result["skipped_modules"],
            errors=result["errors"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating quizzes: {str(e)}"
        )


@router.get("/generation-status/{course_id}", response_model=QuizGenerationStatus)
async def get_quiz_generation_status(
    course_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserModel = Depends(get_current_user)
) -> QuizGenerationStatus:
    """
    Get the quiz generation status for a course.
    Shows how many modules have quizzes vs how many don't.
    """
    try:
        quiz_service = QuizService()
        
        # Get all quizzes for the course
        quizzes = await quiz_service.get_quizzes_by_course(db, course_id)
        
        # Get course modules info
        modules_info = await quiz_service.get_course_modules_info(db, course_id)
        
        modules_with_quizzes = len(set(quiz.module_code for quiz in quizzes if quiz.module_code))
        total_modules = len(modules_info)
        modules_without_quizzes = total_modules - modules_with_quizzes
        
        # Get last generation time
        last_generated = None
        if quizzes:
            last_generated = max(quiz.created_at for quiz in quizzes)
        
        return QuizGenerationStatus(
            course_id=course_id,
            total_modules=total_modules,
            modules_with_quizzes=modules_with_quizzes,
            modules_without_quizzes=modules_without_quizzes,
            last_generated=last_generated
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting quiz generation status: {str(e)}"
        )


# Quiz CRUD Endpoints
@router.post("/", response_model=QuizResponse)
async def create_quiz(
    quiz_data: QuizCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserModel = Depends(get_current_user)
) -> QuizResponse:
    """
    Create a new quiz manually.
    
    **Example:**
    ```json
    {
        "course_id": "507f1f77bcf86cd799439011",
        "module_code": "MOD001",
        "title": "Python Basics Quiz",
        "description": "Test your knowledge of Python fundamentals",
        "difficulty": "medium",
        "questions": [
            {
                "question": "What is Python?",
                "options": ["A snake", "A programming language", "A tool", "A framework"],
                "correct_answer": 1,
                "explanation": "Python is a high-level programming language."
            }
        ],
        "estimated_time_minutes": 10
    }
    ```
    """
    try:
        quiz_service = QuizService()
        quiz = await quiz_service.create_quiz(db, quiz_data)
        return QuizResponse(**quiz.to_dict())
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating quiz: {str(e)}"
        )


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserModel = Depends(get_current_user)
) -> QuizResponse:
    """Get a specific quiz by ID."""
    quiz_service = QuizService()
    quiz = await quiz_service.get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    return QuizResponse(**quiz.to_dict())


@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: str,
    quiz_update: QuizUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserModel = Depends(get_current_user)
) -> QuizResponse:
    """Update an existing quiz."""
    quiz_service = QuizService()
    quiz = await quiz_service.update_quiz(db, quiz_id, quiz_update)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    return QuizResponse(**quiz.to_dict())


@router.delete("/{quiz_id}")
async def delete_quiz(
    quiz_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserModel = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete a quiz (soft delete)."""
    quiz_service = QuizService()
    success = await quiz_service.delete_quiz(db, quiz_id)
    if not success:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    return {"message": "Quiz deleted successfully"}


@router.get("/course/{course_id}", response_model=QuizListResponse)
async def get_quizzes_by_course(
    course_id: str,
    module_code: Optional[str] = Query(None, description="Filter by module code"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserModel = Depends(get_current_user)
) -> QuizListResponse:
    """
    Get all quizzes for a course, optionally filtered by module.
    
    **Parameters:**
    - **course_id**: MongoDB ObjectId of the course
    - **module_code**: Optional module code to filter by
    - **page**: Page number for pagination
    - **size**: Number of items per page
    """
    try:
        quiz_service = QuizService()
        quizzes = await quiz_service.get_quizzes_by_course(db, course_id, module_code)
        
        # Apply pagination
        total = len(quizzes)
        start = (page - 1) * size
        end = start + size
        paginated_quizzes = quizzes[start:end]
        
        pages = (total + size - 1) // size  # Ceiling division
        
        return QuizListResponse(
            quizzes=[QuizResponse(**quiz.to_dict()) for quiz in paginated_quizzes],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting quizzes: {str(e)}"
        )


# Quiz Attempt Endpoints
@router.post("/attempt", response_model=QuizAttemptResponse)
async def create_quiz_attempt(
    attempt_data: QuizAttemptCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserModel = Depends(get_current_user)
) -> QuizAttemptResponse:
    """
    Submit a quiz attempt.
    
    **Example:**
    ```json
    {
        "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
        "user_program_id": "507f1f77bcf86cd799439011",
        "answers": [
            {
                "question_index": 0,
                "selected_answer": 1
            },
            {
                "question_index": 1,
                "selected_answer": 2
            }
        ]
    }
    ```
    """
    try:
        # Convert answers to the format expected by the service
        answers = [
            {
                "question_index": answer.question_index,
                "selected_answer": answer.selected_answer
            }
            for answer in attempt_data.answers
        ]
        
        quiz_service = QuizService()
        attempt = await quiz_service.create_quiz_attempt(
            db, str(current_user.id), attempt_data.quiz_id, attempt_data.user_program_id, answers
        )
        
        return QuizAttemptResponse(**attempt.to_dict())
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating quiz attempt: {str(e)}"
        )


@router.get("/attempts/my", response_model=List[QuizAttemptResponse])
async def get_my_quiz_attempts(
    quiz_id: Optional[str] = Query(None, description="Filter by quiz ID"),
    user_program_id: Optional[str] = Query(None, description="Filter by user program ID"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserModel = Depends(get_current_user)
) -> List[QuizAttemptResponse]:
    """Get all quiz attempts for the current user, optionally filtered by quiz ID and/or user program ID."""
    try:
        quiz_service = QuizService()
        attempts = await quiz_service.get_user_quiz_attempts(db, str(current_user.id), quiz_id, user_program_id)
        return [QuizAttemptResponse(**attempt.to_dict()) for attempt in attempts]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting quiz attempts: {str(e)}"
        )


# Utility Endpoints
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for quiz service."""
    return {
        "status": "healthy",
        "service": "quiz_service",
        "version": "1.0.0"
    }


@router.get("/stats/course/{course_id}")
async def get_course_quiz_stats(
    course_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserModel = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get quiz statistics for a course."""
    try:
        quiz_service = QuizService()
        quizzes = await quiz_service.get_quizzes_by_course(db, course_id)
        
        stats = {
            "total_quizzes": len(quizzes),
            "total_questions": sum(quiz.total_questions for quiz in quizzes),
            "difficulty_distribution": {},
            "modules_with_quizzes": len(set(quiz.module_code for quiz in quizzes if quiz.module_code)),
            "average_questions_per_quiz": 0,
            "last_generated": None
        }
        
        if quizzes:
            # Calculate difficulty distribution
            for quiz in quizzes:
                difficulty = quiz.difficulty or "medium"
                stats["difficulty_distribution"][difficulty] = stats["difficulty_distribution"].get(difficulty, 0) + 1
            
            # Calculate average questions per quiz
            stats["average_questions_per_quiz"] = round(stats["total_questions"] / len(quizzes), 1)
            
            # Get last generation time
            stats["last_generated"] = max(quiz.created_at for quiz in quizzes).isoformat()
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting quiz stats: {str(e)}"
        )
