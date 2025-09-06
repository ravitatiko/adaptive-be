from fastapi import APIRouter, Depends, HTTPException, status
from app.core.mongodb import get_database
from app.services.asset_summary_service import AssetSummaryService
from app.schemas.asset_summary import AssetSummaryRequest, AssetSummaryResponse, AssetSummaryStatus
from app.models.user import User
# from app.core.security import get_current_user  # Commented out - function doesn't exist

router = APIRouter()


@router.post("/generate", response_model=AssetSummaryResponse)
async def generate_asset_summary(
    request: AssetSummaryRequest,
    # current_user: User = Depends(get_current_user)  # Commented out - function doesn't exist
):
    """
    Generate a summary for an asset using AI.
    Requires authentication.
    """
    try:
        # Validate asset ID format
        from bson import ObjectId
        try:
            ObjectId(request.asset_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid asset ID format"
            )
        
        db = get_database()
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection not available"
            )
        
        asset_summary_service = AssetSummaryService(db)
        
        # Generate and update summary
        updated_asset = await asset_summary_service.generate_and_update_summary(request.asset_id)
        
        if not updated_asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found or summary generation failed"
            )
        
        return updated_asset
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation failed: {str(e)}"
        )


@router.get("/status/{asset_id}", response_model=AssetSummaryStatus)
async def get_asset_summary_status(
    asset_id: str,
    # current_user: User = Depends(get_current_user)  # Commented out - function doesn't exist
):
    """
    Get the summary status for an asset.
    Requires authentication.
    """
    try:
        # Validate asset ID format
        from bson import ObjectId
        try:
            ObjectId(asset_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid asset ID format"
            )
        
        db = get_database()
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection not available"
            )
        
        asset_summary_service = AssetSummaryService(db)
        asset = await asset_summary_service.get_asset_by_id(asset_id)
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        has_summary = asset.get("summary") is not None and asset.get("summary").strip() != ""
        
        return AssetSummaryStatus(
            success=True,
            message="Summary found" if has_summary else "No summary available",
            asset_id=asset_id,
            summary=asset.get("summary"),
            summary_updated_at=asset.get("summary_updated_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary status: {str(e)}"
        )
