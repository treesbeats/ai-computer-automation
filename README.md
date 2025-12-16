# MouseGPT

**Voice-Controlled Computer Automation Engine**

MouseGPT is a complete dictation engine that takes verbal commands from users and controls the mouse, keyboard, and other inputs on a computer. It uses speech recognition to understand natural language commands and translates them into precise computer control actions.

## Features

- **Voice-Controlled Mouse**: Move, click, double-click, right-click, scroll, and drag using voice commands
- **Voice-Controlled Keyboard**: Type text, press keys, and execute keyboard shortcuts
- **Application Control**: Open, close, and switch between applications
- **Screenshot Capture**: Take screenshots via voice command
- **Multiple Speech Backends**: Google Speech Recognition, OpenAI Whisper, or offline CMU Sphinx
- **AI-Powered Command Parsing**: Optional OpenAI GPT integration for understanding complex commands
- **Wake Word Support**: Customizable wake word activation (e.g., "Hey Mouse")
- **Text-to-Speech Feedback**: Audio confirmation of executed commands
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Windows Integration**: Native Windows Voice Access and SAPI support (Windows 10/11)
- **UI Automation**: Find and click UI elements by name (Windows)

## Installation

### Prerequisites

- Python 3.9 or higher
- A working microphone
- System audio libraries (PortAudio)

### Install System Dependencies

**macOS:**
```bash
brew install portaudio
```

**Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

**Windows:**
PyAudio wheels are available for Windows, no additional setup needed.

For Windows-specific features (Voice Access integration, SAPI, UI Automation):
```bash
pip install pywin32 comtypes
```

### Install MouseGPT

```bash
# Clone the repository
git clone https://github.com/treesbeats/ai-computer-automation.git
cd ai-computer-automation

# Install the package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Start Voice Control

```bash
# Start MouseGPT with default settings
mousegpt start

# Start without wake word (always listening)
mousegpt start --no-wake-word

# Start with OpenAI for smarter command parsing
mousegpt start --ai-backend openai --openai-key YOUR_API_KEY

# Start with Whisper for better speech recognition
mousegpt start --speech-backend whisper_api --openai-key YOUR_API_KEY

# Start with Windows SAPI (Windows only)
mousegpt start --speech-backend windows_sapi
```

### Interactive Text Mode

Test commands without voice input:

```bash
mousegpt interactive
```

### Run a Single Command

```bash
mousegpt run "click"
mousegpt run "move to 500 300"
mousegpt run "type hello world"
```

### Test Components

```bash
mousegpt test
```

### List Available Devices

```bash
mousegpt devices
```

### Windows-Specific Commands

```bash
# Check Windows integration status
mousegpt windows

# Control Windows Voice Access (Windows 11)
mousegpt voice-access --status
mousegpt voice-access --start
mousegpt voice-access --stop

# Find UI elements by name
mousegpt find "Submit"
mousegpt find --buttons
mousegpt find --inputs
mousegpt find --list
```

## Voice Commands

### Mouse Commands

| Command | Description |
|---------|-------------|
| `click` | Left click at current position |
| `double click` | Double click |
| `right click` | Right click (context menu) |
| `middle click` | Middle mouse button click |
| `click at 500, 300` | Click at specific coordinates |
| `move to 500, 300` | Move cursor to coordinates |
| `move to center` | Move cursor to screen center |
| `move up/down/left/right` | Move cursor in a direction |
| `move up 100 pixels` | Move cursor 100 pixels up |
| `scroll up` | Scroll up |
| `scroll down 5` | Scroll down 5 units |

### Keyboard Commands

| Command | Description |
|---------|-------------|
| `type hello world` | Type the text "hello world" |
| `press enter` | Press the Enter key |
| `press tab` | Press the Tab key |
| `press escape` | Press the Escape key |
| `press backspace` | Press Backspace |
| `press f5` | Press F5 (function keys) |
| `copy` | Ctrl+C (Cmd+C on Mac) |
| `paste` | Ctrl+V (Cmd+V on Mac) |
| `cut` | Ctrl+X (Cmd+X on Mac) |
| `undo` | Ctrl+Z (Cmd+Z on Mac) |
| `redo` | Ctrl+Y (Cmd+Shift+Z on Mac) |
| `save` | Ctrl+S (Cmd+S on Mac) |
| `select all` | Ctrl+A (Cmd+A on Mac) |
| `find` | Ctrl+F (Cmd+F on Mac) |
| `new tab` | Ctrl+T (Cmd+T on Mac) |
| `close tab` | Ctrl+W (Cmd+W on Mac) |

### Application Commands

| Command | Description |
|---------|-------------|
| `open chrome` | Open Google Chrome |
| `open terminal` | Open terminal/command prompt |
| `close chrome` | Close the Chrome window |
| `switch to firefox` | Switch to Firefox window |

### Utility Commands

| Command | Description |
|---------|-------------|
| `screenshot` | Take a screenshot |
| `stop` / `pause` | Pause listening |
| `help` | Show available commands |

## Configuration

MouseGPT can be configured via environment variables or a `.env` file:

```bash
# Speech Recognition
MOUSEGPT_SPEECH_BACKEND=google          # google, whisper_api, whisper_local, sphinx
MOUSEGPT_SPEECH_LANGUAGE=en-US
MOUSEGPT_SPEECH_TIMEOUT=5.0

