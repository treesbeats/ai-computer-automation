"""Main entry point for MouseGPT CLI."""

import sys
import signal
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text

from mousegpt import __version__
from mousegpt.config.settings import Settings, SpeechBackend, AIBackend, configure
from mousegpt.engine import MouseGPTEngine, EngineState


console = Console()


def create_banner() -> Panel:
    """Create the MouseGPT banner."""
    banner_text = """
 __  __                       _____ _____ _____
|  \/  |                     / ____|  __ \_   _|
| \  / | ___  _   _ ___  ___| |  __| |__) || |
| |\/| |/ _ \| | | / __|/ _ \ | |_ |  ___/ | |
| |  | | (_) | |_| \__ \  __/ |__| | |    _| |_
|_|  |_|\___/ \__,_|___/\___|\_____|_|   |_____|

    Voice-Controlled Computer Automation
"""
    return Panel(
        Text(banner_text, style="bold cyan"),
        title=f"[bold white]MouseGPT v{__version__}[/]",
        border_style="cyan",
    )


def print_status(engine: MouseGPTEngine) -> Table:
    """Create a status table."""
    table = Table(title="Engine Status", border_style="cyan")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    stats = engine.get_stats()
    table.add_row("State", stats['state'])
    table.add_row("Commands Executed", str(stats['commands_executed']))
    table.add_row("Commands Failed", str(stats['commands_failed']))
    table.add_row("Last Command", stats['last_command'] or "None")

    return table


@click.group()
@click.version_option(version=__version__)
def cli():
    """MouseGPT - Voice-controlled computer automation."""
    pass


@cli.command()
@click.option(
    '--speech-backend',
    type=click.Choice(['google', 'whisper_api', 'whisper_local', 'sphinx', 'windows_sapi', 'windows_voice_access']),
    default='google',
    help='Speech recognition backend to use',
)
@click.option(
    '--ai-backend',
    type=click.Choice(['rule_based', 'openai']),
    default='rule_based',
    help='AI backend for command parsing',
)
@click.option(
    '--openai-key',
    envvar='OPENAI_API_KEY',
    help='OpenAI API key (for whisper_api or openai backends)',
)
@click.option(
    '--wake-word',
    default='hey mouse',
    help='Wake word to activate listening',
)
@click.option(
    '--no-wake-word',
    is_flag=True,
    help='Disable wake word (always listening)',
)
@click.option(
    '--no-tts',
    is_flag=True,
    help='Disable text-to-speech feedback',
)
@click.option(
    '--debug',
    is_flag=True,
    help='Enable debug mode',
)
def start(
    speech_backend: str,
    ai_backend: str,
    openai_key: Optional[str],
    wake_word: str,
    no_wake_word: bool,
    no_tts: bool,
    debug: bool,
):
    """Start MouseGPT and begin listening for voice commands."""
    console.print(create_banner())

    # Configure settings
    settings = configure(
        speech_backend=SpeechBackend(speech_backend),
        ai_backend=AIBackend(ai_backend),
        openai_api_key=openai_key,
        wake_word=wake_word if not no_wake_word else None,
        wake_word_enabled=not no_wake_word,
        tts_enabled=not no_tts,
        debug=debug,
    )

    # Show configuration
    config_table = Table(title="Configuration", border_style="cyan")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    config_table.add_row("Speech Backend", speech_backend)
    config_table.add_row("AI Backend", ai_backend)
    config_table.add_row("Wake Word", wake_word if not no_wake_word else "Disabled")
    config_table.add_row("TTS", "Enabled" if not no_tts else "Disabled")
    config_table.add_row("Debug", "Yes" if debug else "No")
    console.print(config_table)

    # Create engine
    engine = MouseGPTEngine(settings)

    # Setup signal handlers
    def signal_handler(sig, frame):
        console.print("\n[yellow]Shutting down...[/]")
        engine.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Setup callbacks
    def on_command(text: str):
        console.print(f"[cyan]Command:[/] {text}")

    def on_state_change(state: EngineState):
        if state == EngineState.LISTENING:
            console.print("[green]Listening...[/]")
        elif state == EngineState.PROCESSING:
            console.print("[yellow]Processing...[/]")

    engine.on_command(on_command)
    engine.on_state_change(on_state_change)

    try:
        # Start engine
        engine.start()

        console.print("\n[bold green]MouseGPT is running![/]")
        console.print("[dim]Press Ctrl+C to stop[/]\n")

        if not no_wake_word:
            console.print(f"[cyan]Say '{wake_word}' followed by your command[/]")
        else:
            console.print("[cyan]Speak your command[/]")

        # Main loop
        while engine.state != EngineState.STOPPED:
            result = engine.listen_once()
            if result:
                if result.success:
                    console.print(f"[green]{result.message}[/]")
                else:
                    console.print(f"[red]Error: {result.error}[/]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/]")
    finally:
        engine.stop()
        console.print("[bold cyan]MouseGPT stopped[/]")


