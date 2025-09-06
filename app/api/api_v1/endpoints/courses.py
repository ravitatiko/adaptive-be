from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.core.mongodb import get_database
from app.schemas.course import Course, CourseCreate, CourseUpdate, CourseWithAssets, CourseWithUserProgress, Asset, AssetCreate
from app.services.course_service import CourseService
from app.api.api_v1.endpoints.auth import get_current_user
from app.models.user import User as UserModel

router = APIRouter()


@router.get("/{course_id}/assets", response_model=CourseWithAssets)
async def get_course_assets(
    course_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get course with populated assets.
    Returns the course with all modules and their associated assets.
    """
    try:
        # Validate ObjectId format
        ObjectId(course_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid course ID format"
        )
    
    db = get_database()
    course_service = CourseService(db)
    
    course = await course_service.get_course_with_assets(course_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return course


@router.get("/{course_id}/assets/progress", response_model=CourseWithUserProgress)
async def get_course_assets_with_progress(
    course_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get course with populated assets and user progress.
    Returns the course with all modules, their associated assets, and user progress status.
    """
    try:
        # Validate ObjectId format
        ObjectId(course_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid course ID format"
        )
    
    db = get_database()
    course_service = CourseService(db)
    
    # Use current user's ID for progress tracking
    user_id = str(current_user.id)
    course = await course_service.get_course_with_user_progress(course_id, user_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return course


@router.get("/", response_model=List[Course])
async def get_courses(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get list of courses with pagination.
    """
    db = get_database()
    course_service = CourseService(db)
    
    courses = await course_service.get_courses(skip=skip, limit=limit)
    return courses


@router.get("/{course_id}", response_model=Course)
async def get_course(
    course_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get a specific course by ID.
    """
    try:
        # Validate ObjectId format
        ObjectId(course_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid course ID format"
        )
    
    db = get_database()
    course_service = CourseService(db)
    
    course = await course_service.get_course(course_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return course


@router.post("/", response_model=Course)
async def create_course(
    course: CourseCreate,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new course.
    """
    db = get_database()
    course_service = CourseService(db)
    
    try:
        new_course = await course_service.create_course(course)
        return new_course
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create course: {str(e)}"
        )


@router.put("/{course_id}", response_model=Course)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a course.
    """
    try:
        # Validate ObjectId format
        ObjectId(course_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid course ID format"
        )
    
    db = get_database()
    course_service = CourseService(db)
    
    updated_course = await course_service.update_course(course_id, course_update)
    
    if not updated_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return updated_course


@router.delete("/{course_id}")
async def delete_course(
    course_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a course.
    """
    try:
        # Validate ObjectId format
        ObjectId(course_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid course ID format"
        )
    
    db = get_database()
    course_service = CourseService(db)
    
    success = await course_service.delete_course(course_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return {"message": "Course deleted successfully"}


# Asset endpoints
@router.get("/assets/", response_model=List[Asset])
async def get_assets(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get list of assets with pagination.
    """
    db = get_database()
    course_service = CourseService(db)
    
    assets = await course_service.get_assets(skip=skip, limit=limit)
    return assets


@router.get("/assets/{asset_id}", response_model=Asset)
async def get_asset(
    asset_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get a specific asset by ID.
    """
    try:
        # Validate ObjectId format
        ObjectId(asset_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid asset ID format"
        )
    
    db = get_database()
    course_service = CourseService(db)
    
    asset = await course_service.get_asset(asset_id)
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    return asset


@router.post("/assets/", response_model=Asset)
async def create_asset(
    asset: AssetCreate,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new asset.
    """
    db = get_database()
    course_service = CourseService(db)
    
    try:
        new_asset = await course_service.create_asset(asset)
        return new_asset
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create asset: {str(e)}"
        )


@router.delete("/assets/{asset_id}")
async def delete_asset(
    asset_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete an asset.
    """
    try:
        # Validate ObjectId format
        ObjectId(asset_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid asset ID format"
        )
    
    db = get_database()
    course_service = CourseService(db)
    
    success = await course_service.delete_asset(asset_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    return {"message": "Asset deleted successfully"}
