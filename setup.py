"""Setup script for AI Computer Automation."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="ai-computer-automation",
    version="0.1.0",
    author="AI Computer Automation Team",
    author_email="",
    description="A Python-based framework for automating computer tasks using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/treesbeats/ai-computer-automation",
    project_urls={
        "Bug Tracker": "https://github.com/treesbeats/ai-computer-automation/issues",
        "Documentation": "https://github.com/treesbeats/ai-computer-automation/docs",
        "Source Code": "https://github.com/treesbeats/ai-computer-automation",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "openai>=1.0.0",
        "anthropic>=0.18.0",
        "pyautogui>=0.9.54",
        "pyperclip>=1.8.2",
        "keyboard>=0.13.5",
        "mouse>=0.7.1",
        "opencv-python>=4.8.0",
        "pillow>=10.0.0",
        "pytesseract>=0.3.10",
        "requests>=2.31.0",
        "pyyaml>=6.0.1",
        "click>=8.1.7",
        "loguru>=0.7.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "isort>=5.12.0",
        ],
        "web": [
            "selenium>=4.15.0",
            "playwright>=1.40.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-automation=ai_automation.cli:main",
        ],
    },
)
