#!/usr/bin/env python3
"""
Basic usage examples for MouseGPT.

This script demonstrates how to use MouseGPT programmatically
for voice-controlled computer automation.
"""

from mousegpt import MouseGPTEngine, Settings
from mousegpt.config.settings import configure


def example_basic_commands():
    """Example: Execute basic commands programmatically."""
    print("=== Basic Command Execution ===\n")

    # Configure with TTS disabled for quiet operation
    settings = configure(
        tts_enabled=False,
        wake_word_enabled=False,
    )

    # Create the engine
    engine = MouseGPTEngine(settings)

    # Execute various commands
    commands = [
        "move to center",
        "click",
        "scroll down 3",
        "screenshot",
    ]

    for cmd in commands:
        print(f"Executing: {cmd}")
        result = engine.process_command(cmd)
        print(f"  Result: {'Success' if result.success else 'Failed'}")
        print(f"  Message: {result.message}\n")


def example_direct_control():
    """Example: Direct mouse and keyboard control."""
    print("=== Direct Controller Access ===\n")

    settings = configure(tts_enabled=False)
    engine = MouseGPTEngine(settings)

    # Get current mouse position
    pos = engine.mouse.get_position()
    print(f"Current mouse position: ({pos.x}, {pos.y})")

    # Get screen size
    width, height = engine.screen.screen_size
    print(f"Screen size: {width}x{height}")

    # Move to center (without executing)
    center_x, center_y = width // 2, height // 2
    print(f"Moving to center: ({center_x}, {center_y})")
    engine.mouse.move_to(center_x, center_y)

    # Get new position
    pos = engine.mouse.get_position()
    print(f"New position: ({pos.x}, {pos.y})")


def example_keyboard_shortcuts():
    """Example: Keyboard shortcuts and typing."""
    print("=== Keyboard Operations ===\n")

    settings = configure(tts_enabled=False)
    engine = MouseGPTEngine(settings)

    # Available shortcuts
    shortcuts = {
        "copy": engine.keyboard.copy,
        "paste": engine.keyboard.paste,
        "cut": engine.keyboard.cut,
        "undo": engine.keyboard.undo,
        "redo": engine.keyboard.redo,
        "save": engine.keyboard.save,
        "select_all": engine.keyboard.select_all,
        "find": engine.keyboard.find,
    }

    print("Available keyboard shortcuts:")
    for name in shortcuts:
        print(f"  - {name}")

    print("\nTo type text: engine.keyboard.type_text('Hello, World!')")
    print("To press a key: engine.keyboard.press('enter')")
    print("To use hotkey: engine.keyboard.hotkey('ctrl', 'shift', 't')")


def example_screenshot():
    """Example: Taking screenshots."""
    print("=== Screenshot Operations ===\n")

    settings = configure(tts_enabled=False)
    engine = MouseGPTEngine(settings)

    # Take a full screenshot
    print("Taking screenshot...")
    path = engine.screen.screenshot_to_file(prefix="example")
    print(f"Screenshot saved to: {path}")

    # Get screen info
    width, height = engine.screen.screen_size
    print(f"\nScreen resolution: {width}x{height}")

    # Check if retina display
    is_retina = engine.screen.is_retina()
    print(f"Retina/HiDPI display: {is_retina}")


def example_callbacks():
    """Example: Using callbacks for event handling."""
    print("=== Event Callbacks ===\n")

    settings = configure(tts_enabled=False)
    engine = MouseGPTEngine(settings)

    # Track commands
    command_log = []

    def on_command(text):
        command_log.append(text)
        print(f"[LOG] Command received: {text}")

    def on_action(result):
        status = "SUCCESS" if result.success else "FAILED"
        print(f"[LOG] Action {status}: {result.action_type}")

    def on_error(error):
        print(f"[LOG] Error: {error}")

    # Register callbacks
    engine.on_command(on_command)
    engine.on_action(on_action)
    engine.on_error(on_error)

    # Execute some commands
    engine.process_command("move to center")
    engine.process_command("click")

    print(f"\nTotal commands logged: {len(command_log)}")


def example_custom_settings():
    """Example: Custom configuration."""
    print("=== Custom Configuration ===\n")

    # Configure with custom settings
    settings = Settings(
        # Speech settings
        speech_language="en-US",
        speech_timeout=10.0,
        wake_word="computer",
        wake_word_enabled=True,

        # Mouse settings
        mouse_speed=1.5,
        mouse_smooth_movement=True,
        mouse_movement_duration=0.3,

        # Keyboard settings
        keyboard_typing_speed=0.03,

        # Safety settings
        safe_mode=True,
        failsafe_enabled=True,

        # Feedback
        tts_enabled=True,
        tts_rate=200,

        # Debug
        debug=True,
    )

    print("Custom settings configured:")
    print(f"  Wake word: '{settings.wake_word}'")
    print(f"  Mouse speed: {settings.mouse_speed}")
    print(f"  TTS rate: {settings.tts_rate} WPM")
    print(f"  Debug mode: {settings.debug}")

    engine = MouseGPTEngine(settings)
    print(f"\nEngine created with custom settings")


def example_command_parsing():
    """Example: Command parsing without execution."""
    print("=== Command Parsing ===\n")

    from mousegpt.commands.parser import CommandParser

    parser = CommandParser()

    test_commands = [
        "click",
        "double click on the button",
        "move to 500, 300",
        "move up 100 pixels",
        "scroll down 5",
        "type hello world",
        "press enter",
        "copy",
        "open chrome",
        "screenshot",
    ]

    for cmd in test_commands:
        result = parser.parse(cmd)
        if result.success:
            action = result.actions[0]
            print(f"'{cmd}'")
            print(f"  -> Type: {action.action_type}")
            print(f"  -> Params: {action.parameters}\n")
        else:
            print(f"'{cmd}'")
            print(f"  -> Failed: {result.error}\n")


if __name__ == "__main__":
    print("MouseGPT Examples\n")
    print("=" * 50)

    # Run examples (comment out ones you don't want to run)

    # Basic command execution
    # example_basic_commands()

    # Direct controller access
    # example_direct_control()

    # Keyboard operations info
    example_keyboard_shortcuts()

    print("\n" + "=" * 50)

    # Screenshot operations
    # example_screenshot()

    # Callback usage
    # example_callbacks()

    # Custom settings
    example_custom_settings()

    print("\n" + "=" * 50)

    # Command parsing
    example_command_parsing()

    print("\nExamples complete!")
