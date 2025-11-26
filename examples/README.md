# Examples

This directory contains example scripts demonstrating various features of the AI Computer Automation framework.

## Available Examples

### 1. Basic Automation (`basic_automation.py`)

A simple example showing how to create and run basic automation tasks.

**Requirements:** None (uses only core framework)

**Run:**
```bash
python examples/basic_automation.py
```

**What it does:**
- Creates simple automation tasks
- Demonstrates task configuration
- Shows basic task execution

### 2. GUI Interaction (`gui_interaction.py`)

Demonstrates GUI automation capabilities using PyAutoGUI.

**Requirements:** `pyautogui`

**Run:**
```bash
pip install pyautogui
python examples/gui_interaction.py
```

**What it does:**
- Shows screen size and mouse position
- Captures screenshots
- Demonstrates safety features (failsafe, pause)

**Safety Notes:**
- FAILSAFE enabled: Move mouse to screen corner to abort
- Automatic pause between actions
- Always review code before running

### 3. AI Decision Making (`ai_decision_making.py`)

Shows how to integrate AI for intelligent decision-making in automation workflows.

**Requirements:** `openai`, `OPENAI_API_KEY` environment variable

**Run:**
```bash
pip install openai
# Set OPENAI_API_KEY in your .env file
python examples/ai_decision_making.py
```

**What it does:**
- Uses OpenAI API for decision making
- Demonstrates AI-powered automation logic
- Shows error handling for API calls

**Notes:**
- Requires valid OpenAI API key
- Uses API credits
- Configurable prompts and models

### 4. Computer Vision (`computer_vision.py`)

Demonstrates computer vision capabilities for automation.

**Requirements:** `opencv-python`, `pillow`, `pyautogui`

**Run:**
```bash
pip install opencv-python pillow pyautogui
python examples/computer_vision.py
```

**What it does:**
- Captures and analyzes screenshots
- Performs color analysis
- Detects edges
- Calculates image statistics

**Privacy Note:** Captures screen content for analysis

## Running Examples

### Method 1: Direct Execution

```bash
# From repository root
python examples/basic_automation.py
```

### Method 2: Module Execution

```bash
# From repository root
python -m examples.basic_automation
```

### Method 3: With Virtual Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run example
python examples/basic_automation.py
```

## Creating Your Own Examples

To create a new example:

1. Create a new Python file in the `examples/` directory
2. Import the automation framework:
   ```python
   from ai_automation import AutomationTask
   ```
3. Create a task class extending `AutomationTask`
4. Implement the `_run()` method
5. Add a `main()` function to run your example
6. Update this README with your example

### Template

```python
"""
Your Example Name

Description of what this example does.
"""

import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_automation import AutomationTask


class YourTask(AutomationTask):
    """Description of your task."""

    def _run(self) -> None:
        """Execute your task logic."""
        print("Your automation logic here")


def main():
    """Run your example."""
    print("Your Example")
    task = YourTask("your_task")
    task.execute()


if __name__ == "__main__":
    main()
```

## Safety Guidelines

When running or creating examples:

- **Review code** before execution
- **Test in safe environment** first
- **Enable failsafe features** for GUI automation
- **Validate inputs** and outputs
- **Monitor execution** for unexpected behavior
- **Use appropriate permissions** (don't run as admin/root unless necessary)
- **Protect sensitive data** (API keys, credentials)

## Common Issues

### Import Errors

```
ModuleNotFoundError: No module named 'ai_automation'
```

**Solution:** Install the package in development mode:
```bash
pip install -e .
```

### Missing Dependencies

```
ModuleNotFoundError: No module named 'pyautogui'
```

**Solution:** Install required dependencies:
```bash
pip install -r requirements.txt
```

### API Key Errors

```
ValueError: OPENAI_API_KEY not found
```

**Solution:** Set up your `.env` file:
```bash
cp .env.example .env
# Edit .env and add your API key
```

## Contributing Examples

We welcome example contributions! Please:

1. Follow the template structure
2. Include clear documentation
3. Add safety warnings if needed
4. Update this README
5. Test thoroughly
6. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for more details.

## Additional Resources

- [Main Documentation](../docs/)
- [API Reference](../docs/api/)
- [Contributing Guide](../CONTRIBUTING.md)
- [Security Policy](../SECURITY.md)
