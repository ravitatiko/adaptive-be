from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base

class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=False)
    resource_type = Column(String(50), nullable=False)  # e.g., 'video', 'article', 'tutorial'
    difficulty_level = Column(String(20), nullable=False)  # e.g., 'beginner', 'intermediate', 'advanced'
    tags = Column(Text, nullable=True)  # Store as comma-separated string for SQLite compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def __repr__(self):
        return f"<LearningResource(id={self.id}, title='{self.title}')>"