@cli.command()
@click.argument('command', nargs=-1)
@click.option('--debug', is_flag=True, help='Enable debug mode')
def run(command: tuple, debug: bool):
    """Run a single command without voice input."""
    if not command:
        console.print("[red]Please provide a command[/]")
        return

    command_text = ' '.join(command)
    console.print(f"[cyan]Executing:[/] {command_text}")

    settings = configure(
        tts_enabled=False,
        debug=debug,
    )

    engine = MouseGPTEngine(settings)

    try:
        result = engine.process_command(command_text)

        if result.success:
            console.print(f"[green]Success:[/] {result.message}")
        else:
            console.print(f"[red]Failed:[/] {result.error}")

    except Exception as e:
        console.print(f"[red]Error:[/] {e}")


@cli.command()
def devices():
    """List available input devices."""
    console.print("[bold cyan]Available Microphones:[/]\n")

    try:
        from mousegpt.speech.recognizer import SpeechRecognizer

        mics = SpeechRecognizer.list_microphones()

        if mics:
            table = Table(border_style="cyan")
            table.add_column("Index", style="cyan")
            table.add_column("Name", style="green")

            for mic in mics:
                table.add_row(str(mic['index']), mic['name'])

            console.print(table)
        else:
            console.print("[yellow]No microphones found[/]")

    except Exception as e:
        console.print(f"[red]Error listing microphones:[/] {e}")


@cli.command()
def commands():
    """List available voice commands."""
    console.print(create_banner())
    console.print("\n[bold cyan]Available Voice Commands:[/]\n")

    commands_info = [
        ("Mouse Commands", [
            ("click", "Click at current position or target"),
            ("double click", "Double click"),
            ("right click", "Right click for context menu"),
            ("move to [x, y]", "Move mouse to coordinates"),
            ("move [direction]", "Move mouse in a direction (up/down/left/right)"),
            ("scroll up/down", "Scroll the page"),
            ("drag to [x, y]", "Drag from current position to target"),
        ]),
        ("Keyboard Commands", [
            ("type [text]", "Type the specified text"),
            ("press [key]", "Press a key (enter, tab, escape, etc.)"),
            ("copy/paste/cut", "Clipboard operations"),
            ("undo/redo", "Undo or redo last action"),
            ("save", "Save current document"),
            ("select all", "Select all content"),
        ]),
        ("Application Commands", [
            ("open [app]", "Open an application"),
            ("close [app]", "Close an application"),
            ("switch to [app]", "Switch to an application"),
        ]),
        ("Other Commands", [
            ("screenshot", "Take a screenshot"),
            ("stop/pause", "Pause listening"),
            ("help", "Get help"),
        ]),
    ]

    for category, cmds in commands_info:
        table = Table(title=category, border_style="cyan")
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="white")

        for cmd, desc in cmds:
            table.add_row(cmd, desc)

        console.print(table)
        console.print()


