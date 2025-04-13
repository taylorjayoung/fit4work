import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Try to import dotenv, install if not available
try:
    from dotenv import load_dotenv
except ImportError:
    import subprocess
    import sys
    print("python-dotenv not found, installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path(os.path.dirname(__file__)) / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded environment variables from {env_path}")

logger = logging.getLogger(__name__)

def load_config() -> Dict[str, Any]:
    """
    Load configuration from config files and environment variables.
    
    Priority order:
    1. Environment variables (highest priority)
    2. config.local.json (if exists)
    3. config.json (lowest priority)
    
    Returns:
        Dict[str, Any]: The merged configuration
    """
    # Base configuration from example/default
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    local_config_path = os.path.join(os.path.dirname(__file__), "config.local.json")
    
    # Load the main config
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file not found at {config_path}. Using empty config.")
        config = {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in config file at {config_path}. Using empty config.")
        config = {}
    
    # Override with local config if it exists
    try:
        if os.path.exists(local_config_path):
            with open(local_config_path, 'r') as f:
                local_config = json.load(f)
                deep_merge(config, local_config)
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in local config file at {local_config_path}. Skipping.")
    
    # Override with environment variables
    apply_env_overrides(config)
    
    return config

def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> None:
    """
    Deep merge override dict into base dict.
    
    Args:
        base: Base dictionary to merge into
        override: Dictionary with values to override
    """
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value

def apply_env_overrides(config: Dict[str, Any]) -> None:
    """
    Apply environment variable overrides to the config.
    
    Environment variables take precedence over config file values.
    
    Format for environment variables:
    - FIT4WORK_ANTHROPIC_API_KEY: For Anthropic API key
    
    Args:
        config: Configuration dictionary to update
    """
    # Handle Anthropic API key
    anthropic_api_key = os.environ.get('FIT4WORK_ANTHROPIC_API_KEY')
    if anthropic_api_key:
        if 'ai_services' not in config:
            config['ai_services'] = {}
        if 'anthropic' not in config['ai_services']:
            config['ai_services']['anthropic'] = {}
        config['ai_services']['anthropic']['api_key'] = anthropic_api_key

def get_anthropic_api_key() -> Optional[str]:
    """
    Get the Anthropic API key from the configuration.
    
    Returns:
        Optional[str]: The API key or None if not configured
    """
    config = load_config()
    try:
        return config['ai_services']['anthropic']['api_key']
    except KeyError:
        return None
