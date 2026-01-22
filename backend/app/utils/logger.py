import logging
import sys
import json
from typing import Dict, Any, Optional
from datetime import datetime

class StructuredLogger:
    """
    Advanced structured logging utility with JSON formatting and multiple output options.
    Supports console and file logging with rich contextual information.
    """
    
    def __init__(
        self, 
        name: str, 
        log_level: str = 'INFO', 
        log_file: Optional[str] = None
    ):
        """
        Initialize a structured logger.
        
        Args:
            name (str): Logger name
            log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file (Optional[str]): Path to log file for file logging
        """
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Console handler with JSON formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._JSONFormatter())
        self.logger.addHandler(console_handler)
        
        # Optional file handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(self._JSONFormatter())
            self.logger.addHandler(file_handler)
    
    def _format_log_data(
        self, 
        level: str, 
        message: str, 
        extra: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format log data with structured information.
        
        Args:
            level (str): Log level
            message (str): Log message
            extra (Optional[Dict[str, Any]]): Additional context
        
        Returns:
            Dict[str, Any]: Structured log data
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            'logger_name': self.logger.name
        }
        
        if extra:
            log_data['context'] = extra
        
        return log_data
    
    def debug(
        self, 
        message: str, 
        extra: Optional[Dict[str, Any]] = None
    ):
        """
        Log a debug message.
        
        Args:
            message (str): Debug message
            extra (Optional[Dict[str, Any]]): Additional context
        """
        log_data = self._format_log_data('DEBUG', message, extra)
        self.logger.debug(json.dumps(log_data))
    
    def info(
        self, 
        message: str, 
        extra: Optional[Dict[str, Any]] = None
    ):
        """
        Log an info message.
        
        Args:
            message (str): Info message
            extra (Optional[Dict[str, Any]]): Additional context
        """
        log_data = self._format_log_data('INFO', message, extra)
        self.logger.info(json.dumps(log_data))
    
    def warning(
        self, 
        message: str, 
        extra: Optional[Dict[str, Any]] = None
    ):
        """
        Log a warning message.
        
        Args:
            message (str): Warning message
            extra (Optional[Dict[str, Any]]): Additional context
        """
        log_data = self._format_log_data('WARNING', message, extra)
        self.logger.warning(json.dumps(log_data))
    
    def error(
        self, 
        message: str, 
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False
    ):
        """
        Log an error message.
        
        Args:
            message (str): Error message
            extra (Optional[Dict[str, Any]]): Additional context
            exc_info (bool): Whether to include exception information
        """
        log_data = self._format_log_data('ERROR', message, extra)
        self.logger.error(json.dumps(log_data), exc_info=exc_info)
    
    def critical(
        self, 
        message: str, 
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = True
    ):
        """
        Log a critical message.
        
        Args:
            message (str): Critical message
            extra (Optional[Dict[str, Any]]): Additional context
            exc_info (bool): Whether to include exception information
        """
        log_data = self._format_log_data('CRITICAL', message, extra)
        self.logger.critical(json.dumps(log_data), exc_info=exc_info)
    
    class _JSONFormatter(logging.Formatter):
        """
        Custom JSON log formatter.
        """
        def format(self, record):
            """
            Format log record as JSON.
            
            Args:
                record (logging.LogRecord): Log record to format
            
            Returns:
                str: JSON-formatted log message
            """
            try:
                # Try to parse the message as JSON
                log_data = json.loads(record.msg)
            except (TypeError, json.JSONDecodeError):
                # If not JSON, create a basic log structure
                log_data = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.msg,
                    'logger_name': record.name
                }
            
            return json.dumps(log_data)

# Create a default logger instance
logger = StructuredLogger('restaurantgrader')