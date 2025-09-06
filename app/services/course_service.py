from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.mongodb import get_database


def convert_objectids_to_strings(data):
    """Recursively convert ObjectId fields to strings in a dictionary"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, (dict, list)):
                convert_objectids_to_strings(value)
    elif isinstance(data, list):
        for item in data:
            convert_objectids_to_strings(item)
    return data
from app.models.course import Course, Asset, Module
from app.schemas.course import CourseCreate, CourseUpdate, AssetCreate


class CourseService:
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self.db = db
        self._courses_collection = None
        self._assets_collection = None
    
    @property
    def courses_collection(self):
        if self._courses_collection is None:
            if self.db is None:
                self.db = get_database()
            if self.db is None:
                raise Exception("Database connection not available. Please ensure MongoDB is running and the app has started properly.")
            self._courses_collection = self.db.courses
        return self._courses_collection
    
    @property
    def assets_collection(self):
        if self._assets_collection is None:
            if self.db is None:
                self.db = get_database()
            if self.db is None:
                raise Exception("Database connection not available. Please ensure MongoDB is running and the app has started properly.")
            self._assets_collection = self.db.assets
        return self._assets_collection
    
    @property
    def user_asset_status_collection(self):
        """Get user asset status collection"""
        if self.db is None:
            self.db = get_database()
        if self.db is None:
            raise Exception("Database connection not available. Please ensure MongoDB is running and the app has started properly.")
        return self.db.userassetstatus

    async def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Get a course by ID"""
        try:
            course = await self.courses_collection.find_one({"_id": ObjectId(course_id)})
            if course:
                course["_id"] = str(course["_id"])
                # Convert ObjectIds in modules to strings
                for module in course.get("modules", []):
                    if "assets" in module:
                        module["assets"] = [str(asset_id) for asset_id in module["assets"]]
                    # Convert any other ObjectId fields in module
                    for key, value in module.items():
                        if isinstance(value, ObjectId):
                            module[key] = str(value)
            return course
        except Exception as e:
            print(f"Error getting course: {e}")
            return None

    async def get_course_with_assets(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Get a course with populated assets"""
        try:
            course = await self.get_course(course_id)
            if not course:
                return None

            # Populate assets for each module
            for module in course.get("modules", []):
                asset_ids = module.get("assets", [])
                assets = []
                
                for asset_id in asset_ids:
                    asset = await self.assets_collection.find_one({"code": ObjectId(asset_id)})
                    if asset:
                        asset["_id"] = str(asset["_id"])
                        # Convert ObjectId fields to strings
                        if isinstance(asset.get("code"), ObjectId):
                            asset["code"] = str(asset["code"])
                        assets.append(asset)
                
                module["assets"] = assets

            # Convert all ObjectIds to strings
            return convert_objectids_to_strings(course)
        except Exception as e:
            print(f"Error getting course with assets: {e}")
            return None

    async def get_course_with_user_progress(self, course_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a course with populated assets and user progress"""
        try:
            course = await self.get_course(course_id)
            if not course:
                return None

            # Get user asset status for this course
            user_status_cursor = self.user_asset_status_collection.find({
                "user": user_id,
                "course": course_id
            })
            user_statuses = {}
            async for status in user_status_cursor:
                user_statuses[status.get("asset")] = status.get("status", "not-started")

            # Populate assets for each module with user progress
            for module in course.get("modules", []):
                asset_ids = module.get("assets", [])
                assets = []
                
                for asset_id in asset_ids:
                    asset = await self.assets_collection.find_one({"_id": ObjectId(asset_id)})
                    if asset:
                        asset["_id"] = str(asset["_id"])
                        # Convert ObjectId fields to strings
                        if isinstance(asset.get("code"), ObjectId):
                            asset["code"] = str(asset["code"])
                        # Add user progress status
                        asset["user_status"] = user_statuses.get(str(asset_id), "not-started")
                        assets.append(asset)
                
                module["assets"] = assets

            # Convert all ObjectIds to strings
            return convert_objectids_to_strings(course)
        except Exception as e:
            print(f"Error getting course with user progress: {e}")
            return None

    async def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get an asset by ID"""
        try:
            asset = await self.assets_collection.find_one({"_id": ObjectId(asset_id)})
            if asset:
                asset["_id"] = str(asset["_id"])
            return asset
        except Exception as e:
            print(f"Error getting asset: {e}")
            return None

    async def create_course(self, course_data: CourseCreate) -> Dict[str, Any]:
        """Create a new course"""
        try:
            course_dict = course_data.dict()
            course_dict["created_at"] = datetime.utcnow()
            course_dict["updated_at"] = datetime.utcnow()
            
            result = await self.courses_collection.insert_one(course_dict)
            course_dict["_id"] = str(result.inserted_id)
            return course_dict
        except Exception as e:
            print(f"Error creating course: {e}")
            raise e

    async def create_asset(self, asset_data: AssetCreate) -> Dict[str, Any]:
        """Create a new asset"""
        try:
            asset_dict = asset_data.dict()
            result = await self.assets_collection.insert_one(asset_dict)
            asset_dict["_id"] = str(result.inserted_id)
            return asset_dict
        except Exception as e:
            print(f"Error creating asset: {e}")
            raise e

    async def update_course(self, course_id: str, course_data: CourseUpdate) -> Optional[Dict[str, Any]]:
        """Update a course"""
        try:
            update_data = course_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.courses_collection.update_one(
                {"_id": ObjectId(course_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_course(course_id)
            return None
        except Exception as e:
            print(f"Error updating course: {e}")
            return None

    async def delete_course(self, course_id: str) -> bool:
        """Delete a course"""
        try:
            result = await self.courses_collection.delete_one({"_id": ObjectId(course_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting course: {e}")
            return False

    async def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset"""
        try:
            result = await self.assets_collection.delete_one({"_id": ObjectId(asset_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting asset: {e}")
            return False

    async def get_courses(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of courses with pagination"""
        try:
            cursor = self.courses_collection.find().skip(skip).limit(limit)
            courses = []
            async for course in cursor:
                course["_id"] = str(course["_id"])
                # Convert ObjectIds in modules to strings
                for module in course.get("modules", []):
                    if "assets" in module:
                        module["assets"] = [str(asset_id) for asset_id in module["assets"]]
                courses.append(course)
            return courses
        except Exception as e:
            print(f"Error getting courses: {e}")
            return []

    async def get_assets(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of assets with pagination"""
        try:
            cursor = self.assets_collection.find().skip(skip).limit(limit)
            assets = []
            async for asset in cursor:
                asset["_id"] = str(asset["_id"])
                assets.append(asset)
            return assets
        except Exception as e:
            print(f"Error getting assets: {e}")
            return []
