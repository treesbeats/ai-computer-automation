"""Command-line interface for AI Computer Automation."""

import sys
import logging
from pathlib import Path
from typing import Optional
import click

from ai_automation import __version__
from ai_automation.utils import setup_logger, load_config


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="Logging level",
)
@click.pass_context
def cli(ctx, config, log_level):
    """AI Computer Automation - Automate tasks with AI."""
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Setup logging
    logger = setup_logger(level=log_level)
    ctx.obj["logger"] = logger

    # Load configuration
    try:
        cfg = load_config(yaml_file=config)
        ctx.obj["config"] = cfg
        logger.debug("Configuration loaded")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)


@cli.command()
@click.argument("task_name")
@click.option("--dry-run", is_flag=True, help="Show what would be done without executing")
@click.pass_context
def run(ctx, task_name, dry_run):
    """Run an automation task."""
    logger = ctx.obj["logger"]
    config = ctx.obj["config"]

    logger.info(f"Running task: {task_name}")

    if dry_run:
        logger.info("DRY RUN MODE - No actions will be executed")
        click.echo(f"Would run task: {task_name}")
        return

    click.echo(f"Executing task: {task_name}")
    # Task execution logic would go here
    logger.info(f"Task {task_name} completed")


@cli.command()
@click.option("--api-key", help="API key to test")
@click.option("--provider", type=click.Choice(["openai", "anthropic"]), default="openai")
@click.pass_context
def test_ai(ctx, api_key, provider):
    """Test AI integration."""
    logger = ctx.obj["logger"]
    config = ctx.obj["config"]

    if not api_key:
        if provider == "openai":
            api_key = config.get("openai_api_key")
        else:
            api_key = config.get("anthropic_api_key")

    if not api_key:
        click.echo(f"Error: No API key found for {provider}", err=True)
        sys.exit(1)

    click.echo(f"Testing {provider} AI integration...")

    try:
        from ai_automation.ai import create_ai_client

        client = create_ai_client(provider=provider, api_key=api_key)
        response = client.complete("Say 'AI integration test successful'")

        click.echo(f"✓ Success! Response: {response}")
        logger.info(f"AI test successful for {provider}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        logger.error(f"AI test failed: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def info(ctx):
    """Show system information."""
    logger = ctx.obj["logger"]

    click.echo(f"AI Computer Automation v{__version__}")
    click.echo()

    # Python version
    import platform

    click.echo(f"Python: {platform.python_version()}")
    click.echo(f"Platform: {platform.system()} {platform.release()}")
    click.echo()

    # Check dependencies
    click.echo("Dependencies:")

    deps = [
        ("pyautogui", "GUI Automation"),
        ("opencv-python", "Computer Vision"),
        ("pytesseract", "OCR"),
        ("openai", "OpenAI Integration"),
        ("anthropic", "Anthropic Integration"),
    ]

    for module, description in deps:
        try:
            __import__(module)
            status = "✓ Installed"
        except ImportError:
            status = "✗ Not installed"

        click.echo(f"  {description:25} {status}")

    logger.debug("System info displayed")


@cli.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
@click.pass_context
def list_tasks(ctx, format):
    """List available automation tasks."""
    logger = ctx.obj["logger"]

    # This would list actual tasks from a registry
    tasks = [
        {"name": "example_task", "description": "An example automation task"},
    ]

    if format == "json":
        import json

        click.echo(json.dumps(tasks, indent=2))
    else:
        click.echo("Available tasks:")
        for task in tasks:
            click.echo(f"  • {task['name']}: {task['description']}")

    logger.debug(f"Listed {len(tasks)} tasks")


@cli.command()
@click.option("--output", type=click.Path(), help="Output file path")
@click.pass_context
def screenshot(ctx, output):
    """Take a screenshot."""
    logger = ctx.obj["logger"]

    try:
        from ai_automation.gui import GUIAutomation

        gui = GUIAutomation()
        img = gui.screenshot()

        if output:
            img.save(output)
            click.echo(f"Screenshot saved to: {output}")
        else:
            output = "screenshot.png"
            img.save(output)
            click.echo(f"Screenshot saved to: {output}")

        logger.info(f"Screenshot saved: {output}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.error(f"Screenshot failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument("config_key")
@click.argument("config_value", required=False)
@click.pass_context
def config(ctx, config_key, config_value):
    """Get or set configuration values."""
    logger = ctx.obj["logger"]
    cfg = ctx.obj["config"]

    if config_value is None:
        # Get value
        value = cfg.get(config_key)
        if value is None:
            click.echo(f"Configuration key '{config_key}' not found")
        else:
            click.echo(f"{config_key} = {value}")
    else:
        # Set value
        cfg.set(config_key, config_value)
        click.echo(f"Set {config_key} = {config_value}")
        logger.info(f"Configuration updated: {config_key}")


def main():
    """Main entry point for CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
