"""Central configuration management for Notes."""

import json
import os
from pathlib import Path
from typing import Optional

# Default config location
CONFIG_DIR = Path(os.environ.get("NOTES_CONFIG_DIR", "~/.config/notes")).expanduser()
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config_dir() -> Path:
    """Get the config directory, creating if needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def get_config_path() -> Path:
    """Get the path to the config file."""
    return CONFIG_FILE


def load_config() -> Optional[dict]:
    """Load config from disk. Returns None if no config exists."""
    config_path = get_config_path()
    if not config_path.exists():
        return None
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_config(config: dict) -> None:
    """Save config to disk."""
    get_config_dir()  # Ensure dir exists
    config_path = get_config_path()
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def validate_and_show_config(config: dict) -> bool:
    """Validate config using provider and show connection status.

    Uses the provider's validate_config method for validation and testing.
    Returns True if config is valid and connection works.
    """
    import click

    # Import here to avoid circular imports
    from .providers import validate_provider_config

    provider = config.get("provider")
    if not provider:
        click.secho("Config validation failed: Missing 'provider' field", fg="red")
        return False

    click.echo(f"Provider: {provider}")

    # Use provider's validate_config
    success, message, stats = validate_provider_config(config)

    # Display stats
    for key, value in stats.items():
        click.echo(f"  {key}: {value}")

    # Show result
    if success:
        click.secho(f"\n  {message}", fg="green")
        return True
    else:
        click.secho(f"\n  {message}", fg="red")
        return False
