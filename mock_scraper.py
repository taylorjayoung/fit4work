#!/usr/bin/env python3
"""
Mock Scraper for testing the Job Scraper Application.

This script creates a mock scraper that returns dummy data,
allowing testing of the ScraperManager without relying on external websites.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Import the necessary modules
from job_scraper_app.scrapers.base_scraper import BaseScraper
from job_scraper_app.scrapers.scraper_manager import ScraperManager

class MockScraper(BaseScraper):
    """
    Mock scraper that returns dummy job listings.
    
    This class extends BaseScraper and overrides the scrape method
    to return dummy data without actually scraping any website.
    """
    
    def scrape(self):
        """
        Return dummy job listings.
        
        Returns:
            List of dictionaries containing dummy job listing data
        """
        # Create dummy job listings
        job_listings = [
            {
                "title": "Remote Data Entry Specialist",
                "company_name": "DataCorp Inc.",
                "job_type": "Full-time",
                "location": "Remote",
                "description": "Looking for a detail-oriented data entry specialist to join our remote team.",
                "url": "https://example.com/jobs/1",
                "contact_info": "jobs@datacorp.example.com",
                "company_website": "https://datacorp.example.com",
                "salary_info": "$40,000 - $50,000",
                "posted_date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "Virtual Assistant",
                "company_name": "RemoteWorks LLC",
                "job_type": "Part-time",
                "location": "Remote",
                "description": "Seeking a virtual assistant to help with administrative tasks.",
                "url": "https://example.com/jobs/2",
                "contact_info": "careers@remoteworks.example.com",
                "company_website": "https://remoteworks.example.com",
                "salary_info": "$20 - $25 per hour",
                "posted_date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "title": "Remote Customer Support Representative",
                "company_name": "SupportHub",
                "job_type": "Full-time",
                "location": "Remote",
                "description": "Join our customer support team and help customers resolve issues.",
                "url": "https://example.com/jobs/3",
                "contact_info": "hr@supporthub.example.com",
                "company_website": "https://supporthub.example.com",
                "salary_info": "$45,000 - $55,000",
                "posted_date": datetime.now().strftime("%Y-%m-%d")
            }
        ]
        
        print(f"Mock scraper returning {len(job_listings)} dummy job listings")
        return job_listings

def main():
    """
    Main function to demonstrate using the ScraperManager with a mock scraper.
    """
    # Load the configuration
    config_path = project_dir / "job_scraper_app" / "config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Create a ScraperManager instance
    scraper_manager = ScraperManager(config, None)
    
    # Register our mock scraper for Remote.co
    scraper_manager.scrapers["Remote.co"] = MockScraper(
        config["job_sites"][0],  # Use Remote.co config
        config["scraping_settings"]
    )
    
    # Scrape using the mock scraper
    print("Scraping with mock scraper...")
    results = scraper_manager.scrape_site('Remote.co')
    
    # Print the results
    print(f"Scraped {len(results)} job listings")
    
    # Print the job listings
    for i, job in enumerate(results):
        print(f"\nJob {i+1}:")
        print(f"Title: {job.get('title')}")
        print(f"Company: {job.get('company_name')}")
        print(f"Type: {job.get('job_type')}")
        print(f"Location: {job.get('location')}")
        print(f"URL: {job.get('url')}")
        print(f"Salary: {job.get('salary_info')}")

if __name__ == "__main__":
    main()
