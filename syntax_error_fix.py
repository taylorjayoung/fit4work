#!/usr/bin/env python3
"""
Executable script that implements the fixed one-liner.

This script demonstrates the correct way to use the job scraper in a one-liner.
"""

def scrape_and_print():
    """Scrape job listings from Remote.co and print the results."""
    from job_scraper_app.scrapers.scraper_manager import ScraperManager
    import json
    with open('job_scraper_app/config.json', 'r') as f:
        config = json.load(f)
    scraper = ScraperManager(config, None)
    results = scraper.scrape_site('Remote.co')
    print(f'Scraped {len(results)} job listings')
    return results

if __name__ == "__main__":
    results = scrape_and_print()
    
    # Print details of the first 5 job listings
    for i, job in enumerate(results[:5]):
        print(f"\nJob {i+1}:")
        print(f"Title: {job.title}")
        print(f"Company: {job.company_name}")
        print(f"Location: {job.location}")
        print(f"Date Posted: {job.date_posted}")
        print(f"URL: {job.url}")
        print(f"Description: {job.description[:100]}...")
