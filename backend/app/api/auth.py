from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token, verify_token
from backend.app.core.schemas import UserCreate, User, Token, UserLogin, APIResponse
from backend.app.models.user import User as UserModel
from backend.app.utils.logger import get_logger
from config.settings import settings
import time

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")
logger = get_logger()

def get_user_by_username(db: Session, username: str):
    """Get user by username."""
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Get user by email."""
    return db.query(UserModel).filter(UserModel.email == email).first()

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user credentials."""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=APIResponse)
async def register_user(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    """Register a new user."""
    start_time = time.time()
    
    try:
        # Check if username already exists
        if get_user_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        if get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = UserModel(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Log registration
        execution_time = int((time.time() - start_time) * 1000)
        logger.log_user_registration(
            user_id=db_user.id,
            username=db_user.username,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            execution_time=execution_time
        )
        
        return APIResponse(
            success=True,
            message="User registered successfully",
            data={"user_id": db_user.id, "username": db_user.username}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(
            error_message=f"Registration failed: {str(e)}",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None, db: Session = Depends(get_db)):
    """Login user and return access token."""
    start_time = time.time()
    
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # Log login
        execution_time = int((time.time() - start_time) * 1000)
        logger.log_user_login(
            user_id=user.id,
            username=user.username,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            execution_time=execution_time
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(
            error_message=f"Login failed: {str(e)}",
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=User)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.post("/verify-token")
async def verify_user_token(token: str = Depends(oauth2_scheme)):
    """Verify if token is valid."""
    try:
        payload = verify_token(token)
        return {"valid": True, "username": payload.get("sub")}
    except HTTPException:
        return {"valid": False}
