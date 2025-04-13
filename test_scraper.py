#!/usr/bin/env python3
"""
Test script for the Job Scraper Application.

This script tests the ScraperManager by scraping job listings from Remote.co.
"""

import json
import sys
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Import the ScraperManager
from job_scraper_app.scrapers.scraper_manager import ScraperManager

def main():
    # Load the configuration
    config_path = project_dir / "job_scraper_app" / "config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Disable Selenium for testing purposes
    config["scraping_settings"]["use_selenium_for_dynamic_sites"] = False
    
    # Initialize the ScraperManager with None as the database engine (for testing)
    scraper = ScraperManager(config, None)
    
    # Scrape Remote.co job listings
    print("Scraping Remote.co job listings...")
    results = scraper.scrape_site('Remote.co')
    
    # Print the results
    print(f"Scraped {len(results)} job listings from Remote.co")
    
    # Print the first 3 job listings (if available)
    for i, job in enumerate(results[:3]):
        print(f"\nJob {i+1}:")
        print(f"Title: {job.get('title')}")
        print(f"Company: {job.get('company_name')}")
        print(f"URL: {job.get('url')}")

if __name__ == "__main__":
    main()
