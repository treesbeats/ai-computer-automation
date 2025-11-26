# AI Computer Automation

A Python-based framework for automating computer tasks using AI, enabling intelligent automation of repetitive workflows, GUI interactions, and system operations.

## Overview

This project provides tools and utilities to automate computer tasks with AI-powered decision making. It combines traditional automation techniques with modern AI capabilities to create flexible and intelligent automation solutions.

## Features

- **AI-Powered Task Automation**: Leverage AI to make intelligent decisions during automation workflows
- **GUI Automation**: Interact with graphical user interfaces programmatically
- **Computer Vision**: Identify and interact with UI elements using image recognition
- **Natural Language Processing**: Control automation using natural language commands
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Extensible Architecture**: Easy to add custom automation tasks and AI models

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Platform-Specific Requirements

- **Windows**: No additional requirements
- **macOS**: Accessibility permissions may be required for some automation features
- **Linux**: X11 or Wayland display server

## Installation

1. Clone the repository:
```bash
git clone https://github.com/treesbeats/ai-computer-automation.git
cd ai-computer-automation
```

2. Create and activate a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Quick Start

```python
from ai_automation import AutomationTask

# Create a simple automation task
task = AutomationTask("example_task")

# Run the automation
task.execute()
```

## Usage Examples

See the `examples/` directory for detailed usage examples:

- `examples/basic_automation.py` - Simple automation tasks
- `examples/gui_interaction.py` - GUI element interaction
- `examples/ai_decision_making.py` - AI-powered workflow decisions
- `examples/computer_vision.py` - Image-based automation

## Configuration

Configuration is managed through environment variables. Copy `.env.example` to `.env` and configure:

```env
# AI API Configuration
OPENAI_API_KEY=your_api_key_here

# Automation Settings
AUTOMATION_DELAY=0.5
SCREENSHOT_DIR=./screenshots

# Logging
LOG_LEVEL=INFO
```

## Development

### Setting Up Development Environment

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
pytest
```

4. Run linting:
```bash
flake8 src/
black src/ tests/
mypy src/
```

### Project Structure

```
ai-computer-automation/
├── src/                    # Source code
│   ├── ai_automation/      # Main package
│   │   ├── core/          # Core automation functionality
│   │   ├── ai/            # AI integration modules
│   │   ├── gui/           # GUI automation utilities
│   │   └── vision/        # Computer vision utilities
│   └── __init__.py
├── tests/                  # Test files
├── examples/               # Usage examples
├── docs/                   # Documentation
├── config/                 # Configuration files
├── scripts/                # Utility scripts
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── README.md              # This file
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_automation --cov-report=html

# Run specific test file
pytest tests/test_core.py
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Security

If you discover a security vulnerability, please see [SECURITY.md](SECURITY.md) for reporting instructions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Enhanced AI model integration (GPT-4, Claude, etc.)
- [ ] Web automation capabilities (Selenium/Playwright integration)
- [ ] Voice command support
- [ ] Advanced computer vision features
- [ ] Task scheduling and queuing
- [ ] Cloud deployment options
- [ ] Plugin system for custom extensions
- [ ] GUI application for non-programmers

## Acknowledgments

- Built with Python and modern AI technologies
- Inspired by automation and AI research communities

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/treesbeats/ai-computer-automation/issues)
- Discussions: [GitHub Discussions](https://github.com/treesbeats/ai-computer-automation/discussions)

## FAQ

**Q: What AI models are supported?**
A: Currently supports OpenAI GPT models, with plans to add support for other providers.

**Q: Is this safe to use for sensitive tasks?**
A: Always review automation scripts before running them. Never share API keys or credentials.

**Q: Can I use this for commercial purposes?**
A: Yes, under the terms of the MIT License.

## Status

[![Tests](https://github.com/treesbeats/ai-computer-automation/workflows/tests/badge.svg)](https://github.com/treesbeats/ai-computer-automation/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

Made with ❤️ by the AI Computer Automation team
