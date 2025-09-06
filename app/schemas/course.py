from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AssetBase(BaseModel):
    """Base asset schema"""
    code: str
    name: str
    style: str = "original"
    content: str
    summary: Optional[str] = None
    summary_updated_at: Optional[datetime] = None


class AssetCreate(AssetBase):
    """Schema for creating an asset"""
    pass


class Asset(AssetBase):
    """Asset schema for responses"""
    id: str = Field(alias="_id")
    
    class Config:
        populate_by_name = True


class ModuleBase(BaseModel):
    """Base module schema"""
    id: str = Field(alias="_id")
    code: str
    type: str = "module"
    assets: List[str] = []


class ModuleCreate(ModuleBase):
    """Schema for creating a module"""
    pass


class Module(ModuleBase):
    """Module schema for responses"""
    pass


class CourseBase(BaseModel):
    """Base course schema"""
    name: str
    modules: List[ModuleCreate] = []


class CourseCreate(CourseBase):
    """Schema for creating a course"""
    pass


class CourseUpdate(BaseModel):
    """Schema for updating a course"""
    name: Optional[str] = None
    modules: Optional[List[ModuleCreate]] = None


class Course(CourseBase):
    """Course schema for responses"""
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    modules: List[Module] = []  # Override to use Module instead of ModuleCreate for responses
    
    class Config:
        populate_by_name = True


class CourseWithAssets(BaseModel):
    """Course schema with populated assets"""
    id: str = Field(alias="_id")
    name: str
    modules: List[dict] = []  # Will contain modules with populated assets
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True


class CourseWithUserProgress(BaseModel):
    """Course schema with populated assets and user progress"""
    id: str = Field(alias="_id")
    name: str
    modules: List[dict] = []  # Will contain modules with populated assets and user progress
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
