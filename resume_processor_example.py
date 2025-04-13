#!/usr/bin/env python3
"""
Example script demonstrating how to use the resume processor functionality.

This script shows how to:
1. Upload and parse a resume
2. Generate a tailored resume for a job listing
3. Get tailored resumes for a specific resume or job listing
"""

import os
import json
import logging
from pathlib import Path
from sqlalchemy import create_engine

from job_scraper_app.resume_processor.resume_manager import ResumeManager
from job_scraper_app.scrapers.scraper_manager import ScraperManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run the resume processor example."""
    # Load configuration
    with open('job_scraper_app/config.json', 'r') as f:
        config = json.load(f)
    
    # Create database engine
    db_url = config.get('database_url', 'sqlite:///job_listings.db')
    engine = create_engine(db_url)
    
    # Create resume manager
    resume_manager = ResumeManager(config, engine)
    
    # Create scraper manager
    scraper_manager = ScraperManager(config, engine)
    
    # Example 1: Upload and parse a resume
    print("\n=== Example 1: Upload and parse a resume ===")
    
    # Check if the resume directory exists, create it if it doesn't
    resume_dir = Path(config["resume_settings"]["storage_path"])
    os.makedirs(resume_dir, exist_ok=True)
    
    # Create a sample resume file path
    sample_resume_path = resume_dir / "sample_resume.docx"
    
    # Check if the sample resume exists
    if not sample_resume_path.exists():
        print(f"Sample resume not found at {sample_resume_path}")
        print("Please create a sample resume file in DOCX or PDF format")
        print("You can use Microsoft Word or Google Docs to create a resume")
        print("Then save it as 'sample_resume.docx' in the resume directory")
        return
    
    # Upload the resume
    resume_id = resume_manager.upload_resume(sample_resume_path, "Sample Resume", True)
    
    if resume_id:
        print(f"Successfully uploaded resume with ID: {resume_id}")
    else:
        print("Failed to upload resume")
        return
    
    # Example 2: Scrape job listings
    print("\n=== Example 2: Scrape job listings ===")
    
    # Scrape job listings from Remote.co
    job_listings = scraper_manager.scrape_site('Remote.co')
    
    if job_listings:
        print(f"Scraped {len(job_listings)} job listings from Remote.co")
        
        # Get the first job listing
        job_listing = job_listings[0]
        print(f"First job listing: {job_listing.title} at {job_listing.company_name}")
    else:
        print("Failed to scrape job listings")
        # Create a sample job listing for demonstration
        job_listing_id = 1
        print("Using a sample job listing for demonstration")
    
    # Example 3: Generate a tailored resume
    print("\n=== Example 3: Generate a tailored resume ===")
    
    # Generate a tailored resume for the job listing
    tailored_resume_id = resume_manager.generate_tailored_resume(resume_id, job_listing.id)
    
    if tailored_resume_id:
        print(f"Successfully generated tailored resume with ID: {tailored_resume_id}")
    else:
        print("Failed to generate tailored resume")
    
    # Example 4: Get tailored resumes
    print("\n=== Example 4: Get tailored resumes ===")
    
    # Get all tailored resumes for the resume
    tailored_resumes = resume_manager.get_tailored_resumes(resume_id=resume_id)
    
    if tailored_resumes:
        print(f"Found {len(tailored_resumes)} tailored resumes for resume ID {resume_id}")
        for tr in tailored_resumes:
            print(f"- {tr.name} (ID: {tr.id})")
    else:
        print(f"No tailored resumes found for resume ID {resume_id}")
    
    print("\nResume processor example completed successfully!")

if __name__ == "__main__":
    main()
