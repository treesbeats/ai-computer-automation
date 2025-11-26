#!/bin/bash
# Run tests with coverage

set -e

echo "Running AI Computer Automation test suite..."
echo

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run pytest with coverage
pytest --cov=ai_automation \
       --cov-report=term-missing \
       --cov-report=html \
       --cov-report=xml \
       -v \
       "$@"

echo
echo "Test run complete!"
echo "Coverage report generated in htmlcov/index.html"
