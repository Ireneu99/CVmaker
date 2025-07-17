from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Log(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Can be null for system logs
    action = Column(String(100), nullable=False)  # e.g., "cv_upload", "cv_analysis", "pdf_generation"
    details = Column(JSON, nullable=True)  # Store additional details as JSON
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    user_agent = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="success")  # success, error, warning
    error_message = Column(Text, nullable=True)
    execution_time = Column(Integer, nullable=True)  # Time in milliseconds
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="logs")
    
    def __repr__(self):
        return f"<Log(id={self.id}, user_id={self.user_id}, action='{self.action}', status='{self.status}')>"
