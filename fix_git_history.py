#!/usr/bin/env python3
"""
Script to rewrite Git history to remove sensitive information.
"""

import os
import subprocess
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command):
    """Run a shell command and return the output."""
    logger.info(f"Running command: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        logger.error(f"Command failed with exit code {process.returncode}")
        logger.error(f"Error output: {stderr.decode('utf-8')}")
        return False, stderr.decode('utf-8')
    
    return True, stdout.decode('utf-8')

def main():
    """Main function to rewrite Git history."""
    # Create a filter script to replace the API key
    filter_script = """
    #!/bin/sh
    sed -i 's/sk-ant-api03-[A-Za-z0-9_-]\\{40,\\}/YOUR_ANTHROPIC_API_KEY/g' "$@"
    """
    
    with open('filter.sh', 'w') as f:
        f.write(filter_script)
    
    # Make the script executable
    os.chmod('filter.sh', 0o755)
    
    # Use git filter-branch to rewrite history
    command = """
    git filter-branch --force --tree-filter './filter.sh job_scraper_app/config.json' HEAD
    """
    
    success, output = run_command(command)
    if not success:
        logger.error("Failed to rewrite Git history")
        return
    
    logger.info("Git history rewritten successfully")
    
    # Force push the changes
    success, output = run_command("git push --force")
    if not success:
        logger.error("Failed to force push changes")
        return
    
    logger.info("Changes force pushed successfully")
    
    # Clean up
    os.remove('filter.sh')
    logger.info("Cleanup completed")

if __name__ == "__main__":
    main()
