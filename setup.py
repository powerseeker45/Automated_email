"""
Setup configuration for Birthday Automation System
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements from requirements.txt
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    # Fallback requirements if file doesn't exist
    requirements = [
        "pandas>=1.3.0",
        "Pillow>=8.0.0",
    ]

setup(
    name="birthday-automation-system",
    version="2.0.0",
    author="Bharti Airtel",
    author_email="shashwat.airtel@gmail.com",
    description="Automated birthday image generation and email system for Bharti Airtel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bharti-airtel/birthday-automation",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
        "Natural Language :: English",
    ],
    keywords="birthday automation email hr airtel employee",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-mock>=3.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "isort>=5.0",
            "pre-commit>=2.0",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-mock>=3.0",
            "coverage>=5.0",
            "factory-boy>=3.0",
        ],
        "production": [
            "gunicorn>=20.0",
            "supervisor>=4.0",
        ],
        "monitoring": [
            "prometheus-client>=0.8",
            "sentry-sdk>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "birthday-automation=main:main",
            "birthday-test=tests.test_suite:main",
            "birthday-setup=src.config.settings:create_default_config",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "assets/*.png",
            "assets/*.jpg", 
            "assets/*.jpeg",
            "config/*.json",
            "config/*.yaml",
            "config/*.yml",
        ],
    },
    data_files=[
        ("config", ["config/config.json"]),
        ("assets", ["assets/airtel_logo.png", "assets/cake.png"]),
    ],
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/bharti-airtel/birthday-automation/issues",
        "Source": "https://github.com/bharti-airtel/birthday-automation",
        "Documentation": "https://github.com/bharti-airtel/birthday-automation/wiki",
        "Changelog": "https://github.com/bharti-airtel/birthday-automation/releases",
    },
    
    # Additional metadata
    maintainer="Bharti Airtel IT Team",
    maintainer_email="it-support@airtel.com",
    license="MIT",
    platforms=["any"],
    
    # Custom commands for development
    cmdclass={},
    
    # Options for different build tools
    options={
        "build_exe": {
            "packages": ["pandas", "PIL", "smtplib", "email"],
            "include_files": [
                ("assets/", "assets/"),
                ("config/", "config/"),
            ],
        },
        "bdist_wheel": {
            "universal": False,
        },
    },
)

# Print installation success message
if __name__ == "__main__":
    print("Birthday Automation System setup configuration loaded!")
    print("To install: pip install -e .")
    print("To install with dev dependencies: pip install -e .[dev]")
    print("To run: birthday-automation")