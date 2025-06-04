"""
Logging utilities for the birthday automation system.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        log_format: Custom log format (optional)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Default log format
    if log_format is None:
        log_format = (
            '%(asctime)s - %(name)s - %(levelname)s - '
            '[%(filename)s:%(lineno)d] - %(message)s'
        )
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use rotating file handler to prevent huge log files
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def create_birthday_logger(
    name: str = "birthday_automation",
    log_dir: str = "logs",
    log_level: str = "INFO"
) -> logging.Logger:
    """
    Create a specialized logger for birthday automation.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        log_level: Logging level
        
    Returns:
        Configured logger
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = log_path / f"{name}_{timestamp}.log"
    
    # Custom format for birthday automation
    log_format = (
        '%(asctime)s | %(levelname)-8s | %(name)-20s | '
        '%(funcName)-15s | %(message)s'
    )
    
    return setup_logger(
        log_level=log_level,
        log_file=str(log_file),
        log_format=log_format
    )


class PerformanceLogger:
    """Context manager for logging performance metrics."""
    
    def __init__(self, logger: logging.Logger, operation: str, log_level: int = logging.INFO):
        """
        Initialize performance logger.
        
        Args:
            logger: Logger instance to use
            operation: Name of operation being timed
            log_level: Log level for performance messages
        """
        self.logger = logger
        self.operation = operation
        self.log_level = log_level
        self.start_time = None
    
    def __enter__(self):
        """Start timing the operation."""
        self.start_time = datetime.now()
        self.logger.log(self.log_level, f"Starting {self.operation}...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log results."""
        if self.start_time:
            duration = datetime.now() - self.start_time
            if exc_type is None:
                self.logger.log(
                    self.log_level,
                    f"Completed {self.operation} in {duration.total_seconds():.2f} seconds"
                )
            else:
                self.logger.error(
                    f"Failed {self.operation} after {duration.total_seconds():.2f} seconds: {exc_val}"
                )


class EmailLogger:
    """Specialized logger for email operations."""
    
    def __init__(self, base_logger: logging.Logger):
        """Initialize email logger."""
        self.logger = base_logger
        self.email_stats = {
            'sent': 0,
            'failed': 0,
            'total_attempts': 0
        }
    
    def log_email_attempt(self, recipient: str, employee_name: str):
        """Log email sending attempt."""
        self.email_stats['total_attempts'] += 1
        self.logger.info(f"Attempting to send birthday email to {employee_name} ({recipient})")
    
    def log_email_success(self, recipient: str, employee_name: str):
        """Log successful email sending."""
        self.email_stats['sent'] += 1
        self.logger.info(f"✓ Birthday email sent successfully to {employee_name} ({recipient})")
    
    def log_email_failure(self, recipient: str, employee_name: str, error: str):
        """Log failed email sending."""
        self.email_stats['failed'] += 1
        self.logger.error(f"✗ Failed to send birthday email to {employee_name} ({recipient}): {error}")
    
    def log_email_summary(self):
        """Log summary of email operations."""
        stats = self.email_stats
        success_rate = (stats['sent'] / stats['total_attempts'] * 100) if stats['total_attempts'] > 0 else 0
        
        self.logger.info(
            f"Email Summary - Total: {stats['total_attempts']}, "
            f"Sent: {stats['sent']}, Failed: {stats['failed']}, "
            f"Success Rate: {success_rate:.1f}%"
        )
    
    def reset_stats(self):
        """Reset email statistics."""
        self.email_stats = {'sent': 0, 'failed': 0, 'total_attempts': 0}


class ImageLogger:
    """Specialized logger for image operations."""
    
    def __init__(self, base_logger: logging.Logger):
        """Initialize image logger."""
        self.logger = base_logger
        self.image_stats = {
            'generated': 0,
            'saved': 0,
            'failed': 0
        }
    
    def log_image_generation(self, employee_name: str, success: bool, file_path: str = None):
        """Log image generation result."""
        if success:
            self.image_stats['generated'] += 1
            self.logger.info(f"✓ Generated birthday image for {employee_name}")
            if file_path:
                self.image_stats['saved'] += 1
                self.logger.info(f"✓ Saved image to: {file_path}")
        else:
            self.image_stats['failed'] += 1
            self.logger.error(f"✗ Failed to generate birthday image for {employee_name}")
    
    def log_image_summary(self):
        """Log summary of image operations."""
        stats = self.image_stats
        self.logger.info(
            f"Image Summary - Generated: {stats['generated']}, "
            f"Saved: {stats['saved']}, Failed: {stats['failed']}"
        )
    
    def reset_stats(self):
        """Reset image statistics."""
        self.image_stats = {'generated': 0, 'saved': 0, 'failed': 0}


def log_system_info(logger: logging.Logger):
    """Log system information for debugging."""
    import platform
    import sys
    from pathlib import Path
    
    logger.info("="*50)
    logger.info("BIRTHDAY AUTOMATION SYSTEM STARTUP")
    logger.info("="*50)
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Working Directory: {Path.cwd()}")
    logger.info(f"Script Path: {Path(__file__).parent if __name__ != '__main__' else 'N/A'}")
    logger.info("="*50)


def log_configuration(logger: logging.Logger, config_dict: dict):
    """
    Log configuration settings (with sensitive data masked).
    
    Args:
        logger: Logger instance
        config_dict: Configuration dictionary
    """
    logger.info("Current Configuration:")
    logger.info("-" * 30)
    
    # Sensitive keys to mask
    sensitive_keys = {'password', 'email_password', 'smtp_password', 'token', 'key', 'secret'}
    
    for key, value in config_dict.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            logger.info(f"  {key}: {'*' * 8}")
        else:
            logger.info(f"  {key}: {value}")
    
    logger.info("-" * 30)


class LogRotationHelper:
    """Helper for managing log file rotation and cleanup."""
    
    def __init__(self, log_directory: str = "logs"):
        """Initialize log rotation helper."""
        self.log_dir = Path(log_directory)
        self.log_dir.mkdir(exist_ok=True)
    
    def cleanup_old_logs(self, days_to_keep: int = 30, pattern: str = "*.log"):
        """
        Clean up log files older than specified days.
        
        Args:
            days_to_keep: Number of days of logs to keep
            pattern: File pattern to match for cleanup
        """
        import time
        
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        cleaned_count = 0
        
        for log_file in self.log_dir.glob(pattern):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    cleaned_count += 1
                except OSError:
                    pass  # Ignore files that can't be deleted
        
        return cleaned_count
    
    def get_log_files_info(self):
        """Get information about existing log files."""
        log_files = []
        total_size = 0
        
        for log_file in self.log_dir.glob("*.log*"):
            file_size = log_file.stat().st_size
            file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            log_files.append({
                'name': log_file.name,
                'size': file_size,
                'size_mb': file_size / 1024 / 1024,
                'modified': file_mtime,
                'path': str(log_file)
            })
            total_size += file_size
        
        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: x['modified'], reverse=True)
        
        return {
            'files': log_files,
            'total_count': len(log_files),
            'total_size_mb': total_size / 1024 / 1024
        }


