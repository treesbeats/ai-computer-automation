# AI Computer Automation

Voice-controlled automation toolkit for Windows that leverages ChatGPT to interpret natural language commands. The application captures microphone input, converts it to text, requests a structured set of automation actions from ChatGPT, and executes them on the local computer.

## Features

- Hands-free control of mouse movement, clicks, and keyboard input.
- Launch approved desktop applications or open websites by voice.
- Clean, minimal dashboard for starting/stopping the assistant and reviewing live logs.
- Configurable command parser that validates ChatGPT responses before executing them.
- Safety guardrails such as an allow-list for applications and the ability to stop the assistant with a voice command.

## Requirements

- Python 3.9 or newer on Windows.
- [OpenAI API key](https://platform.openai.com/).
- Microphone recognized by the operating system.
- The following Python dependencies (installed automatically when using `pip install`):
  - `openai`
  - `SpeechRecognition`
  - `PyAudio` (Windows wheels are available on PyPI)
  - `pyautogui`

## Installation

```powershell
# Create and activate a virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\activate

# Install the package in editable mode
pip install -e .
```

Set your OpenAI API key for the current session:

```powershell
$Env:OPENAI_API_KEY = "sk-..."
```

## Usage

Run the assistant from a terminal:

```powershell
voice-automation --log-level INFO
```

Optional flags:

- `--config PATH` – Provide a JSON file to override default configuration values such as the wake word, ChatGPT model, or application allow-list.
- `--log-level LEVEL` – Adjust verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- `--dashboard` – Open the graphical dashboard instead of the console loop.

### Dashboard experience

For a point-and-click experience, launch the minimalist dashboard. It shows the current status, provides start/stop controls, and streams the assistant logs in real time:

```powershell
voice-automation --dashboard
```

You can also launch it directly via the convenience entry point:

```powershell
voice-automation-dashboard
```

The dashboard remains responsive while the voice assistant runs on a background thread, making it clear when the system is listening or executing actions.

Once running, speak naturally to issue commands. Example phrases include:

- "Move the mouse to the top left and click twice."
- "Open Notepad and type Hello world."
- "Go to https://openai.com in my browser."

Say "stop listening" to gracefully exit the application. You can change this stop phrase in the configuration.

## Configuration

Create a JSON file such as `config.json` to override defaults:

```json
{
  "speech_recognition": {
    "language": "en-US",
    "stop_phrase": "assistant stop"
  },
  "chatgpt": {
    "model": "gpt-4o-mini",
    "temperature": 0.2
  },
  "execution": {
    "allowed_applications": {
      "notepad": "notepad.exe",
      "vs code": "Code.exe"
    }
  }
}
```

Launch the app with `voice-automation --config config.json` to use these values.

## How It Works

1. **Speech recognition** – The app listens through the default microphone using the `speech_recognition` package and transcribes audio via the Google Web Speech API.
2. **Intent interpretation** – The transcribed text is sent to ChatGPT with instructions to respond using a strict JSON schema of actions.
3. **Validation** – The JSON response is validated to ensure only supported actions and safe parameters are executed.
4. **Automation** – Mouse and keyboard events are performed using `pyautogui`, applications are launched from an allow-list, and websites are opened using the default browser.

## Safety Notes

- The allow-list for applications prevents arbitrary executable launches. Modify it consciously.
- `pyautogui.FAILSAFE` is enabled; move the mouse cursor to the top-left corner to abort execution if needed.
- Running this tool grants voice control over your computer. Test in a controlled environment before relying on it for critical tasks.

## Development

Run static checks or unit tests (if added) using standard Python tooling. Logging statements throughout the modules aid debugging and tracing of voice commands.

## Building a Windows installer

The repository includes automation to produce a polished `VoiceAssistantSetup.exe` installer that bundles the dashboard executable.

1. Install [Inno Setup 6](https://jrsoftware.org/isinfo.php) on your Windows build machine.
2. From a Developer Command Prompt, run:

   ```powershell
   installer\build_installer.bat
   ```

   This script installs build dependencies, generates a standalone dashboard executable with PyInstaller, and then invokes Inno Setup to create the installer.
3. Retrieve the finished installer from `installer\Output\VoiceAssistantSetup.exe` and distribute it to end users.

## Disclaimer

This project provides a template implementation. Hardware, driver support, and ambient noise conditions can affect reliability. Extend and adapt to your environment as necessary.
