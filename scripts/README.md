# Scripts

Utility scripts for development and maintenance.

## Available Scripts

### setup_dev.sh

Sets up the development environment.

**Usage:**
```bash
./scripts/setup_dev.sh
```

**What it does:**
- Creates Python virtual environment
- Installs dependencies (production and development)
- Installs package in editable mode
- Sets up pre-commit hooks
- Creates necessary directories
- Copies .env.example to .env

### run_tests.sh

Runs the test suite with coverage reporting.

**Usage:**
```bash
./scripts/run_tests.sh

# Run specific test file
./scripts/run_tests.sh tests/test_core.py

# Run with specific marker
./scripts/run_tests.sh -m unit
```

**What it does:**
- Runs pytest with coverage
- Generates coverage reports (terminal, HTML, XML)
- Displays detailed test output

## Windows Equivalents

For Windows users, use PowerShell or create equivalent `.ps1` scripts, or use the Makefile commands:

```powershell
# Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -e .

# Run tests
pytest --cov=ai_automation --cov-report=html
```

Or use make commands (if you have GNU Make installed):

```bash
make install-dev
make test
```
