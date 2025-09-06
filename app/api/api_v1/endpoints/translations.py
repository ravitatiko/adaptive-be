from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.core.mongodb import get_database
from app.schemas.translation import TranslationRequest, TranslationResponse, TranslationStatus
from app.services.translation_service import TranslationService
from app.api.api_v1.endpoints.auth import get_current_user
from app.models.user import User as UserModel

router = APIRouter()


@router.post("/translate", response_model=TranslationResponse)
async def translate_asset(
    request: TranslationRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Translate an asset's content to the specified language using Google Gemini API.
    
    - **asset_code**: The code of the asset to translate
    - **target_language**: Target language ("hi" for Hindi, "te" for Telugu)
    - **content**: The content to translate
    """
    # Validate target language
    if request.target_language not in ["hi", "te"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target language must be 'hi' (Hindi) or 'te' (Telugu)"
        )
    
    try:
        db = get_database()
        translation_service = TranslationService(db)
        
        # Create translation
        translation = await translation_service.create_translation(
            asset_code=request.asset_code,
            target_language=request.target_language,
            content=request.content
        )
        
        if not translation:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create translation"
            )
        
        return translation
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/asset/{asset_code}/translations")
async def get_asset_translations(
    asset_code: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get all available translations for a specific asset.
    
    - **asset_code**: The code of the asset to get translations for
    """
    try:
        db = get_database()
        translation_service = TranslationService(db)
        
        # Get available translations
        translations = await translation_service.get_available_translations(asset_code)
        
        return translations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/asset/{asset_code}/language/{language}")
async def get_asset_by_language(
    asset_code: str,
    language: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get a specific asset in a specific language.
    
    - **asset_code**: The code of the asset
    - **language**: The language ("en", "hi", "te")
    """
    # Validate language
    if language not in ["en", "hi", "te"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Language must be 'en' (English), 'hi' (Hindi), or 'te' (Telugu)"
        )
    
    try:
        db = get_database()
        translation_service = TranslationService(db)
        
        # Get asset by code and language
        asset = await translation_service.get_asset_by_code(asset_code, language)
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset with code '{asset_code}' in language '{language}' not found"
            )
        
        return asset
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/translate/batch")
async def translate_multiple_assets(
    requests: list[TranslationRequest],
    current_user: UserModel = Depends(get_current_user)
):
    """
    Translate multiple assets in batch.
    
    - **requests**: List of translation requests
    """
    results = []
    
    for request in requests:
        try:
            # Validate target language
            if request.target_language not in ["hi", "te"]:
                results.append({
                    "asset_code": request.asset_code,
                    "target_language": request.target_language,
                    "status": "error",
                    "error": "Target language must be 'hi' (Hindi) or 'te' (Telugu)"
                })
                continue
            
            db = get_database()
            translation_service = TranslationService(db)
            
            # Create translation
            translation = await translation_service.create_translation(
                asset_code=request.asset_code,
                target_language=request.target_language,
                content=request.content
            )
            
            if translation:
                results.append({
                    "asset_code": request.asset_code,
                    "target_language": request.target_language,
                    "status": "success",
                    "translation": translation
                })
            else:
                results.append({
                    "asset_code": request.asset_code,
                    "target_language": request.target_language,
                    "status": "error",
                    "error": "Failed to create translation"
                })
                
        except Exception as e:
            results.append({
                "asset_code": request.asset_code,
                "target_language": request.target_language,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "total_requests": len(requests),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "results": results
    }
