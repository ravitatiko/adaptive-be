from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UsersCollectionBase(BaseModel):
    """Base user schema for users collection"""
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    domain: str = Field(..., description="User's domain/field of expertise")
    hobbies: str = Field(..., description="User's hobbies (comma-separated string)")
    learningStyle: str = Field(..., description="User's learning style")

class UsersCollectionCreate(UsersCollectionBase):
    """Schema for creating a user in users collection"""
    pass

class UsersCollectionUpdate(BaseModel):
    """Schema for updating a user in users collection"""
    name: Optional[str] = None
    email: Optional[str] = None
    domain: Optional[str] = None
    hobbies: Optional[str] = None
    learningStyle: Optional[str] = None

class UsersCollectionResponse(UsersCollectionBase):
    """Schema for user response from users collection"""
    id: str = Field(..., description="User document ID")
    createdAt: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True

class UsersCollectionNotFound(BaseModel):
    """Schema for when user is not found in users collection"""
    detail: str = Field(..., description="Error message")
    user_id: str = Field(..., description="User ID that was not found")
