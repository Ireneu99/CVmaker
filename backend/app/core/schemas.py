from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# CV Schemas
class CVBase(BaseModel):
    title: str
    original_text: str
    sector: Optional[str] = None

class CVCreate(CVBase):
    pass

class CVUpdate(BaseModel):
    title: Optional[str] = None
    original_text: Optional[str] = None
    sector: Optional[str] = None

class CVAnalysis(BaseModel):
    analyzed_text: Optional[str] = None
    suggestions: Optional[List[Dict[str, Any]]] = None
    analysis_score: Optional[int] = None
    keywords: Optional[List[str]] = None

class CV(CVBase):
    id: int
    user_id: int
    analyzed_text: Optional[str] = None
    suggestions: Optional[List[Dict[str, Any]]] = None
    pdf_path: Optional[str] = None
    analysis_score: Optional[int] = None
    keywords: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Log Schemas
class LogBase(BaseModel):
    action: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str = "success"
    error_message: Optional[str] = None
    execution_time: Optional[int] = None

class LogCreate(LogBase):
    user_id: Optional[int] = None

class Log(LogBase):
    id: int
    user_id: Optional[int] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Response Schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class CVAnalysisResponse(BaseModel):
    success: bool
    message: str
    cv_id: int
    analysis_score: int
    suggestions: List[Dict[str, Any]]
    keywords: List[str]
