import os
import json
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

import google.generativeai as genai
from app.core.mongodb import get_database
from app.core.config import settings


class TranslationService:
    """Service for handling translations using Google Gemini API"""
    
    def __init__(self, db=None):
        self.db = db
        self._assets_collection = None
        self._gemini_model = None
        
        # Initialize Gemini API
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Google Gemini API"""
        try:
            api_key = settings.google_api_key
            if not api_key:
                raise Exception("Google API key not configured in settings")
            
            genai.configure(api_key=api_key)
            self._gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini API initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Gemini API: {e}")
            self._gemini_model = None
    
    @property
    def assets_collection(self):
        """Get assets collection"""
        if self._assets_collection is None:
            if self.db is None:
                self.db = get_database()
            if self.db is None:
                raise Exception("Database connection not available")
            self._assets_collection = self.db.assets
        return self._assets_collection
    
    def _create_translation_prompt(self, content: str, target_language: str) -> str:
        """Create educational content translator prompt"""
        language_names = {
            "hi": "Hindi",
            "te": "Telugu"
        }
        
        target_lang_name = language_names.get(target_language, target_language)
        
        prompt = f"""You are an expert educational content creator and translator specializing in translating educational materials while maintaining their instructional value and clarity.

TASK: Translate the following educational content from English to {target_lang_name}.

TRANSLATION GUIDELINES:
1. Maintain the educational structure and flow
2. Preserve technical terms and concepts accurately
3. Use appropriate educational terminology in {target_lang_name}
4. Keep the same HTML structure and formatting
5. Ensure the translation is natural and easy to understand for students
6. Maintain the same level of formality and tone
7. Do not add extra newlines or line breaks
8. Return clean, properly formatted content without unnecessary whitespace

CONTENT TO TRANSLATE:
{content}

RESPONSE FORMAT:
Return ONLY the translated content in {target_lang_name}. Do not include any explanations, notes, or additional text. The response should be ready to use as educational content. Do not add extra newlines or formatting.

TRANSLATED CONTENT:"""
        return prompt
    
    async def translate_content(self, content: str, target_language: str) -> Optional[str]:
        """Translate content using Gemini API"""
        if not self._gemini_model:
            raise Exception("Gemini API not initialized")
        
        try:
            prompt = self._create_translation_prompt(content, target_language)
            
            # Generate translation
            response = await asyncio.to_thread(
                self._gemini_model.generate_content, 
                prompt
            )
            
            if response and response.text:
                # Clean up the response - remove extra newlines and whitespace
                translated_text = response.text.strip()
                # Remove multiple consecutive newlines and replace with single newline
                import re
                translated_text = re.sub(r'\n\s*\n', '\n', translated_text)
                # Remove leading/trailing whitespace from each line
                lines = [line.strip() for line in translated_text.split('\n')]
                translated_text = '\n'.join(lines)
                return translated_text
            else:
                raise Exception("No translation received from Gemini API")
                
        except Exception as e:
            print(f"❌ Error translating content: {e}")
            raise Exception(f"Translation failed: {str(e)}")
    
    async def get_asset_by_code(self, asset_code: str, language: str = "en") -> Optional[Dict[str, Any]]:
        """Get asset by code and language"""
        try:
            from bson import ObjectId
            
            # Try to convert asset_code to ObjectId if it looks like one
            try:
                asset_code_obj = ObjectId(asset_code)
            except:
                asset_code_obj = asset_code
            
            # First try to find asset with specific language
            asset = await self.assets_collection.find_one({
                "code": asset_code_obj,
                "language": language
            })
            
            # If not found and looking for English, try without language field (legacy assets)
            if not asset and language == "en":
                asset = await self.assets_collection.find_one({
                    "code": asset_code_obj,
                    "$or": [
                        {"language": {"$exists": False}},
                        {"language": "en"}
                    ]
                })
            
            if asset:
                asset["_id"] = str(asset["_id"])
                # Convert code to string if it's an ObjectId
                if isinstance(asset.get("code"), ObjectId):
                    asset["code"] = str(asset["code"])
                # Ensure language field exists
                if "language" not in asset:
                    asset["language"] = "en"
            
            return asset
        except Exception as e:
            print(f"❌ Error getting asset: {e}")
            return None
    
    async def create_translation(self, asset_code: str, target_language: str, content: str) -> Optional[Dict[str, Any]]:
        """Create a new translation for an asset"""
        try:
            # Get the original English asset
            original_asset = await self.get_asset_by_code(asset_code, "en")
            if not original_asset:
                raise Exception(f"Original asset with code '{asset_code}' not found")
            
            # Check if translation already exists
            existing_translation = await self.get_asset_by_code(asset_code, target_language)
            if existing_translation:
                raise Exception(f"Translation for asset '{asset_code}' in language '{target_language}' already exists")
            
            # Translate the content
            translated_content = await self.translate_content(str(original_asset["content"]), target_language)
            
            # Create new asset record for translation
            translation_asset = {
                "name": original_asset["name"],  # Keep original name for now
                "style": original_asset["style"],
                "content": translated_content,
                "code": ObjectId(asset_code),  # Store code as ObjectId
                "language": target_language,
                "source_asset_id": str(original_asset["_id"]),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert translation into database
            result = await self.assets_collection.insert_one(translation_asset)
            
            if result.inserted_id:
                # Get the created translation
                created_translation = await self.assets_collection.find_one({"_id": result.inserted_id})
                if created_translation:
                    created_translation["_id"] = str(created_translation["_id"])
                    # Convert code to string if it's an ObjectId
                    if isinstance(created_translation.get("code"), ObjectId):
                        created_translation["code"] = str(created_translation["code"])
                    # Convert datetime to ISO format
                    if created_translation.get("created_at"):
                        created_translation["created_at"] = created_translation["created_at"].isoformat()
                    if created_translation.get("updated_at"):
                        created_translation["updated_at"] = created_translation["updated_at"].isoformat()
                return created_translation
            else:
                raise Exception("Failed to create translation")
                
        except Exception as e:
            print(f"❌ Error creating translation: {e}")
            raise Exception(f"Translation creation failed: {str(e)}")
    
    async def get_available_translations(self, asset_code: str) -> Dict[str, Any]:
        """Get all available translations for an asset"""
        try:
            from bson import ObjectId
            
            # Try to convert asset_code to ObjectId if it looks like one
            try:
                asset_code_obj = ObjectId(asset_code)
            except:
                asset_code_obj = asset_code
            
            # Get all assets with the same code
            cursor = self.assets_collection.find({"code": asset_code_obj})
            assets = []
            
            async for asset in cursor:
                asset["_id"] = str(asset["_id"])
                assets.append(asset)
            
            # Organize by language
            translations = {}
            for asset in assets:
                lang = asset.get("language", "en")
                # Convert code to string if it's an ObjectId
                code = asset["code"]
                if isinstance(code, ObjectId):
                    code = str(code)
                
                translations[lang] = {
                    "id": asset["_id"],
                    "name": asset["name"],
                    "style": asset["style"],
                    "content": asset["content"],
                    "code": code,
                    "language": lang,
                    "source_asset_id": asset.get("source_asset_id"),
                    "created_at": asset.get("created_at").isoformat() if asset.get("created_at") else None,
                    "updated_at": asset.get("updated_at").isoformat() if asset.get("updated_at") else None
                }
            
            return {
                "asset_code": asset_code,
                "available_languages": list(translations.keys()),
                "translations": translations
            }
            
        except Exception as e:
            print(f"❌ Error getting available translations: {e}")
            return {
                "asset_code": asset_code,
                "available_languages": [],
                "translations": {},
                "error": str(e)
            }
