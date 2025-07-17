from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.core.schemas import User, APIResponse
from backend.app.models.user import User as UserModel
from backend.app.models.log import Log as LogModel
from backend.app.api.auth import get_current_user
from backend.app.utils.logger import get_logger

router = APIRouter()
logger = get_logger()

@router.get("/profile", response_model=User)
async def get_user_profile(current_user: UserModel = Depends(get_current_user)):
    """Get current user profile."""
    return current_user

@router.get("/stats", response_model=APIResponse)
async def get_user_stats(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics."""
    try:
        # Count user's CVs
        cv_count = len(current_user.cvs)
        
        # Count user's logs
        log_count = db.query(LogModel).filter(LogModel.user_id == current_user.id).count()
        
        # Get recent activity
        recent_logs = db.query(LogModel).filter(
            LogModel.user_id == current_user.id
        ).order_by(LogModel.timestamp.desc()).limit(10).all()
        
        recent_activity = [
            {
                "action": log.action,
                "timestamp": log.timestamp.isoformat(),
                "status": log.status
            }
            for log in recent_logs
        ]
        
        stats = {
            "cv_count": cv_count,
            "total_actions": log_count,
            "recent_activity": recent_activity,
            "member_since": current_user.created_at.isoformat()
        }
        
        return APIResponse(
            success=True,
            message="User statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.log_error(
            error_message=f"Failed to get user stats: {str(e)}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        )

@router.get("/activity", response_model=APIResponse)
async def get_user_activity(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """Get user activity logs."""
    try:
        logs = db.query(LogModel).filter(
            LogModel.user_id == current_user.id
        ).order_by(LogModel.timestamp.desc()).offset(skip).limit(limit).all()
        
        activity = [
            {
                "id": log.id,
                "action": log.action,
                "details": log.details,
                "status": log.status,
                "timestamp": log.timestamp.isoformat(),
                "execution_time": log.execution_time
            }
            for log in logs
        ]
        
        return APIResponse(
            success=True,
            message="User activity retrieved successfully",
            data={"activity": activity, "total": len(activity)}
        )
        
    except Exception as e:
        logger.log_error(
            error_message=f"Failed to get user activity: {str(e)}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user activity"
        )