# Context manager for temporary log level changes
class TemporaryLogLevel:
    """Context manager for temporarily changing log level."""
    
    def __init__(self, logger: logging.Logger, temp_level: str):
        """
        Initialize temporary log level manager.
        
        Args:
            logger: Logger to modify
            temp_level: Temporary log level
        """
        self.logger = logger
        self.temp_level = getattr(logging, temp_level.upper())
        self.original_level = None
    
    def __enter__(self):
        """Set temporary log level."""
        self.original_level = self.logger.level
        self.logger.setLevel(self.temp_level)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original log level."""
        if self.original_level is not None:
            self.logger.setLevel(self.original_level)


# Example usage and testing
if __name__ == "__main__":
    # Test basic logging setup
    logger = setup_logger(log_level="INFO", log_file="test_birthday.log")
    
    # Test system info logging
    log_system_info(logger)
    
    # Test performance logging
    with PerformanceLogger(logger, "test operation"):
        import time
        time.sleep(1)  # Simulate work
    
    # Test email logger
    email_logger = EmailLogger(logger)
    email_logger.log_email_attempt("test@example.com", "Test User")
    email_logger.log_email_success("test@example.com", "Test User")
    email_logger.log_email_summary()
    
    # Test image logger
    image_logger = ImageLogger(logger)
    image_logger.log_image_generation("Test User", True, "/path/to/image.png")
    image_logger.log_image_summary()
    
    # Test configuration logging
    test_config = {
        'smtp_server': 'smtp.gmail.com',
        'email_password': 'secret123',
        'log_level': 'INFO'
    }
    log_configuration(logger, test_config)
    
    # Test log rotation helper
    rotation_helper = LogRotationHelper()
    log_info = rotation_helper.get_log_files_info()
    logger.info(f"Found {log_info['total_count']} log files, total size: {log_info['total_size_mb']:.2f} MB")
    
    # Test temporary log level
    logger.info("This is at INFO level")
    with TemporaryLogLevel(logger, "DEBUG"):
        logger.debug("This DEBUG message will be shown")
    logger.debug("This DEBUG message will NOT be shown")
    
    logger.info("Logging utilities test completed!")