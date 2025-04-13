#!/usr/bin/env python3
"""
Examples for using the Job Scraper Application.

This script demonstrates different ways to use the ScraperManager.
"""

import sys
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

def print_section(title):
    """Print a section title with separators."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def example_one_liner():
    """Example of how to correctly format a one-liner for the Python interpreter."""
    print_section("ONE-LINER EXAMPLE")
    print("The original one-liner had a syntax error:")
    print("from scrapers.scraper_manager import ScraperManager; import json; with open('config.json', 'r') as f: config = json.load(f); scraper = ScraperManager(config, None); results = scraper.scrape_site('Remote.co'); print(f'Scraped {len(results)} job listings')")
    print("\nThe issue is with the 'with' statement in a one-liner. Here's the correct way:")
    print("from job_scraper_app.scrapers.scraper_manager import ScraperManager; import json; f = open('job_scraper_app/config.json', 'r'); config = json.load(f); f.close(); scraper = ScraperManager(config, None); results = scraper.scrape_site('Remote.co'); print(f'Scraped {len(results)} job listings')")
    print("\nNote: We replaced the 'with' statement with explicit open/close calls.")

def example_proper_script():
    """Example of how to properly write a script to use the ScraperManager."""
    print_section("PROPER SCRIPT EXAMPLE")
    print("Here's how to properly write a script to use the ScraperManager:")
    print("""
# Import necessary modules
from job_scraper_app.scrapers.scraper_manager import ScraperManager
import json

# Load the configuration
with open('job_scraper_app/config.json', 'r') as f:
    config = json.load(f)

# Initialize the ScraperManager
scraper = ScraperManager(config, None)  # None for the database engine (testing only)

# Scrape job listings
results = scraper.scrape_site('Remote.co')

# Print the results
print(f'Scraped {len(results)} job listings')
for job in results[:3]:  # Print first 3 jobs
    print(f"Title: {job.get('title')}")
    print(f"Company: {job.get('company_name')}")
    print(f"URL: {job.get('url')}")
    print()
""")

def example_mock_scraper():
    """Example of how to use the mock scraper for testing."""
    print_section("MOCK SCRAPER EXAMPLE")
    print("For testing without relying on external websites, use the mock_scraper.py script:")
    print("python mock_scraper.py")
    print("\nThe mock_scraper.py script:")
    print("1. Creates a mock scraper that returns dummy job listings")
    print("2. Registers the mock scraper with the ScraperManager")
    print("3. Uses the ScraperManager to 'scrape' job listings")
    print("4. Prints the results")
    print("\nThis is useful for testing the ScraperManager without network issues.")

def example_main_application():
    """Example of how to use the main application."""
    print_section("MAIN APPLICATION EXAMPLE")
    print("For actual usage, it's recommended to use the main application:")
    print("python run.py")
    print("or")
    print("python run_app.py")
    print("\nThese scripts:")
    print("1. Load the configuration")
    print("2. Set up the database")
    print("3. Initialize the ScraperManager with the config and database engine")
    print("4. Either run the scraper only or start the Flask web application")
    print("\nFor scrape-only mode:")
    print("python run.py --scrape-only")

def main():
    """Main function to run all examples."""
    print_section("JOB SCRAPER APPLICATION EXAMPLES")
    print("This script demonstrates different ways to use the ScraperManager.")
    
    example_one_liner()
    example_proper_script()
    example_mock_scraper()
    example_main_application()
    
    print("\n" + "=" * 60)
    print("RECOMMENDATION")
    print("=" * 60)
    print("For testing and development, use the mock_scraper.py script.")
    print("For actual usage, use the main application (run.py or run_app.py).")
    print("Avoid one-liners for complex operations like web scraping.")

if __name__ == "__main__":
    main()
