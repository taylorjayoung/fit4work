"""
Scraper Manager for the Job Scraper Application.

This module manages the scraping process for all configured job sites.
It handles the creation and execution of site-specific scrapers and
stores the scraped job listings in the database.
"""

import logging
import importlib
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from ..database import JobListing
from .base_scraper import BaseScraper
from .remote_co_scraper import RemoteCoScraper
from .weworkremotely_scraper import WeWorkRemotelyScraper
from .remoteok_scraper import RemoteOkScraper
from .flexjobs_scraper import FlexJobsScraper

logger = logging.getLogger(__name__)

class ScraperManager:
    """
    Manager for job site scrapers.
    
    This class is responsible for:
    1. Creating and managing scrapers for different job sites
    2. Executing the scraping process
    3. Storing scraped job listings in the database
    """
    
    def __init__(self, config, db_engine):
        """
        Initialize the scraper manager.
        
        Args:
            config: Application configuration dictionary
            db_engine: SQLAlchemy database engine
        """
        self.config = config
        self.db_engine = db_engine
        self.Session = sessionmaker(bind=db_engine)
        self.scrapers = {}
        self._initialize_scrapers()
        
    def _initialize_scrapers(self):
        """Initialize scrapers for all enabled job sites in the configuration."""
        scraper_map = {
            "Remote.co": RemoteCoScraper,
            "We Work Remotely": WeWorkRemotelyScraper,
            "RemoteOK": RemoteOkScraper,
            "FlexJobs": FlexJobsScraper
        }
        
        for site_config in self.config["job_sites"]:
            site_name = site_config["name"]
            if site_config["enabled"]:
                if site_name in scraper_map:
                    try:
                        self.scrapers[site_name] = scraper_map[site_name](site_config, self.config["scraping_settings"])
                        logger.info(f"Initialized scraper for {site_name}")
                    except Exception as e:
                        logger.error(f"Failed to initialize scraper for {site_name}: {e}")
                else:
                    logger.warning(f"No scraper implementation found for {site_name}")
        
        logger.info(f"Initialized {len(self.scrapers)} scrapers")
    
    def scrape_site(self, site_name):
        """
        Scrape job listings from a specific site.
        
        Args:
            site_name: Name of the job site to scrape
            
        Returns:
            List of scraped job listings
        """
        if site_name not in self.scrapers:
            logger.error(f"No scraper found for {site_name}")
            return []
        
        try:
            logger.info(f"Starting scraping process for {site_name}")
            scraper = self.scrapers[site_name]
            job_listings = scraper.scrape()
            logger.info(f"Scraped {len(job_listings)} job listings from {site_name}")
            
            # Store job listings in the database
            self._store_job_listings(job_listings, site_name)
            
            return job_listings
        except Exception as e:
            logger.error(f"Error scraping {site_name}: {e}", exc_info=True)
            return []
    
    def scrape_all_sites(self):
        """
        Scrape job listings from all enabled job sites.
        
        Returns:
            Dictionary mapping site names to lists of scraped job listings
        """
        results = {}
        
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_site = {executor.submit(self.scrape_site, site_name): site_name 
                             for site_name in self.scrapers.keys()}
            
            for future in as_completed(future_to_site):
                site_name = future_to_site[future]
                try:
                    job_listings = future.result()
                    results[site_name] = job_listings
                except Exception as e:
                    logger.error(f"Error processing results from {site_name}: {e}", exc_info=True)
                    results[site_name] = []
        
        total_jobs = sum(len(listings) for listings in results.values())
        logger.info(f"Completed scraping all sites. Total job listings: {total_jobs}")
        
        return results
    
    def _store_job_listings(self, job_listings, site_name):
        """
        Store job listings in the database.
        
        Args:
            job_listings: List of job listings to store
            site_name: Name of the job site the listings were scraped from
        """
        session = self.Session()
        try:
            for job_data in job_listings:
                # Check if the job listing already exists
                existing_job = session.query(JobListing).filter_by(url=job_data["url"]).first()
                
                if existing_job:
                    # Update existing job listing
                    for key, value in job_data.items():
                        if key != "url":  # Don't update the URL (primary identifier)
                            setattr(existing_job, key, value)
                    logger.debug(f"Updated existing job listing: {job_data['title']} at {job_data['company_name']}")
                else:
                    # Create new job listing
                    job_listing = JobListing(
                        title=job_data["title"],
                        company_name=job_data["company_name"],
                        job_type=job_data.get("job_type"),
                        location=job_data.get("location"),
                        description=job_data.get("description"),
                        url=job_data["url"],
                        contact_info=job_data.get("contact_info"),
                        company_website=job_data.get("company_website"),
                        salary_info=job_data.get("salary_info"),
                        posted_date=job_data.get("posted_date"),
                        scraped_date=datetime.utcnow(),
                        source_site=site_name,
                        is_active=True
                    )
                    session.add(job_listing)
                    logger.debug(f"Added new job listing: {job_data['title']} at {job_data['company_name']}")
            
            session.commit()
            logger.info(f"Successfully stored {len(job_listings)} job listings from {site_name}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing job listings from {site_name}: {e}", exc_info=True)
        finally:
            session.close()
    
    def get_job_listings(self, filters=None, limit=100, offset=0):
        """
        Retrieve job listings from the database.
        
        Args:
            filters: Dictionary of filters to apply
            limit: Maximum number of job listings to retrieve
            offset: Offset for pagination
            
        Returns:
            List of job listings
        """
        session = self.Session()
        try:
            query = session.query(JobListing)
            
            # Apply filters if provided
            if filters:
                if "title" in filters and filters["title"]:
                    query = query.filter(JobListing.title.ilike(f"%{filters['title']}%"))
                if "company" in filters and filters["company"]:
                    query = query.filter(JobListing.company_name.ilike(f"%{filters['company']}%"))
                if "job_type" in filters and filters["job_type"]:
                    query = query.filter(JobListing.job_type.ilike(f"%{filters['job_type']}%"))
                if "location" in filters and filters["location"]:
                    query = query.filter(JobListing.location.ilike(f"%{filters['location']}%"))
                if "source_site" in filters and filters["source_site"]:
                    query = query.filter(JobListing.source_site == filters["source_site"])
                if "is_active" in filters:
                    query = query.filter(JobListing.is_active == filters["is_active"])
            
            # Order by most recently scraped
            query = query.order_by(JobListing.scraped_date.desc())
            
            # Apply pagination
            query = query.limit(limit).offset(offset)
            
            # Execute query and return results
            return query.all()
        except Exception as e:
            logger.error(f"Error retrieving job listings: {e}", exc_info=True)
            return []
        finally:
            session.close()
