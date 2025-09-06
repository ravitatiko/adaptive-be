from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime
import logging
from bson import ObjectId

from app.schemas.users_collection import (
    UsersCollectionCreate,
    UsersCollectionUpdate,
    UsersCollectionResponse,
    UsersCollectionNotFound
)
from app.core.mongodb import get_database

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/{user_id}",
    response_model=UsersCollectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User Preferences",
    description="Retrieve user preferences by user ID from the users collection.",
    responses={
        200: {
            "description": "User preferences retrieved successfully",
            "model": UsersCollectionResponse
        },
        404: {
            "description": "User preferences not found",
            "model": UsersCollectionNotFound
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def getUserPreferences(
    user_id: str,
    db=Depends(get_database)
):
    """
    Get user preferences by user ID.
    
    - **user_id**: The unique identifier of the user (MongoDB ObjectId)
    
    Returns the user's preferences including name, email, domain, hobbies, and learning style.
    """
    try:
        logger.info(f"Fetching user preferences for user ID: {user_id}")
        
        # Convert string to ObjectId
        try:
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid user ID format: {user_id}"
            )
        
        # Find user in MongoDB users collection
        user = await db.users.find_one({"_id": object_id})
        
        if user:
            # Convert MongoDB ObjectId to string for the response
            user["id"] = str(user["_id"])
            del user["_id"]  # Remove the MongoDB _id field
            
            logger.info(f"Found user preferences for user ID: {user_id}")
            return UsersCollectionResponse(**user)
        else:
            logger.warning(f"User preferences not found for user ID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User preferences not found for user ID: {user_id}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user preferences {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user preferences: {str(e)}"
        )

@router.get(
    "/email/{email}",
    response_model=UsersCollectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User Preferences by Email",
    description="Retrieve user preferences by email address from the users collection.",
    responses={
        200: {
            "description": "User preferences retrieved successfully",
            "model": UsersCollectionResponse
        },
        404: {
            "description": "User preferences not found",
            "model": UsersCollectionNotFound
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def getUserPreferencesByEmail(
    email: str,
    db=Depends(get_database)
):
    """
    Get user preferences by email address.
    
    - **email**: The email address of the user
    
    Returns the user's preferences including name, email, domain, hobbies, and learning style.
    """
    try:
        logger.info(f"Fetching user preferences for email: {email}")
        
        # Find user in MongoDB users collection by email
        user = await db.users.find_one({"email": email})
        
        if user:
            # Convert MongoDB ObjectId to string for the response
            user["id"] = str(user["_id"])
            del user["_id"]  # Remove the MongoDB _id field
            
            logger.info(f"Found user preferences for email: {email}")
            return UsersCollectionResponse(**user)
        else:
            logger.warning(f"User preferences not found for email: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User preferences not found for email: {email}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user preferences by email {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user preferences: {str(e)}"
        )

@router.post(
    "/",
    response_model=UsersCollectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save User Preferences",
    description="Create new user preferences in the users collection.",
    responses={
        201: {
            "description": "User preferences created successfully",
            "model": UsersCollectionResponse
        },
        400: {
            "description": "Bad request - invalid data"
        },
        409: {
            "description": "User preferences already exist"
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def saveUserPreferences(
    user_preferences: UsersCollectionCreate,
    db=Depends(get_database)
):
    """
    Save/create new user preferences.
    
    - **user_preferences**: User preferences data including name, email, domain, hobbies, and learning style
    
    Creates new user preferences in the users collection.
    """
    try:
        logger.info(f"Saving user preferences for email: {user_preferences.email}")
        
        # Check if user already exists by email
        existing_user = await db.users.find_one({"email": user_preferences.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User preferences already exist for email: {user_preferences.email}"
            )
        
        # Prepare data for insertion
        user_data = user_preferences.dict()
        user_data["createdAt"] = datetime.utcnow()
        
        # Insert into MongoDB
        result = await db.users.insert_one(user_data)
        
        if result.inserted_id:
            # Fetch the created document
            created_user = await db.users.find_one({"_id": result.inserted_id})
            created_user["id"] = str(created_user["_id"])
            del created_user["_id"]
            
            logger.info(f"Successfully saved user preferences for email: {user_preferences.email}")
            return UsersCollectionResponse(**created_user)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save user preferences"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving user preferences for email {user_preferences.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save user preferences: {str(e)}"
        )

@router.put(
    "/{user_id}",
    response_model=UsersCollectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Update User Preferences",
    description="Update existing user preferences by user ID.",
    responses={
        200: {
            "description": "User preferences updated successfully",
            "model": UsersCollectionResponse
        },
        404: {
            "description": "User preferences not found",
            "model": UsersCollectionNotFound
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def updateUserPreferences(
    user_id: str,
    user_preferences_update: UsersCollectionUpdate,
    db=Depends(get_database)
):
    """
    Update user preferences by user ID.
    
    - **user_id**: The unique identifier of the user
    - **user_preferences_update**: Updated user preferences data
    
    Updates existing user preferences in the users collection.
    """
    try:
        logger.info(f"Updating user preferences for user ID: {user_id}")
        
        # Convert string to ObjectId
        try:
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid user ID format: {user_id}"
            )
        
        # Check if user exists
        existing_user = await db.users.find_one({"_id": object_id})
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User preferences not found for user ID: {user_id}"
            )
        
        # Prepare update data (only include non-None values)
        update_data = {k: v for k, v in user_preferences_update.dict().items() if v is not None}
        
        # Update in MongoDB
        result = await db.users.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            # Fetch the updated document
            updated_user = await db.users.find_one({"_id": object_id})
            updated_user["id"] = str(updated_user["_id"])
            del updated_user["_id"]
            
            logger.info(f"Successfully updated user preferences for user ID: {user_id}")
            return UsersCollectionResponse(**updated_user)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user preferences"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user preferences {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user preferences: {str(e)}"
        )

@router.get(
    "/",
    response_model=List[UsersCollectionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All User Preferences",
    description="Retrieve all user preferences from the users collection.",
    responses={
        200: {
            "description": "User preferences retrieved successfully",
            "model": List[UsersCollectionResponse]
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def getAllUserPreferences(
    db=Depends(get_database)
):
    """
    Get all user preferences from the users collection.
    
    Returns a list of all user preferences in the database.
    """
    try:
        logger.info("Fetching all user preferences")
        
        # Find all users in MongoDB
        users_cursor = db.users.find({})
        users = await users_cursor.to_list(length=None)
        
        # Convert MongoDB ObjectIds to strings
        for user in users:
            user["id"] = str(user["_id"])
            del user["_id"]
        
        logger.info(f"Found {len(users)} user preferences")
        return [UsersCollectionResponse(**user) for user in users]
        
    except Exception as e:
        logger.error(f"Error fetching all user preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user preferences: {str(e)}"
        )
