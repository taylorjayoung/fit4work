#!/usr/bin/env python3
"""
Proper script for testing the Job Scraper Application.

This script demonstrates the correct way to use the ScraperManager.
"""

import sys
import json
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

def main():
    """Main function to demonstrate using the ScraperManager."""
    try:
        # Import the ScraperManager
        from job_scraper_app.scrapers.scraper_manager import ScraperManager
        
        # Print a message to show the import worked
        print("Successfully imported ScraperManager")
        
        # Load the configuration
        config_path = project_dir / "job_scraper_app" / "config.json"
        print(f"Loading configuration from {config_path}")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("Successfully loaded configuration")
        
        # Disable Selenium for testing purposes
        config["scraping_settings"]["use_selenium_for_dynamic_sites"] = False
        print("Disabled Selenium for testing purposes")
        
        # Initialize the ScraperManager
        print("Initializing ScraperManager")
        scraper = ScraperManager(config, None)  # None for the database engine (testing only)
        
        print("Successfully initialized ScraperManager")
        
        # Instead of actually scraping, let's just print a message
        print("\nNOTE: This script doesn't actually perform scraping to avoid network issues.")
        print("To perform actual scraping, use one of the following approaches:")
        print("1. Use the mock_scraper.py script for testing with dummy data:")
        print("   python mock_scraper.py")
        print("2. Use the main application for actual scraping:")
        print("   python run.py --scrape-only")
        
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Make sure you're running this script from the project root directory.")
    except FileNotFoundError as e:
        print(f"Error loading configuration: {e}")
        print("Make sure the config.json file exists in the job_scraper_app directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
