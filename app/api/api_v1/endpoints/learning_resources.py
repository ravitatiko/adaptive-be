from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.learning_resource import LearningResource
from app.schemas.learning_resource import LearningResourceCreate, LearningResource as LearningResourceSchema

router = APIRouter()

@router.post("/learning-resources/", response_model=LearningResourceSchema)
def create_learning_resource(
    resource: LearningResourceCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new learning resource
    """
    db_resource = LearningResource(**resource.dict())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

@router.get("/learning-resources/", response_model=List[LearningResourceSchema])
def read_learning_resources(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Retrieve all learning resources with pagination
    """
    resources = db.query(LearningResource).offset(skip).limit(limit).all()
    return resources

@router.get("/learning-resources/{resource_id}", response_model=LearningResourceSchema)
def read_learning_resource(
    resource_id: int, 
    db: Session = Depends(get_db)
):
    """
    Get a specific learning resource by ID
    """
    db_resource = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
    if db_resource is None:
        raise HTTPException(status_code=404, detail="Learning resource not found")
    return db_resource

@router.put("/learning-resources/{resource_id}", response_model=LearningResourceSchema)
def update_learning_resource(
    resource_id: int, 
    resource: LearningResourceCreate, 
    db: Session = Depends(get_db)
):
    """
    Update a learning resource
    """
    db_resource = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
    if db_resource is None:
        raise HTTPException(status_code=404, detail="Learning resource not found")
    
    for key, value in resource.dict().items():
        setattr(db_resource, key, value)
    
    db.commit()
    db.refresh(db_resource)
    return db_resource

@router.delete("/learning-resources/{resource_id}")
def delete_learning_resource(
    resource_id: int, 
    db: Session = Depends(get_db)
):
    """
    Delete a learning resource
    """
    db_resource = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
    if db_resource is None:
        raise HTTPException(status_code=404, detail="Learning resource not found")
    
    db.delete(db_resource)
    db.commit()
    return {"message": "Learning resource deleted successfully"}
