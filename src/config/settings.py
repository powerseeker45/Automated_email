"""
Configuration management for the birthday automation system.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Config:
    """Configuration class for birthday automation system."""
    
    # File paths
    csv_file: str = "employees.csv"
    custom_base_image: Optional[str] = None
    output_dir: str = "output_img"
    
    # Email settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_user: str = ""
    email_password: str = ""
    
    # Image settings
    image_width: int = 800
    image_height: int = 624
    background_color: str = "#e40000"
    
    # Asset paths
    logo_path: str = "assets/airtel_logo.png"
    cake_path: str = "assets/cake.png"
    
    # Font settings
    font_paths: Dict[str, str] = field(default_factory=lambda: {
        "regular": "arial.ttf",
        "bold": "arialbd.ttf",
        "italic": "ariali.ttf"
    })
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Email template settings
    email_subject_template: str = "🎉 Happy Birthday {first_name}! 🎉"
    sender_signature: str = "CEO, Bharti Airtel"
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file or environment variables."""
        # Load from file if provided
        if config_path and Path(config_path).exists():
            self._load_from_file(config_path)
        
        # Override with environment variables
        self._load_from_env()
        
        # Validate configuration
        self._validate()
    
    def _load_from_file(self, config_path: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            for key, value in config_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ValueError(f"Error loading config file {config_path}: {e}")
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'BIRTHDAY_CSV_FILE': 'csv_file',
            'BIRTHDAY_CUSTOM_IMAGE': 'custom_base_image',
            'BIRTHDAY_OUTPUT_DIR': 'output_dir',
            'SMTP_SERVER': 'smtp_server',
            'SMTP_PORT': 'smtp_port',
            'EMAIL_USER': 'email_user',
            'EMAIL_PASSWORD': 'email_password',
            'LOG_LEVEL': 'log_level',
            'LOG_FILE': 'log_file',
        }
        
        for env_var, attr_name in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                # Convert types as needed
                if attr_name == 'smtp_port':
                    env_value = int(env_value)
                setattr(self, attr_name, env_value)
    
    def _validate(self) -> None:
        """Validate configuration settings."""
        errors = []
        
        if not self.email_user:
            errors.append("Email user is required")
        
        if not self.email_password:
            errors.append("Email password is required")
        
        if not Path(self.csv_file).exists():
            errors.append(f"CSV file not found: {self.csv_file}")
        
        if self.custom_base_image and not Path(self.custom_base_image).exists():
            errors.append(f"Custom base image not found: {self.custom_base_image}")
        
        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(errors))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'csv_file': self.csv_file,
            'custom_base_image': self.custom_base_image,
            'output_dir': self.output_dir,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'email_user': self.email_user,
            'email_password': '***',  # Don't expose password
            'image_width': self.image_width,
            'image_height': self.image_height,
            'background_color': self.background_color,
            'logo_path': self.logo_path,
            'cake_path': self.cake_path,
            'font_paths': self.font_paths,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'email_subject_template': self.email_subject_template,
            'sender_signature': self.sender_signature
        }
    
    def save_to_file(self, config_path: str) -> None:
        """Save current configuration to JSON file."""
        config_dict = self.to_dict()
        # Include password for saving (user's choice to save it)
        config_dict['email_password'] = self.email_password
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=4)


# Default configuration file template
DEFAULT_CONFIG = {
    "csv_file": "employees.csv",
    "custom_base_image": None,
    "output_dir": "output_img",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email_user": "your-email@company.com",
    "email_password": "your-app-password",
    "image_width": 800,
    "image_height": 624,
    "background_color": "#e40000",
    "logo_path": "assets/airtel_logo.png",
    "cake_path": "assets/cake.png",
    "font_paths": {
        "regular": "arial.ttf",
        "bold": "arialbd.ttf",
        "italic": "ariali.ttf"
    },
    "log_level": "INFO",
    "log_file": None,
    "email_subject_template": "🎉 Happy Birthday {first_name}! 🎉",
    "sender_signature": "CEO, Bharti Airtel"
}


def create_default_config(config_path: str = "config.json") -> None:
    """Create a default configuration file."""
    with open(config_path, 'w') as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)
    print(f"Default configuration created at: {config_path}")


if __name__ == "__main__":
    # Create default config file
    create_default_config()