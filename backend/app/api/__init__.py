from fastapi import APIRouter
from .auth import router as auth_router
from .cv import router as cv_router
from .users import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(cv_router, prefix="/cv", tags=["cv"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