@cli.command()
def test():
    """Test MouseGPT components."""
    console.print(create_banner())
    console.print("\n[bold cyan]Testing MouseGPT Components...[/]\n")

    tests = []

    # Test speech recognition
    console.print("[cyan]Testing speech recognition...[/]")
    try:
        from mousegpt.speech.recognizer import SpeechRecognizer
        recognizer = SpeechRecognizer()
        tests.append(("Speech Recognition", True, "OK"))
    except Exception as e:
        tests.append(("Speech Recognition", False, str(e)))

    # Test mouse controller
    console.print("[cyan]Testing mouse controller...[/]")
    try:
        from mousegpt.controllers.mouse import MouseController
        mouse = MouseController()
        pos = mouse.get_position()
        tests.append(("Mouse Controller", True, f"Position: ({pos.x}, {pos.y})"))
    except Exception as e:
        tests.append(("Mouse Controller", False, str(e)))

    # Test keyboard controller
    console.print("[cyan]Testing keyboard controller...[/]")
    try:
        from mousegpt.controllers.keyboard import KeyboardController
        keyboard = KeyboardController()
        tests.append(("Keyboard Controller", True, "OK"))
    except Exception as e:
        tests.append(("Keyboard Controller", False, str(e)))

    # Test screen controller
    console.print("[cyan]Testing screen controller...[/]")
    try:
        from mousegpt.controllers.screen import ScreenController
        screen = ScreenController()
        size = screen.screen_size
        tests.append(("Screen Controller", True, f"Screen: {size[0]}x{size[1]}"))
    except Exception as e:
        tests.append(("Screen Controller", False, str(e)))

    # Test command parser
    console.print("[cyan]Testing command parser...[/]")
    try:
        from mousegpt.commands.parser import CommandParser
        parser = CommandParser()
        result = parser.parse("click")
        tests.append(("Command Parser", True, f"Parsed: {result.success}"))
    except Exception as e:
        tests.append(("Command Parser", False, str(e)))

    # Display results
    console.print()
    table = Table(title="Test Results", border_style="cyan")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")

    for name, success, details in tests:
        status = "[green]PASS[/]" if success else "[red]FAIL[/]"
        table.add_row(name, status, details)

    console.print(table)

    # Summary
    passed = sum(1 for _, s, _ in tests if s)
    total = len(tests)
    console.print(f"\n[bold]Results: {passed}/{total} tests passed[/]")


@cli.command()
@click.argument('text')
def speak(text: str):
    """Test text-to-speech with the given text."""
    console.print(f"[cyan]Speaking:[/] {text}")

    try:
        from mousegpt.speech.tts import TextToSpeech
        tts = TextToSpeech()
        tts.speak(text, block=True)
        console.print("[green]Done[/]")
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")


@cli.command()
def interactive():
    """Start an interactive text-based command session."""
    console.print(create_banner())
    console.print("\n[bold cyan]Interactive Mode[/]")
    console.print("[dim]Type commands to execute them. Type 'quit' to exit.[/]\n")

    settings = configure(tts_enabled=False)
    engine = MouseGPTEngine(settings)

    while True:
        try:
            command = console.input("[cyan]> [/]")

            if command.lower() in ('quit', 'exit', 'q'):
                break

            if not command.strip():
                continue

            result = engine.process_command(command)

            if result.success:
                console.print(f"[green]{result.message}[/]")
            else:
                console.print(f"[red]Error: {result.error}[/]")

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")

    console.print("[bold cyan]Goodbye![/]")


