#!/usr/bin/env python3
"""
Run script for the Job Scraper Application.

This script changes to the job_scraper_app directory and runs the main.py script.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the path to the job_scraper_app directory
    app_dir = Path(__file__).resolve().parent / "job_scraper_app"
    
    # Check if the directory exists
    if not app_dir.exists() or not app_dir.is_dir():
        print(f"Error: {app_dir} does not exist or is not a directory")
        sys.exit(1)
    
    # Get the path to the main.py script
    main_script = app_dir / "main.py"
    
    # Check if the script exists
    if not main_script.exists() or not main_script.is_file():
        print(f"Error: {main_script} does not exist or is not a file")
        sys.exit(1)
    
    # Change to the job_scraper_app directory
    os.chdir(app_dir)
    
    # Run the main.py script
    try:
        print(f"Running {main_script} from {os.getcwd()}")
        result = subprocess.run([sys.executable, "main.py"], check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"Error running {main_script}: {e}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