# Wake Word
MOUSEGPT_WAKE_WORD="hey mouse"
MOUSEGPT_WAKE_WORD_ENABLED=true

# AI Backend
MOUSEGPT_AI_BACKEND=rule_based          # rule_based, openai
MOUSEGPT_OPENAI_API_KEY=your_key_here
MOUSEGPT_OPENAI_MODEL=gpt-4o-mini

# Mouse Settings
MOUSEGPT_MOUSE_SPEED=1.0
MOUSEGPT_MOUSE_SMOOTH_MOVEMENT=true

# Safety
MOUSEGPT_SAFE_MODE=true
MOUSEGPT_FAILSAFE_ENABLED=true

# TTS
MOUSEGPT_TTS_ENABLED=true
MOUSEGPT_TTS_RATE=175

# Debug
MOUSEGPT_DEBUG=false
```

## Python API

Use MouseGPT programmatically in your Python code:

```python
from mousegpt import MouseGPTEngine, Settings

# Create settings
settings = Settings(
    wake_word_enabled=False,
    tts_enabled=False,
)

# Create engine
engine = MouseGPTEngine(settings)

# Process commands directly
result = engine.process_command("click")
print(f"Success: {result.success}, Message: {result.message}")

# Use individual controllers
engine.mouse.move_to(500, 300)
engine.mouse.click()
engine.keyboard.type_text("Hello, World!")
engine.keyboard.hotkey('ctrl', 's')

# Take a screenshot
path = engine.screen.screenshot_to_file()
print(f"Screenshot saved to: {path}")
```

### Continuous Listening

```python
from mousegpt import MouseGPTEngine

engine = MouseGPTEngine()

# Register callbacks
@engine.on_command
def handle_command(text):
    print(f"Received: {text}")

@engine.on_action
def handle_action(result):
    print(f"Executed: {result.action_type}")

# Start listening
engine.start()
engine.listen_continuous()
```

## Architecture

```
mousegpt/
├── __init__.py           # Package exports
├── main.py               # CLI entry point
├── engine.py             # Main orchestration engine
├── config/
│   └── settings.py       # Configuration management
├── speech/
│   ├── recognizer.py     # Speech recognition
│   └── tts.py            # Text-to-speech
├── commands/
│   ├── parser.py         # Natural language parsing
│   └── registry.py       # Command registration
├── controllers/
│   ├── mouse.py          # Mouse control
│   ├── keyboard.py       # Keyboard control
│   └── screen.py         # Screen utilities
└── utils/
    └── helpers.py        # Utility functions
```

## Extending MouseGPT

### Adding Custom Commands

```python
from mousegpt.commands.registry import get_registry, Command, CommandCategory

registry = get_registry()

# Using decorator
@registry.command(
    name="my_command",
    patterns=[r"do something (.+)"],
    category=CommandCategory.CUSTOM,
    description="Do something custom",
)
def my_handler(target):
    print(f"Doing something with: {target}")

# Or register manually
def another_handler(params):
    return {"success": True}

command = Command(
    name="another_command",
    patterns=[r"another (.+)"],
    handler=another_handler,
    category=CommandCategory.CUSTOM,
)
registry.register(command)
```

## Troubleshooting

### No Microphone Found

Make sure your microphone is connected and properly configured in your system settings. Run `mousegpt devices` to list available microphones.

### Speech Not Recognized

- Speak clearly and at a moderate pace
- Reduce background noise
- Try adjusting the energy threshold in settings
- Try a different speech backend

### PyAudio Installation Issues

On some systems, PyAudio may require additional setup:

```bash
# macOS
brew install portaudio
pip install pyaudio

# Ubuntu
sudo apt-get install portaudio19-dev
pip install pyaudio

# Windows (if wheel fails)
pip install pipwin
pipwin install pyaudio
```

### Commands Not Executing

- Check that you're using the correct wake word (if enabled)
- Try running in interactive mode to test commands
- Enable debug mode for more detailed logging: `mousegpt start --debug`

## Safety Features

- **Failsafe**: Move your mouse to any corner of the screen to abort all actions
- **Safe Mode**: Confirmation required for potentially destructive actions
- **Action Limits**: Maximum actions per command to prevent runaway loops

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Roadmap

- [ ] Mobile support (iOS/Android via companion app)
- [ ] Vision-based element detection
- [ ] Macro recording and playback
- [ ] Multi-monitor support improvements
- [ ] Custom voice training
- [ ] Plugin system for extensions