@cli.command()
def windows():
    """Show Windows-specific features and status."""
    import platform

    console.print(create_banner())
    console.print("\n[bold cyan]Windows Integration Status[/]\n")

    if platform.system() != "Windows":
        console.print("[yellow]Note: Windows-specific features are only available on Windows.[/]")
        console.print("[dim]Current platform: " + platform.system() + "[/]\n")
        return

    tests = []

    # Test Windows SAPI
    console.print("[cyan]Testing Windows SAPI...[/]")
    try:
        from mousegpt.platform.windows.speech_sapi import WindowsSpeechRecognizer, SAPI_AVAILABLE
        if SAPI_AVAILABLE:
            recognizers = WindowsSpeechRecognizer.get_installed_recognizers()
            tests.append(("Windows SAPI", True, f"{len(recognizers)} recognizer(s)"))
        else:
            tests.append(("Windows SAPI", False, "pywin32 not installed"))
    except Exception as e:
        tests.append(("Windows SAPI", False, str(e)))

    # Test Windows Voice Access
    console.print("[cyan]Testing Windows Voice Access...[/]")
    try:
        from mousegpt.platform.windows.voice_access import WindowsVoiceAccessBridge
        bridge = WindowsVoiceAccessBridge()
        info = bridge.get_info()
        status = "Running" if bridge.is_running() else ("Installed" if info.installed else "Not installed")
        tests.append(("Voice Access", info.installed, status))
    except Exception as e:
        tests.append(("Voice Access", False, str(e)))

    # Test Windows UI Automation
    console.print("[cyan]Testing Windows UI Automation...[/]")
    try:
        from mousegpt.platform.windows.ui_automation import WindowsUIAutomation
        uia = WindowsUIAutomation()
        root = uia.get_root_element()
        tests.append(("UI Automation", True, f"Root: {root.name[:30] if root.name else 'Desktop'}"))
    except Exception as e:
        tests.append(("UI Automation", False, str(e)))

    # Test Windows Accessibility
    console.print("[cyan]Testing Windows Accessibility...[/]")
    try:
        from mousegpt.platform.windows.accessibility import WindowsAccessibility
        acc = WindowsAccessibility()
        info = acc.get_accessibility_info()
        features = []
        if info.screen_reader_active:
            features.append("Screen Reader")
        if info.narrator_running:
            features.append("Narrator")
        if info.high_contrast:
            features.append("High Contrast")
        status = ", ".join(features) if features else "Standard"
        tests.append(("Accessibility", True, status))
    except Exception as e:
        tests.append(("Accessibility", False, str(e)))

    # Display results
    console.print()
    table = Table(title="Windows Features", border_style="cyan")
    table.add_column("Feature", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")

    for name, available, details in tests:
        status = "[green]Available[/]" if available else "[red]Unavailable[/]"
        table.add_row(name, status, details)

    console.print(table)

    # Show commands
    console.print("\n[bold cyan]Windows Voice Commands:[/]")
    console.print("[dim]Use these commands with Windows Voice Access integration:[/]\n")

    commands_table = Table(border_style="cyan")
    commands_table.add_column("Command", style="cyan")
    commands_table.add_column("Description", style="white")
    commands_table.add_row("show numbers", "Display click targets as numbers")
    commands_table.add_row("click [number]", "Click the numbered element")
    commands_table.add_row("go to sleep", "Pause voice recognition")
    commands_table.add_row("wake up", "Resume voice recognition")
    commands_table.add_row("what can I say", "Show available commands")
    console.print(commands_table)


@cli.command()
@click.option('--start', 'action', flag_value='start', help='Start Voice Access')
@click.option('--stop', 'action', flag_value='stop', help='Stop Voice Access')
@click.option('--toggle', 'action', flag_value='toggle', help='Toggle Voice Access')
@click.option('--status', 'action', flag_value='status', default=True, help='Show Voice Access status')
def voice_access(action: str):
    """Control Windows Voice Access (Windows 11)."""
    import platform

    if platform.system() != "Windows":
        console.print("[red]Voice Access is only available on Windows 11[/]")
        return

    try:
        from mousegpt.platform.windows.voice_access import WindowsVoiceAccessBridge

        bridge = WindowsVoiceAccessBridge()
        info = bridge.get_info()

        if action == 'status':
            table = Table(title="Voice Access Status", border_style="cyan")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Installed", "Yes" if info.installed else "No")
            table.add_row("Enabled", "Yes" if info.enabled else "No")
            table.add_row("Running", "Yes" if bridge.is_running() else "No")
            table.add_row("State", info.state.value)
            if info.version:
                table.add_row("Version", info.version)
            if info.language:
                table.add_row("Language", info.language)
            console.print(table)

        elif action == 'start':
            console.print("[cyan]Starting Voice Access...[/]")
            if bridge.start():
                console.print("[green]Voice Access started[/]")
            else:
                console.print("[red]Failed to start Voice Access[/]")

        elif action == 'stop':
            console.print("[cyan]Stopping Voice Access...[/]")
            if bridge.stop():
                console.print("[green]Voice Access stopped[/]")
            else:
                console.print("[red]Failed to stop Voice Access[/]")

        elif action == 'toggle':
            running = bridge.toggle()
            if running:
                console.print("[green]Voice Access started[/]")
            else:
                console.print("[yellow]Voice Access stopped[/]")

    except ImportError as e:
        console.print(f"[red]Windows modules not available:[/] {e}")
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")


@cli.command()
@click.argument('name', required=False)
@click.option('--list', 'list_elements', is_flag=True, help='List all clickable elements')
@click.option('--buttons', is_flag=True, help='List all buttons')
@click.option('--inputs', is_flag=True, help='List all input fields')
def find(name: str, list_elements: bool, buttons: bool, inputs: bool):
    """Find UI elements on screen (Windows only)."""
    import platform

    if platform.system() != "Windows":
        console.print("[red]UI Automation is only available on Windows[/]")
        return

    try:
        from mousegpt.platform.windows.ui_automation import WindowsUIAutomation, ControlType

        uia = WindowsUIAutomation()

        if name:
            console.print(f"[cyan]Searching for element: {name}[/]")
            element = uia.find_element_by_name(name, exact_match=False)
            if element:
                table = Table(title=f"Found: {element.name}", border_style="cyan")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="green")
                table.add_row("Name", element.name)
                table.add_row("Type", element.control_type)
                table.add_row("Class", element.class_name)
                table.add_row("Position", f"({element.center[0]}, {element.center[1]})")
                table.add_row("Size", f"{element.width}x{element.height}")
                table.add_row("Enabled", "Yes" if element.is_enabled else "No")
                console.print(table)
            else:
                console.print(f"[yellow]Element not found: {name}[/]")

        elif buttons:
            console.print("[cyan]Finding buttons...[/]")
            elements = uia.find_buttons()
            _display_elements(elements, "Buttons")

        elif inputs:
            console.print("[cyan]Finding input fields...[/]")
            elements = uia.find_edit_boxes()
            _display_elements(elements, "Input Fields")

        elif list_elements:
            console.print("[cyan]Finding clickable elements...[/]")
            elements = []
            for control_type in [ControlType.BUTTON, ControlType.HYPERLINK, ControlType.MENUITEM]:
                elements.extend(uia.find_elements_by_control_type(control_type))
            _display_elements(elements[:50], "Clickable Elements (first 50)")

        else:
            # Show focused element
            element = uia.get_focused_element()
            if element:
                console.print(f"[cyan]Focused Element:[/] {element.name} ({element.control_type})")
            else:
                console.print("[yellow]No focused element detected[/]")

    except ImportError as e:
        console.print(f"[red]Windows modules not available:[/] {e}")
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")


def _display_elements(elements, title: str):
    """Helper to display a list of UI elements."""
    if not elements:
        console.print("[yellow]No elements found[/]")
        return

    table = Table(title=f"{title} ({len(elements)})", border_style="cyan")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Name", style="white", max_width=40)
    table.add_column("Type", style="dim")
    table.add_column("Position", style="green")

    for i, elem in enumerate(elements[:20], 1):
        name = elem.name[:37] + "..." if len(elem.name) > 40 else elem.name
        table.add_row(
            str(i),
            name or "[unnamed]",
            elem.control_type,
            f"({elem.center[0]}, {elem.center[1]})"
        )

    console.print(table)
    if len(elements) > 20:
        console.print(f"[dim]... and {len(elements) - 20} more[/]")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
