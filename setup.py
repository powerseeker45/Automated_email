"""
Setup configuration for Birthday Automation System
"""

import sys
import os
from pathlib import Path

# Ensure setuptools is available
try:
    from setuptools import setup, find_packages
except ImportError:
    print("setuptools is required for installation")
    print("Please install it with: pip install setuptools")
    sys.exit(1)

# Get the current directory
this_directory = Path(__file__).parent

# Read the contents of README file
readme_path = this_directory / "README.md"
if readme_path.exists():
    try:
        long_description = readme_path.read_text(encoding='utf-8')
    except Exception:
        long_description = "Automated birthday image generation and email system for Bharti Airtel"
else:
    long_description = "Automated birthday image generation and email system for Bharti Airtel"

# Define requirements directly (safer than parsing file)
requirements = [
    "pandas>=1.3.0",
    "Pillow>=8.0.0"
]

# Try to read additional requirements from file if it exists
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    try:
        with open(requirements_path, "r", encoding="utf-8") as fh:
            file_requirements = []
            for line in fh:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    # Clean up any extra whitespace or invalid characters
                    clean_line = line.split("#")[0].strip()
                    if clean_line:
                        file_requirements.append(clean_line)
            
            # Only use file requirements if they're valid
            if file_requirements:
                requirements = file_requirements
                
    except Exception as e:
        print(f"Warning: Could not read requirements.txt: {e}")
        print("Using default requirements")

# Package information
PACKAGE_NAME = "birthday-automation-system"
VERSION = "2.0.0"
AUTHOR = "Bharti Airtel"
AUTHOR_EMAIL = "shashwat.airtel@gmail.com"
DESCRIPTION = "Automated birthday image generation and email system for Bharti Airtel"
URL = "https://github.com/bharti-airtel/birthday-automation"

# Validate requirements
validated_requirements = []
for req in requirements:
    if isinstance(req, str) and req.strip():
        validated_requirements.append(req.strip())

print(f"Installing with requirements: {validated_requirements}")

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    
    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Dependencies - use validated requirements
    install_requires=validated_requirements,
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0", 
            "pytest-mock>=3.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "isort>=5.0"
        ],
        "test": [
            "pytest>=6.0",
            "pytest-mock>=3.0",
            "coverage>=5.0"
        ]
    },
    
    # Entry points for command-line scripts
    entry_points={
        "console_scripts": [
            "birthday-automation=main:main"
        ]
    },
    
    # Include additional files
    include_package_data=True,
    package_data={
        "": [
            "*.png",
            "*.jpg", 
            "*.jpeg",
            "*.json",
            "*.yaml",
            "*.yml"
        ]
    },
    
    # Package classification
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: Communications :: Email",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Office/Business :: Human Resources",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: English"
    ],
    
    # Keywords for discovery
    keywords="birthday automation email hr airtel employee",
    
    # Project URLs
    project_urls={
        "Bug Reports": f"{URL}/issues",
        "Source": URL,
        "Documentation": f"{URL}/wiki"
    },
    
    # Ensure wheel is not universal
    zip_safe=False
)

# Print installation success message when setup.py is run directly
if __name__ == "__main__":
    print("=" * 60)
    print("Birthday Automation System - Setup Configuration")
    print("=" * 60)
    print()
    print("Requirements being installed:")
    for req in validated_requirements:
        print(f"  - {req}")
    print()
    print("To install the package:")
    print("  pip install -e .")
    print()
    print("To install with development dependencies:")
    print("  pip install -e .[dev]")
    print()
    print("After installation, you can run:")
    print("  python main.py")
    print()
    print("=" * 60)