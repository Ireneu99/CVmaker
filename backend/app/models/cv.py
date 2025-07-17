from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class CV(Base):
    __tablename__ = "cvs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False, default="Meu CV")
    original_text = Column(Text, nullable=False)
    analyzed_text = Column(Text, nullable=True)
    suggestions = Column(JSON, nullable=True)  # Store suggestions as JSON
    pdf_path = Column(String(500), nullable=True)
    analysis_score = Column(Integer, nullable=True)  # Score from 0-100
    keywords = Column(JSON, nullable=True)  # Store keywords as JSON array
    sector = Column(String(100), nullable=True)  # Professional sector
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="cvs")
    
    def __repr__(self):
        return f"<CV(id={self.id}, user_id={self.user_id}, title='{self.title}')>"
