#!/usr/bin/env python3
"""
Script to run all tests in the project.

This script discovers and runs all tests in the project.
"""

import unittest
import sys
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_tests():
    """Run all tests in the project."""
    # Add the project directory to the Python path
    project_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_dir))
    
    # Discover and run all tests
    logger.info("Discovering and running all tests...")
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests')
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return the number of failures and errors
    return len(result.failures) + len(result.errors)

def run_specific_tests(test_path):
    """Run specific tests."""
    # Add the project directory to the Python path
    project_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_dir))
    
    # Run the specified tests
    logger.info(f"Running tests in {test_path}...")
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(test_path)
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return the number of failures and errors
    return len(result.failures) + len(result.errors)

if __name__ == "__main__":
    # Check if a specific test path was provided
    if len(sys.argv) > 1:
        test_path = sys.argv[1]
        exit_code = run_specific_tests(test_path)
    else:
        exit_code = run_tests()
    
    # Exit with the number of failures and errors
    sys.exit(exit_code)
