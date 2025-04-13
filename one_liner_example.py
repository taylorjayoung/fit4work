#!/usr/bin/env python3
"""
Example script demonstrating how to use the job scraper in a one-liner.

This script shows how to:
1. Import the ScraperManager
2. Create a ScraperManager instance
3. Scrape job listings from a specific site
4. Print the results
"""

import json
from job_scraper_app.scrapers.scraper_manager import ScraperManager

def main():
    """Run the one-liner example."""
    # Load configuration
    with open('job_scraper_app/config.json', 'r') as f:
        config = json.load(f)
    
    # Create a ScraperManager instance
    scraper = ScraperManager(config, None)
    
    # Scrape job listings from Remote.co
    results = scraper.scrape_site('Remote.co')
    
    # Print the results
    print(f'Scraped {len(results)} job listings')
    
    # Print details of the first 5 job listings
    for i, job in enumerate(results[:5]):
        print(f"\nJob {i+1}:")
        print(f"Title: {job.title}")
        print(f"Company: {job.company_name}")
        print(f"Location: {job.location}")
        print(f"Date Posted: {job.date_posted}")
        print(f"URL: {job.url}")
        print(f"Description: {job.description[:100]}...")

if __name__ == "__main__":
    main()
