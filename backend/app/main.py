from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from backend.app.api import api_router
from backend.app.core.database import create_tables
from backend.app.utils.logger import setup_logging, get_logger
from config.settings import settings
import uvicorn
import time

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para CV Maker Inteligente com análise NLP e sugestões personalizadas",
    debug=settings.debug
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logger = setup_logging()

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.logger.info("Starting CV Maker API...")
    
    # Create database tables
    create_tables()
    logger.logger.info("Database tables created/verified")
    
    logger.logger.info("CV Maker API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.logger.info("Shutting down CV Maker API...")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.log_error(
        error_message=f"Validation error: {str(exc)}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "details": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.log_error(
        error_message=f"Unhandled exception: {str(exc)}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "details": str(exc) if settings.debug else "An error occurred"
        }
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests."""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.log_api_request(
        endpoint=str(request.url.path),
        method=request.method,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        execution_time=int(process_time * 1000)
    )
    
    return response

# Include API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "api": settings.api_v1_prefix
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }

if __name__ == "__main__":
    import time
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )
