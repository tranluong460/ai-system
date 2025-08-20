"""
Unified error handling utility for the AI Assistant system
"""
import traceback
import logging
from typing import Dict, Any, Optional, Union
from functools import wraps
import json

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, logger_name: str = "ai_assistant"):
        self.logger = logging.getLogger(logger_name)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def safe_execute(self, func, *args, **kwargs) -> Dict[str, Any]:
        """Safely execute a function with error handling"""
        try:
            result = func(*args, **kwargs)
            return {
                "success": True,
                "result": result,
                "error": None
            }
        except Exception as e:
            error_info = {
                "success": False,
                "result": None,
                "error": {
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
            }
            self.logger.error(f"Error in {func.__name__}: {e}")
            return error_info
    
    def format_error_response(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Format error into standardized response"""
        return {
            "success": False,
            "message": f"Lỗi {context}: {str(error)}",
            "error_type": type(error).__name__,
            "details": str(error)
        }
    
    def log_user_action(self, action: str, user_input: str, success: bool = True):
        """Log user actions for debugging"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"USER_ACTION [{status}] {action}: {user_input[:100]}")

def safe_operation(error_message: str = "Operation failed"):
    """Decorator for safe operations with standardized error handling"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = ErrorHandler()
                return error_handler.format_error_response(e, error_message)
        return wrapper
    return decorator

def safe_json_operation(default_value: Any = None):
    """Decorator for JSON operations with fallback"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
                ErrorHandler().logger.warning(f"JSON operation failed in {func.__name__}: {e}")
                return default_value
        return wrapper
    return decorator

def validate_input(validator_func):
    """Decorator to validate input parameters"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                validator_func(*args, **kwargs)
                return func(*args, **kwargs)
            except ValueError as e:
                return {
                    "success": False,
                    "message": f"Invalid input: {str(e)}"
                }
        return wrapper
    return decorator