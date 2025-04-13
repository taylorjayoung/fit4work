#!/usr/bin/env python3
"""
Test script for the config_loader module.

This script verifies that the configuration loading system works correctly,
including environment variable overrides and local config file support.

Usage:
    python test_config_loader.py
"""

import os
import json
import sys
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Import the config_loader module
from config_loader import load_config, get_anthropic_api_key

def print_separator(title):
    """Print a separator with a title."""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50, "="))
    print("=" * 50 + "\n")

def test_config_loading():
    """Test the configuration loading system."""
    print_separator("Testing Configuration Loading")
    
    # Load the configuration
    config = load_config()
    
    # Print the loaded configuration (excluding sensitive information)
    safe_config = config.copy()
    if 'ai_services' in safe_config and 'anthropic' in safe_config['ai_services']:
        api_key = safe_config['ai_services']['anthropic'].get('api_key', '')
        if api_key and api_key != 'YOUR_ANTHROPIC_API_KEY':
            # Mask the API key if it's set
            safe_config['ai_services']['anthropic']['api_key'] = '********' + api_key[-4:]
    
    print("Loaded configuration:")
    print(json.dumps(safe_config, indent=2))
    
    # Check if the Anthropic API key is set
    api_key = get_anthropic_api_key()
    if api_key and api_key != 'YOUR_ANTHROPIC_API_KEY':
        print("\nAnthropic API key is configured correctly! ✅")
        print(f"API key ending with: ...{api_key[-4:]}")
    else:
        print("\nAnthropic API key is not set or is using the placeholder value. ❌")
        print("Please set your API key using one of the methods described in API_KEY_SETUP.md")

def test_environment_variable_override():
    """Test the environment variable override functionality."""
    print_separator("Testing Environment Variable Override")
    
    # Check if the environment variable is set
    env_var_name = 'FIT4WORK_ANTHROPIC_API_KEY'
    env_var_value = os.environ.get(env_var_name)
    
    if env_var_value:
        print(f"Environment variable {env_var_name} is set! ✅")
        print(f"Value ending with: ...{env_var_value[-4:]}")
    else:
        print(f"Environment variable {env_var_name} is not set. ℹ️")
        print(f"You can set it with: export {env_var_name}=your-api-key")

def test_local_config_file():
    """Test the local config file functionality."""
    print_separator("Testing Local Config File")
    
    # Check if the local config file exists
    local_config_path = project_dir / "config.local.json"
    
    if local_config_path.exists():
        print(f"Local config file exists at {local_config_path}! ✅")
        try:
            with open(local_config_path, 'r') as f:
                local_config = json.load(f)
            
            # Check if the Anthropic API key is set in the local config
            api_key = local_config.get('ai_services', {}).get('anthropic', {}).get('api_key')
            if api_key and api_key != 'YOUR_ACTUAL_ANTHROPIC_API_KEY':
                print("Anthropic API key is set in the local config! ✅")
                print(f"API key ending with: ...{api_key[-4:]}")
            else:
                print("Anthropic API key is not properly set in the local config. ❌")
        except json.JSONDecodeError:
            print("Local config file exists but contains invalid JSON. ❌")
    else:
        print(f"Local config file does not exist at {local_config_path}. ℹ️")
        print("You can create it by copying config.local.json.template")

def main():
    """Main entry point for the test script."""
    print("Config Loader Test Script")
    print("========================\n")
    print("This script tests the configuration loading system, including environment")
    print("variable overrides and local config file support.\n")
    
    # Run the tests
    test_config_loading()
    test_environment_variable_override()
    test_local_config_file()
    
    print_separator("Summary")
    print("If you see any ❌ errors above, please check API_KEY_SETUP.md for instructions")
    print("on how to properly configure your API keys.\n")
    print("Remember: Never commit your actual API keys to GitHub!")

if __name__ == "__main__":
    main()
