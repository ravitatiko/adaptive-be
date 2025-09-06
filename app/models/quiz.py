"""
Quiz model for storing generated quizzes in MongoDB.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field
import uuid

from app.core.database import Base


class Quiz(Base):
    """Quiz model for storing generated quizzes in MongoDB."""
    
    def __init__(self, **data):
        """Initialize Quiz with MongoDB document structure."""
        self._id = data.get('_id', ObjectId())
        self.course_id = data.get('course_id')
        self.module_code = data.get('module_code')
        self.title = data.get('title')
        self.description = data.get('description')
        self.difficulty = data.get('difficulty', 'medium')
        self.questions = data.get('questions', [])
        self.total_questions = data.get('total_questions', len(self.questions))
        self.estimated_time_minutes = data.get('estimated_time_minutes')
        self.is_active = data.get('is_active', True)
        self.is_deleted = data.get('is_deleted', False)
        self.generated_by_ai = data.get('generated_by_ai', True)
        self.created_at = data.get('created_at', datetime.utcnow())
        self.updated_at = data.get('updated_at', datetime.utcnow())
    
    @property
    def id(self):
        """Get the MongoDB ObjectId as string."""
        return str(self._id)
    
    @property
    def questions_count(self):
        """Get the number of questions in this quiz."""
        return len(self.questions) if self.questions else 0
    
    def to_dict(self):
        """Convert quiz to dictionary for API responses."""
        return {
            "id": str(self._id),
            "course_id": self.course_id,
            "module_code": self.module_code,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "questions": self.questions,
            "total_questions": self.total_questions,
            "estimated_time_minutes": self.estimated_time_minutes,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "generated_by_ai": self.generated_by_ai,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_mongo_dict(self):
        """Convert quiz to dictionary for MongoDB storage."""
        return {
            "_id": self._id,
            "course_id": self.course_id,
            "module_code": self.module_code,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "questions": self.questions,
            "total_questions": self.total_questions,
            "estimated_time_minutes": self.estimated_time_minutes,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "generated_by_ai": self.generated_by_ai,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_mongo_dict(cls, data: Dict[str, Any]):
        """Create Quiz instance from MongoDB document."""
        return cls(**data)
    
    def __repr__(self):
        return f"<Quiz(id={self.id}, title='{self.title}', course_id='{self.course_id}')>"


class QuizAttempt(Base):
    """Model for tracking quiz attempts by users in MongoDB."""
    
    def __init__(self, **data):
        """Initialize QuizAttempt with MongoDB document structure."""
        self._id = data.get('_id', ObjectId())
        self.quiz_id = data.get('quiz_id')
        self.user_id = data.get('user_id')
        self.user_program_id = data.get('user_program_id')
        self.answers = data.get('answers', [])
        self.score = data.get('score', 0)
        self.max_score = data.get('max_score', 0)
        self.percentage = data.get('percentage', 0)
        self.started_at = data.get('started_at', datetime.utcnow())
        self.completed_at = data.get('completed_at')
        self.time_taken_seconds = data.get('time_taken_seconds')
        self.is_completed = data.get('is_completed', False)
    
    @property
    def id(self):
        """Get the MongoDB ObjectId as string."""
        return str(self._id)
    
    def calculate_percentage(self):
        """Calculate percentage score."""
        if self.max_score > 0:
            self.percentage = int((self.score / self.max_score) * 100)
        else:
            self.percentage = 0
        return self.percentage
    
    def to_dict(self):
        """Convert quiz attempt to dictionary for API responses."""
        return {
            "id": str(self._id),
            "quiz_id": self.quiz_id,
            "user_id": self.user_id,
            "user_program_id": self.user_program_id,
            "answers": self.answers,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "time_taken_seconds": self.time_taken_seconds,
            "is_completed": self.is_completed
        }
    
    def to_mongo_dict(self):
        """Convert quiz attempt to dictionary for MongoDB storage."""
        return {
            "_id": self._id,
            "quiz_id": self.quiz_id,
            "user_id": self.user_id,
            "user_program_id": self.user_program_id,
            "answers": self.answers,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "time_taken_seconds": self.time_taken_seconds,
            "is_completed": self.is_completed
        }
    
    @classmethod
    def from_mongo_dict(cls, data: Dict[str, Any]):
        """Create QuizAttempt instance from MongoDB document."""
        return cls(**data)
    
    def __repr__(self):
        return f"<QuizAttempt(id={self.id}, quiz_id={self.quiz_id}, score={self.score}/{self.max_score})>"
