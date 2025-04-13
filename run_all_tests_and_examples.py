#!/usr/bin/env python3
"""
Script to run all tests and examples in the project.

This script runs:
1. All unit tests
2. The one-liner example
3. The fixed syntax error example
4. The resume processor example
5. The test scripts for the fixed one-liner and resume processor
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
    """Run all tests and examples."""
    # Keep track of failures
    failures = []
    
    # Run all unit tests
    if not run_command(["python", "run_tests.py"], "unit tests"):
        failures.append("Unit tests")
    
    # Run the one-liner example
    if not run_command(["python", "one_liner_example.py"], "one-liner example"):
        failures.append("One-liner example")
    
    # Run the fixed syntax error example
    if not run_command(["python", "syntax_error_fix.py"], "fixed syntax error example"):
        failures.append("Fixed syntax error example")
    
    # Run the test script for the fixed one-liner
    if not run_command(["python", "test_fixed_one_liner.py"], "test script for the fixed one-liner"):
        failures.append("Test script for the fixed one-liner")
    
    # Run the resume processor example
    if not run_command(["python", "resume_processor_example.py"], "resume processor example"):
        failures.append("Resume processor example")
    
    # Run the test script for the resume processor
    if not run_command(["python", "test_resume_processor.py"], "test script for the resume processor"):
        failures.append("Test script for the resume processor")
    
    # Print summary
    if failures:
        logger.error("The following tests/examples failed:")
        for failure in failures:
            logger.error(f"- {failure}")
        return 1
    else:
        logger.info("All tests and examples completed successfully!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
