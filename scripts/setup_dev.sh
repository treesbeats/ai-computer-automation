#!/bin/bash
# Development environment setup script

set -e

echo "Setting up AI Computer Automation development environment..."
echo

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install package in development mode
echo "Installing package in development mode..."
pip install -e .

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p screenshots
mkdir -p config

# Copy example config if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from example..."
    cp .env.example .env
    echo "⚠ Please edit .env with your API keys"
fi

echo
echo "========================================="
echo "Development environment setup complete!"
echo "========================================="
echo
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Edit .env with your API keys"
echo "3. Run tests: pytest"
echo "4. Run examples: python examples/basic_automation.py"
echo
