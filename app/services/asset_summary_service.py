import asyncio
import re
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

import google.generativeai as genai
from app.core.mongodb import get_database
from app.core.config import settings


class AssetSummaryService:
    def __init__(self, db=None):
        self.db = db
        self._assets_collection = None
        self._gemini_model = None
        self._initialize_gemini()

    @property
    def assets_collection(self):
        """Get assets collection"""
        if self.db is None:
            self.db = get_database()
        if self.db is None:
            raise Exception("Database connection not available. Please ensure MongoDB is running and the app has started properly.")
        return self.db.assets

    def _initialize_gemini(self):
        """Initialize Google Gemini API"""
        try:
            api_key = settings.google_api_key
            if not api_key:
                raise Exception("Google API key not configured in settings")
            
            genai.configure(api_key=api_key)
            self._gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini API initialized successfully for asset summary generation")
        except Exception as e:
            print(f"❌ Error initializing Gemini API for asset summary: {e}")
            self._gemini_model = None

    def _create_summary_prompt(self, content: str) -> str:
        """Create a prompt for generating educational content summaries"""
        prompt = f"""You are an expert educational content analyst specializing in creating concise, informative summaries of educational materials.

TASK: Generate a comprehensive summary of the following educational content.

SUMMARY GUIDELINES:
1. Extract the main learning objectives and key concepts
2. Identify the most important information students should remember
3. Highlight practical applications or examples if present
4. Keep the summary concise but comprehensive (2-4 sentences)
5. Use clear, educational language appropriate for students
6. Focus on the core educational value and takeaways
7. Do not include HTML tags or formatting in the summary
8. Write in a professional, instructional tone

CONTENT TO SUMMARIZE:
{content}

RESPONSE FORMAT:
Return ONLY the summary text. Do not include any explanations, notes, or additional text. The response should be a clean, standalone summary ready for educational use.

SUMMARY:"""
        return prompt

    async def generate_summary(self, content: str) -> Optional[str]:
        """Generate summary using Gemini API"""
        if not self._gemini_model:
            raise Exception("Gemini API not initialized")
        
        try:
            prompt = self._create_summary_prompt(content)
            response = await asyncio.to_thread(
                self._gemini_model.generate_content, 
                prompt
            )
            
            if response and response.text:
                summary = response.text.strip()
                # Clean up the summary
                summary = re.sub(r'\n\s*\n', ' ', summary)
                summary = ' '.join(summary.split())
                return summary
            else:
                raise Exception("No summary received from Gemini API")
                
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            raise Exception(f"Summary generation failed: {str(e)}")

    async def get_asset_by_id(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get asset by ID"""
        try:
            asset = await self.assets_collection.find_one({"_id": ObjectId(asset_id)})
            if asset:
                asset["_id"] = str(asset["_id"])
                # Convert ObjectId fields to strings
                if isinstance(asset.get("code"), ObjectId):
                    asset["code"] = str(asset["code"])
            return asset
        except Exception as e:
            print(f"❌ Error getting asset: {e}")
            return None

    async def update_asset_summary(self, asset_id: str, summary: str) -> Optional[Dict[str, Any]]:
        """Update asset with generated summary"""
        try:
            result = await self.assets_collection.update_one(
                {"_id": ObjectId(asset_id)},
                {
                    "$set": {
                        "summary": summary,
                        "summary_updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                # Return updated asset
                updated_asset = await self.get_asset_by_id(asset_id)
                return updated_asset
            else:
                raise Exception("Failed to update asset summary")
                
        except Exception as e:
            print(f"❌ Error updating asset summary: {e}")
            raise Exception(f"Summary update failed: {str(e)}")

    async def generate_and_update_summary(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Generate summary for an asset and update it in the database"""
        try:
            # Get the asset
            asset = await self.get_asset_by_id(asset_id)
            if not asset:
                raise Exception(f"Asset with ID '{asset_id}' not found")
            
            # Check if asset has content
            content = asset.get("content", "")
            if not content or content.strip() == "":
                raise Exception("Asset has no content to summarize")
            
            # Generate summary
            summary = await self.generate_summary(content)
            if not summary:
                raise Exception("Failed to generate summary")
            
            # Update asset with summary
            updated_asset = await self.update_asset_summary(asset_id, summary)
            return updated_asset
            
        except Exception as e:
            print(f"❌ Error in generate_and_update_summary: {e}")
            raise Exception(f"Summary generation and update failed: {str(e)}")
