from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.item import Item, ItemCreate, ItemUpdate
from app.services.item_service import ItemService
from app.api.api_v1.endpoints.auth import get_current_user
from app.models.user import User as UserModel

router = APIRouter()


@router.get("/", response_model=List[Item])
async def read_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get list of items."""
    item_service = ItemService(db)
    items = item_service.get_items(skip=skip, limit=limit, user_id=current_user.id)
    return items


@router.post("/", response_model=Item)
async def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Create a new item."""
    item_service = ItemService(db)
    return item_service.create_item(item, current_user.id)


@router.get("/{item_id}", response_model=Item)
async def read_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get item by ID."""
    item_service = ItemService(db)
    item = item_service.get_item(item_id)
    
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Users can only access their own items unless they're admin
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return item


@router.put("/{item_id}", response_model=Item)
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Update item."""
    item_service = ItemService(db)
    item = item_service.get_item(item_id)
    
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Users can only update their own items unless they're admin
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_item = item_service.update_item(item_id, item_update)
    return updated_item


@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Delete item."""
    item_service = ItemService(db)
    item = item_service.get_item(item_id)
    
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Users can only delete their own items unless they're admin
    if item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    item_service.delete_item(item_id)
    return {"message": "Item deleted successfully"}
