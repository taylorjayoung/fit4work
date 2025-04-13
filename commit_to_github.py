#!/usr/bin/env python3
"""
Script to commit changes to GitHub.

This script:
1. Adds all new files to git
2. Commits the changes with a descriptive message
3. Pushes the changes to GitHub
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and log the output."""
    logger.info(f"Running {description}...")
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        logger.info(f"{description} completed successfully.")
        logger.info(f"Output:\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"{description} failed with exit code {e.returncode}.")
        logger.error(f"Error output:\n{e.stderr}")
        return False

def main():
    """Commit changes to GitHub."""
    # Add all new files
    if not run_command(["git", "add", "."], "git add"):
        return 1
    
    # Commit the changes
    commit_message = "Fix syntax error in one-liner and add comprehensive testing"
    if not run_command(["git", "commit", "-m", commit_message], "git commit"):
        return 1
    
    # Push the changes to GitHub
    if not run_command(["git", "push"], "git push"):
        return 1
    
    logger.info("Changes successfully committed and pushed to GitHub!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
