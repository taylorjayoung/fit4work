#!/usr/bin/env python3
"""
Run script for the Job Scraper Application.

This script imports and runs the main function from the job_scraper_app package.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

# Import the main function from the job_scraper_app package
try:
    # Import the main function
    from job_scraper_app.main import main
    
    # Run the main function
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Error importing job_scraper_app: {e}")
    print("Please ensure the job_scraper_app package is installed correctly.")
    sys.exit(1)
