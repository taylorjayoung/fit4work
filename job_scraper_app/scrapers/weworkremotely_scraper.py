"""
We Work Remotely Scraper for the Job Scraper Application.

This module implements a scraper for the We Work Remotely job site.
"""

import logging
import re
from urllib.parse import urljoin
from datetime import datetime

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class WeWorkRemotelyScraper(BaseScraper):
    """
    Scraper for We Work Remotely job listings.
    
    This class implements the scrape method to extract job listings
    from the We Work Remotely job site.
    """
    
    def scrape(self):
        """
        Scrape job listings from We Work Remotely.
        
        Returns:
            List of dictionaries containing job listing data
        """
        job_listings = []
        
        try:
            # Get the initial page
            url = self.site_config["job_listings_url"]
            logger.info(f"Scraping job listings from {url}")
            
            # Get the page content
            soup = self._get_page_content(url)
            
            # Extract job listings from the page
            job_containers = soup.select(self.site_config["selectors"]["job_container"])
            
            if not job_containers:
                logger.warning("No job listings found")
                return job_listings
            
            logger.info(f"Found {len(job_containers)} job listings")
            
            # Process each job listing
            for container in job_containers:
                try:
                    # Extract basic job information
                    job_title_elem = container.select_one(self.site_config["selectors"]["job_title"])
                    company_name_elem = container.select_one(self.site_config["selectors"]["company_name"])
                    job_type_elem = container.select_one(self.site_config["selectors"]["job_type"])
                    location_elem = container.select_one(self.site_config["selectors"]["location"])
                    posted_date_elem = container.select_one(self.site_config["selectors"]["posted_date"])
                    
                    # Get the job description URL
                    description_link_elem = container.select_one(self.site_config["selectors"]["description_link"])
                    description_url = urljoin(self.site_config["base_url"], self._extract_attribute(description_link_elem, "href"))
                    
                    # Skip if we can't get the essential information
                    if not job_title_elem or not description_url:
                        logger.warning("Skipping job listing: missing essential information")
                        continue
                    
                    # Create a job listing dictionary with the basic information
                    job_listing = {
                        "title": self._extract_text(job_title_elem),
                        "company_name": self._extract_text(company_name_elem) or "Unknown Company",
                        "job_type": self._extract_text(job_type_elem),
                        "location": self._extract_text(location_elem),
                        "url": description_url,
                        "posted_date": self._parse_date(self._extract_text(posted_date_elem))
                    }
                    
                    # Get the detailed job description
                    try:
                        description_soup = self._get_page_content(description_url)
                        description_elem = description_soup.select_one(self.site_config["selectors"]["description_selector"])
                        
                        if description_elem:
                            job_listing["description"] = description_elem.get_text(strip=True)
                            
                            # Extract contact information from the description
                            contact_info = self._extract_contact_info(description_elem.get_text())
                            if contact_info:
                                job_listing["contact_info"] = contact_info
                            
                            # Extract company website from the description
                            company_website = self._extract_company_website(description_elem.get_text())
                            if company_website:
                                job_listing["company_website"] = company_website
                            
                            # Extract salary information from the description
                            salary_info = self._extract_salary_info(description_elem.get_text())
                            if salary_info:
                                job_listing["salary_info"] = salary_info
                    except Exception as e:
                        logger.error(f"Error fetching job description from {description_url}: {e}")
                    
                    # Add the job listing to the list
                    job_listings.append(job_listing)
                    logger.debug(f"Added job listing: {job_listing['title']} at {job_listing['company_name']}")
                    
                except Exception as e:
                    logger.error(f"Error processing job listing: {e}", exc_info=True)
            
            logger.info(f"Scraped a total of {len(job_listings)} job listings from We Work Remotely")
            
        except Exception as e:
            logger.error(f"Error scraping We Work Remotely: {e}", exc_info=True)
        
        return job_listings
    
    def _extract_contact_info(self, text):
        """
        Extract contact information from text.
        
        Args:
            text: Text to extract contact information from
            
        Returns:
            Extracted contact information or None if not found
        """
        contact_info = []
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info.extend(emails)
        
        # Extract phone numbers
        phone_pattern = r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info.extend(phones)
        
        # Extract LinkedIn profiles
        linkedin_pattern = r'linkedin\.com/(?:in|company)/[A-Za-z0-9_-]+'
        linkedin = re.findall(linkedin_pattern, text)
        if linkedin:
            contact_info.extend(linkedin)
        
        if contact_info:
            return ", ".join(contact_info)
        return None
    
    def _extract_company_website(self, text):
        """
        Extract company website from text.
        
        Args:
            text: Text to extract company website from
            
        Returns:
            Extracted company website or None if not found
        """
        # Extract URLs
        url_pattern = r'https?://(?:www\.)?([A-Za-z0-9][-A-Za-z0-9]*\.)+[A-Za-z]{2,}(?:/[^\\s]*)?'
        urls = re.findall(url_pattern, text)
        
        if urls:
            # Filter out job board URLs, social media, etc.
            excluded_domains = ['weworkremotely.com', 'linkedin.com', 'twitter.com', 'facebook.com', 'instagram.com']
            for url in urls:
                if not any(excluded in url.lower() for excluded in excluded_domains):
                    return url
        
        return None
    
    def _extract_salary_info(self, text):
        """
        Extract salary information from text.
        
        Args:
            text: Text to extract salary information from
            
        Returns:
            Extracted salary information or None if not found
        """
        # Extract salary ranges like $50,000 - $70,000, $50k - $70k, etc.
        salary_pattern = r'\$\s*\d{1,3}(?:,\d{3})*(?:\s*-\s*\$\s*\d{1,3}(?:,\d{3})*)?(?:\s*(?:per|a|\/)\s*(?:year|yr|month|mo|hour|hr|annum))?'
        salary_pattern_alt = r'\$\d{1,3}[k](?:\s*-\s*\$\d{1,3}[k])?(?:\s*(?:per|a|\/)\s*(?:year|yr|month|mo|hour|hr|annum))?'
        
        salaries = re.findall(salary_pattern, text, re.IGNORECASE)
        if not salaries:
            salaries = re.findall(salary_pattern_alt, text, re.IGNORECASE)
        
        if salaries:
            return salaries[0].strip()
        
        return None
