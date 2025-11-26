# Contributing to AI Computer Automation

Thank you for your interest in contributing to AI Computer Automation! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Be respectful, inclusive, and constructive in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a branch for your changes
5. Make your changes
6. Submit a pull request

## How to Contribute

There are many ways to contribute:

- **Report bugs**: Submit detailed bug reports with reproducible steps
- **Suggest features**: Propose new features or enhancements
- **Write code**: Fix bugs, implement features, or improve existing code
- **Improve documentation**: Update or add to documentation
- **Write tests**: Add test coverage for existing or new features
- **Review pull requests**: Help review and provide feedback on PRs

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setup Steps

1. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/ai-computer-automation.git
cd ai-computer-automation
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

5. Create a `.env` file from the example:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications defined in our configuration files.

- **Line length**: 100 characters (configured in `pyproject.toml`)
- **Formatting**: Use `black` for automatic formatting
- **Import sorting**: Use `isort` for organizing imports
- **Linting**: Code must pass `flake8` and `ruff` checks
- **Type hints**: Use type hints where appropriate; check with `mypy`

### Running Code Quality Tools

Before committing, run:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Run linters
flake8 src/
ruff check src/
mypy src/

# Or use the pre-commit hooks
pre-commit run --all-files
```

### Code Structure

- Keep functions focused and concise
- Use descriptive variable and function names
- Add docstrings to all public functions and classes
- Follow the existing project structure

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.

    Longer description if needed, explaining the purpose
    and behavior of the function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this is raised
    """
    pass
```

## Testing Guidelines

### Writing Tests

- Write tests for all new features and bug fixes
- Use `pytest` for testing
- Aim for high test coverage (>80%)
- Test both success and failure cases
- Use fixtures for common test setup

### Test Structure

```python
def test_feature_name():
    """Test description."""
    # Arrange
    setup_data = create_test_data()

    # Act
    result = function_under_test(setup_data)

    # Assert
    assert result == expected_value
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_automation --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run specific test
pytest tests/test_core.py::test_specific_function
```

## Pull Request Process

### Before Submitting

1. **Update your branch** with the latest changes from main:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all tests** and ensure they pass:
   ```bash
   pytest
   ```

3. **Run code quality checks**:
   ```bash
   black src/ tests/
   flake8 src/
   mypy src/
   ```

4. **Update documentation** if you've changed functionality

5. **Add or update tests** for your changes

### Commit Messages

Follow conventional commit format:

```
type(scope): brief description

Longer description if needed, explaining what and why.

Fixes #issue_number
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(ai): add support for Claude API integration

fix(gui): resolve click timing issue on macOS

docs(readme): update installation instructions
```

### Submitting the PR

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a pull request on GitHub

3. Fill out the PR template with:
   - Clear description of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (if applicable)

4. Ensure CI checks pass

5. Respond to review feedback

### PR Review Process

- Maintainers will review your PR
- Address any requested changes
- Once approved, a maintainer will merge your PR
- Your contribution will be included in the next release

## Reporting Bugs

### Before Reporting

- Check if the bug has already been reported in [Issues](https://github.com/treesbeats/ai-computer-automation/issues)
- Verify the bug exists in the latest version
- Collect relevant information about your environment

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Step one
2. Step two
3. Error occurs

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment:**
- OS: [e.g., Windows 11, macOS 14, Ubuntu 22.04]
- Python version: [e.g., 3.11.5]
- Package version: [e.g., 0.1.0]

**Additional context**
Any other relevant information, logs, or screenshots.
```

## Suggesting Enhancements

We welcome feature suggestions! Please:

1. Check if the feature has already been suggested
2. Clearly describe the feature and its use case
3. Explain why it would be valuable
4. Provide examples if possible

### Enhancement Template

```markdown
**Feature Description**
Clear description of the proposed feature.

**Use Case**
Explain the problem this feature would solve.

**Proposed Solution**
Describe how you envision this working.

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
Any other relevant information.
```

## Development Workflow

### Branch Naming

Use descriptive branch names:
- `feature/description` - For new features
- `fix/description` - For bug fixes
- `docs/description` - For documentation
- `refactor/description` - For refactoring

### Keeping Your Fork Updated

```bash
# Add upstream remote (one time)
git remote add upstream https://github.com/treesbeats/ai-computer-automation.git

# Fetch and merge updates
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

## Questions?

If you have questions:
- Check the [documentation](docs/)
- Search existing [issues](https://github.com/treesbeats/ai-computer-automation/issues)
- Start a [discussion](https://github.com/treesbeats/ai-computer-automation/discussions)

Thank you for contributing to AI Computer Automation!
