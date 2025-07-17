from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.core.schemas import CVCreate, CV, CVUpdate, CVAnalysisResponse, APIResponse
from backend.app.models.cv import CV as CVModel
from backend.app.models.user import User as UserModel
from backend.app.api.auth import get_current_user
from backend.app.services.cv_analyzer import CVAnalyzer
from backend.app.services.pdf_generator import PDFGenerator
from backend.app.utils.logger import get_logger
from config.settings import settings
import time
import os

router = APIRouter()
logger = get_logger()

# Initialize services
cv_analyzer = CVAnalyzer()
pdf_generator = PDFGenerator(settings.pdf_storage_path)

@router.post("/upload", response_model=APIResponse)
async def upload_cv(
    cv_data: CVCreate,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and create a new CV."""
    start_time = time.time()
    
    try:
        # Create CV record
        db_cv = CVModel(
            user_id=current_user.id,
            title=cv_data.title,
            original_text=cv_data.original_text,
            sector=cv_data.sector
        )
        
        db.add(db_cv)
        db.commit()
        db.refresh(db_cv)
        
        # Log CV upload
        execution_time = int((time.time() - start_time) * 1000)
        logger.log_cv_upload(
            user_id=current_user.id,
            cv_id=db_cv.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            execution_time=execution_time
        )
        
        return APIResponse(
            success=True,
            message="CV uploaded successfully",
            data={"cv_id": db_cv.id, "title": db_cv.title}
        )
        
    except Exception as e:
        logger.log_error(
            error_message=f"CV upload failed: {str(e)}",
            user_id=current_user.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload CV"
        )

@router.post("/{cv_id}/analyze", response_model=CVAnalysisResponse)
async def analyze_cv(
    cv_id: int,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze CV and provide suggestions."""
    start_time = time.time()
    
    try:
        # Get CV
        cv = db.query(CVModel).filter(
            CVModel.id == cv_id,
            CVModel.user_id == current_user.id
        ).first()
        
        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        # Analyze CV
        analysis_result = cv_analyzer.analyze_cv(cv.original_text, cv.sector)
        
        # Update CV with analysis results
        cv.analyzed_text = analysis_result['analyzed_text']
        cv.suggestions = analysis_result['suggestions']
        cv.analysis_score = analysis_result['analysis_score']
        cv.keywords = analysis_result['keywords']
        
        db.commit()
        
        # Log analysis
        execution_time = int((time.time() - start_time) * 1000)
        logger.log_cv_analysis(
            user_id=current_user.id,
            cv_id=cv.id,
            score=analysis_result['analysis_score'],
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            execution_time=execution_time
        )
        
        return CVAnalysisResponse(
            success=True,
            message="CV analyzed successfully",
            cv_id=cv.id,
            analysis_score=analysis_result['analysis_score'],
            suggestions=analysis_result['suggestions'],
            keywords=analysis_result['keywords']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(
            error_message=f"CV analysis failed: {str(e)}",
            user_id=current_user.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze CV"
        )

@router.post("/{cv_id}/generate-pdf", response_model=APIResponse)
async def generate_cv_pdf(
    cv_id: int,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate PDF from CV."""
    start_time = time.time()
    
    try:
        # Get CV
        cv = db.query(CVModel).filter(
            CVModel.id == cv_id,
            CVModel.user_id == current_user.id
        ).first()
        
        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        # Prepare CV data
        cv_data = {
            'original_text': cv.original_text,
            'analyzed_text': cv.analyzed_text,
            'title': cv.title
        }
        
        user_data = {
            'username': current_user.username,
            'email': current_user.email,
            'full_name': current_user.full_name
        }
        
        # Generate PDF
        pdf_filename = pdf_generator.generate_cv_pdf(cv_data, user_data)
        
        # Update CV with PDF path
        cv.pdf_path = pdf_filename
        db.commit()
        
        # Log PDF generation
        execution_time = int((time.time() - start_time) * 1000)
        logger.log_pdf_generation(
            user_id=current_user.id,
            cv_id=cv.id,
            pdf_filename=pdf_filename,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            execution_time=execution_time
        )
        
        return APIResponse(
            success=True,
            message="PDF generated successfully",
            data={"pdf_filename": pdf_filename, "cv_id": cv.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(
            error_message=f"PDF generation failed: {str(e)}",
            user_id=current_user.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF"
        )

@router.get("/{cv_id}/download-pdf")
async def download_cv_pdf(
    cv_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download CV PDF."""
    try:
        # Get CV
        cv = db.query(CVModel).filter(
            CVModel.id == cv_id,
            CVModel.user_id == current_user.id
        ).first()
        
        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        if not cv.pdf_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF not generated yet"
            )
        
        pdf_path = pdf_generator.get_pdf_path(cv.pdf_path)
        
        if not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF file not found"
            )
        
        return FileResponse(
            path=pdf_path,
            filename=cv.pdf_path,
            media_type='application/pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(
            error_message=f"PDF download failed: {str(e)}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download PDF"
        )

@router.get("/", response_model=List[CV])
async def get_user_cvs(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all CVs for current user."""
    cvs = db.query(CVModel).filter(
        CVModel.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return cvs

@router.get("/{cv_id}", response_model=CV)
async def get_cv(
    cv_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific CV."""
    cv = db.query(CVModel).filter(
        CVModel.id == cv_id,
        CVModel.user_id == current_user.id
    ).first()
    
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )
    
    return cv

@router.put("/{cv_id}", response_model=APIResponse)
async def update_cv(
    cv_id: int,
    cv_update: CVUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update CV."""
    try:
        cv = db.query(CVModel).filter(
            CVModel.id == cv_id,
            CVModel.user_id == current_user.id
        ).first()
        
        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        # Update fields
        update_data = cv_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cv, field, value)
        
        db.commit()
        
        return APIResponse(
            success=True,
            message="CV updated successfully",
            data={"cv_id": cv.id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(
            error_message=f"CV update failed: {str(e)}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update CV"
        )

@router.delete("/{cv_id}", response_model=APIResponse)
async def delete_cv(
    cv_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete CV."""
    try:
        cv = db.query(CVModel).filter(
            CVModel.id == cv_id,
            CVModel.user_id == current_user.id
        ).first()
        
        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        # Delete PDF file if exists
        if cv.pdf_path:
            pdf_generator.delete_pdf(cv.pdf_path)
        
        # Delete CV record
        db.delete(cv)
        db.commit()
        
        return APIResponse(
            success=True,
            message="CV deleted successfully",
            data={"cv_id": cv_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(
            error_message=f"CV deletion failed: {str(e)}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete CV"
        )
