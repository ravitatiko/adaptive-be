from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, db: Session):
        self.db = db

    def get_item(self, item_id: int) -> Optional[Item]:
        """Get item by ID."""
        return self.db.query(Item).filter(Item.id == item_id).first()

    def get_items(self, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[Item]:
        """Get list of items."""
        query = self.db.query(Item)
        
        if user_id is not None:
            query = query.filter(Item.owner_id == user_id)
        
        return query.offset(skip).limit(limit).all()

    def create_item(self, item: ItemCreate, owner_id: int) -> Item:
        """Create a new item."""
        db_item = Item(
            title=item.title,
            description=item.description,
            is_active=item.is_active,
            owner_id=owner_id
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def update_item(self, item_id: int, item_update: ItemUpdate) -> Item:
        """Update item."""
        db_item = self.get_item(item_id)
        if not db_item:
            return None

        update_data = item_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)

        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def delete_item(self, item_id: int) -> bool:
        """Delete item."""
        db_item = self.get_item(item_id)
        if not db_item:
            return False

        self.db.delete(db_item)
        self.db.commit()
        return True
