import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.log import Log
from config.settings import settings

class DatabaseLogHandler(logging.Handler):
    """Custom logging handler that saves logs to database."""
    
    def __init__(self, db_session_factory):
        super().__init__()
        self.db_session_factory = db_session_factory
    
    def emit(self, record):
        """Emit a log record to the database."""
        try:
            db = self.db_session_factory()
            
            # Create log entry
            log_entry = Log(
                action=getattr(record, 'action', 'system_log'),
                details=getattr(record, 'details', None),
                user_id=getattr(record, 'user_id', None),
                ip_address=getattr(record, 'ip_address', None),
                user_agent=getattr(record, 'user_agent', None),
                status=getattr(record, 'status', 'info'),
                error_message=record.getMessage() if record.levelno >= logging.ERROR else None,
                execution_time=getattr(record, 'execution_time', None)
            )
            
            db.add(log_entry)
            db.commit()
            db.close()
            
        except Exception as e:
            # Fallback to console logging if database logging fails
            print(f"Failed to log to database: {e}")

class CVMakerLogger:
    """Custom logger for CV Maker application."""
    
    def __init__(self, name: str = "cvmaker", db_session_factory=None):
        self.logger = logging.getLogger(name)
        self.db_session_factory = db_session_factory
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with file and database handlers."""
        if self.logger.handlers:
            return  # Logger already configured
        
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory
        log_dir = settings.log_storage_path
        os.makedirs(log_dir, exist_ok=True)
        
        # File handler for all logs
        log_file = os.path.join(log_dir, f"cvmaker_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Error file handler
        error_file = os.path.join(log_dir, f"cvmaker_errors_{datetime.now().strftime('%Y%m%d')}.log")
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO if settings.debug else logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
        
        # Add database handler if available
        if self.db_session_factory:
            db_handler = DatabaseLogHandler(self.db_session_factory)
            db_handler.setLevel(logging.INFO)
            self.logger.addHandler(db_handler)
    
    def log_user_action(self, 
                       action: str, 
                       user_id: Optional[int] = None,
                       details: Optional[Dict[str, Any]] = None,
                       ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None,
                       status: str = "success",
                       execution_time: Optional[int] = None):
        """Log user action with additional context."""
        
        extra = {
            'action': action,
            'user_id': user_id,
            'details': details,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'status': status,
            'execution_time': execution_time
        }
        
        message = f"User action: {action}"
        if user_id:
            message += f" (User ID: {user_id})"
        if details:
            message += f" - Details: {details}"
        
        if status == "error":
            self.logger.error(message, extra=extra)
        elif status == "warning":
            self.logger.warning(message, extra=extra)
        else:
            self.logger.info(message, extra=extra)
    
    def log_cv_upload(self, user_id: int, cv_id: int, filename: str = None, **kwargs):
        """Log CV upload action."""
        details = {'cv_id': cv_id}
        if filename:
            details['filename'] = filename
        
        self.log_user_action(
            action="cv_upload",
            user_id=user_id,
            details=details,
            **kwargs
        )
    
    def log_cv_analysis(self, user_id: int, cv_id: int, score: int, **kwargs):
        """Log CV analysis action."""
        details = {
            'cv_id': cv_id,
            'analysis_score': score
        }
        
        self.log_user_action(
            action="cv_analysis",
            user_id=user_id,
            details=details,
            **kwargs
        )
    
    def log_pdf_generation(self, user_id: int, cv_id: int, pdf_filename: str, **kwargs):
        """Log PDF generation action."""
        details = {
            'cv_id': cv_id,
            'pdf_filename': pdf_filename
        }
        
        self.log_user_action(
            action="pdf_generation",
            user_id=user_id,
            details=details,
            **kwargs
        )
    
    def log_user_registration(self, user_id: int, username: str, **kwargs):
        """Log user registration."""
        details = {
            'username': username
        }
        
        self.log_user_action(
            action="user_registration",
            user_id=user_id,
            details=details,
            **kwargs
        )
    
    def log_user_login(self, user_id: int, username: str, **kwargs):
        """Log user login."""
        details = {
            'username': username
        }
        
        self.log_user_action(
            action="user_login",
            user_id=user_id,
            details=details,
            **kwargs
        )
    
    def log_error(self, error_message: str, user_id: Optional[int] = None, **kwargs):
        """Log error with context."""
        self.log_user_action(
            action="error",
            user_id=user_id,
            details={'error_message': error_message},
            status="error",
            **kwargs
        )
    
    def log_api_request(self, endpoint: str, method: str, user_id: Optional[int] = None, **kwargs):
        """Log API request."""
        details = {
            'endpoint': endpoint,
            'method': method
        }
        
        self.log_user_action(
            action="api_request",
            user_id=user_id,
            details=details,
            **kwargs
        )

# Global logger instance
logger = CVMakerLogger()

def get_logger(name: str = "cvmaker", db_session_factory=None) -> CVMakerLogger:
    """Get logger instance."""
    return CVMakerLogger(name, db_session_factory)

def setup_logging(db_session_factory=None):
    """Setup application logging."""
    global logger
    logger = CVMakerLogger("cvmaker", db_session_factory)
    return logger
