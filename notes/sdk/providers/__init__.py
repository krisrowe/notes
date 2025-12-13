"""Provider factory and interfaces."""

import importlib
import os
from typing import Optional, Type, Union

from ..config import load_config

__all__ = [
    "get_provider",
    "get_provider_class",
    "validate_provider_config",
]

# Environment variable to switch providers
PROVIDER_ENV_VAR = "NOTES_PROVIDER"

# Known provider mappings (provider name -> module.ClassName)
PROVIDER_REGISTRY = {
    "appsheet": ("notes.sdk.providers.appsheet", "AppSheetProvider"),
    # "json": ("notes.sdk.providers.json", "JSONProvider"),  # Future
    # "sheets": ("notes.sdk.providers.sheets", "SheetsProvider"),  # Future
}


def get_provider_class(provider_name: str) -> Type:
    """Get a provider class by name.

    Args:
        provider_name: Name of the provider (e.g., 'appsheet')

    Returns:
        The provider class

    Raises:
        ValueError: If provider not found
    """
    provider_name = provider_name.lower()

    if provider_name not in PROVIDER_REGISTRY:
        available = ", ".join(PROVIDER_REGISTRY.keys())
        raise ValueError(f"Unknown provider: {provider_name}. Available: {available}")

    module_path, class_name = PROVIDER_REGISTRY[provider_name]

    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Failed to load provider '{provider_name}': {e}")


def validate_provider_config(config: dict) -> tuple[bool, str, dict]:
    """Validate config using the appropriate provider's validate_config method.

    Args:
        config: Config dict with 'provider' key

    Returns:
        (success, message, stats) from the provider's validate_config
    """
    provider_name = config.get("provider")
    if not provider_name:
        return False, "Missing 'provider' field in config", {}

    try:
        provider_class = get_provider_class(provider_name)
    except ValueError as e:
        return False, str(e), {}

    if not hasattr(provider_class, "validate_config"):
        return False, f"Provider '{provider_name}' does not implement validate_config", {}

    return provider_class.validate_config(config)


def get_provider(provider_type: Optional[str] = None):
    """Get a provider instance based on configuration.

    Provider selection priority:
    1. Explicit provider_type argument
    2. NOTES_PROVIDER environment variable
    3. Config file setting
    4. Default to 'appsheet'
    """
    # Load config from file
    config = load_config() or {}

    if provider_type is None:
        provider_type = os.environ.get(PROVIDER_ENV_VAR)
    if provider_type is None:
        provider_type = config.get("provider", "appsheet")

    provider_type = provider_type.lower()

    # Get provider class
    provider_class = get_provider_class(provider_type)

    # Build provider with config + env var fallback
    if provider_type == "appsheet":
        appsheet_config = config.get("appsheet", {})
        return provider_class(
            app_id=appsheet_config.get("app_id") or os.environ.get("APPSHEET_APP_ID"),
            api_key=appsheet_config.get("api_key") or os.environ.get("APPSHEET_API_KEY"),
            table_name=appsheet_config.get("note_table") or os.environ.get("APPSHEET_TABLE_NAME", "Note"),
        )
    else:
        # For other providers, pass config directly (to be implemented)
        raise ValueError(f"Provider '{provider_type}' instantiation not yet implemented")
