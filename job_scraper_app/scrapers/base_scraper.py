"""
Base Scraper for the Job Scraper Application.

This module defines the BaseScraper class, which provides the common interface
and functionality for all site-specific scrapers.
"""

import logging
import time
import random
import requests
from abc import ABC, abstractmethod
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Base class for all job site scrapers.
    
    This abstract class defines the common interface and functionality
    for all site-specific scrapers. Concrete scraper implementations
    should inherit from this class and implement the abstract methods.
    """
    
    def __init__(self, site_config, scraping_settings):
        """
        Initialize the base scraper.
        
        Args:
            site_config: Configuration for the specific job site
            scraping_settings: General scraping settings
        """
        self.site_config = site_config
        self.scraping_settings = scraping_settings
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': scraping_settings['user_agent'],
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
        self.driver = None
    
    def _get_selenium_driver(self):
        """
        Initialize and return a Selenium WebDriver instance.
        
        Returns:
            Selenium WebDriver instance
        """
        if self.driver is not None:
            return self.driver
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={self.scraping_settings['user_agent']}")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            return self.driver
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}", exc_info=True)
            raise
    
    def _close_selenium_driver(self):
        """Close the Selenium WebDriver if it's open."""
        if self.driver is not None:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error closing Selenium WebDriver: {e}")
            finally:
                self.driver = None
    
    def _get_page_content(self, url, use_selenium=False):
        """
        Get the HTML content of a page.
        
        Args:
            url: URL of the page to fetch
            use_selenium: Whether to use Selenium for dynamic content
            
        Returns:
            BeautifulSoup object representing the page content
        """
        try:
            if use_selenium or self.scraping_settings.get('use_selenium_for_dynamic_sites', False):
                driver = self._get_selenium_driver()
                driver.get(url)
                # Wait for dynamic content to load
                time.sleep(3)
                html_content = driver.page_source
            else:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                html_content = response.text
            
            # Add a random delay to avoid rate limiting
            delay = self.scraping_settings.get('request_delay', 2)
            time.sleep(delay + random.uniform(0, 1))
            
            return BeautifulSoup(html_content, 'lxml')
        except Exception as e:
            logger.error(f"Error fetching page content from {url}: {e}", exc_info=True)
            raise
    
    def _extract_text(self, element):
        """
        Extract text from a BeautifulSoup element, handling None values.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Extracted text or None if the element is None
        """
        if element is None:
            return None
        return element.get_text(strip=True)
    
    def _extract_attribute(self, element, attribute):
        """
        Extract an attribute from a BeautifulSoup element, handling None values.
        
        Args:
            element: BeautifulSoup element
            attribute: Attribute name to extract
            
        Returns:
            Attribute value or None if the element is None
        """
        if element is None:
            return None
        return element.get(attribute)
    
    def _parse_date(self, date_string, format_string=None):
        """
        Parse a date string into a datetime object.
        
        Args:
            date_string: Date string to parse
            format_string: Format string for parsing (if None, try common formats)
            
        Returns:
            Datetime object or None if parsing fails
        """
        if not date_string:
            return None
        
        date_string = date_string.strip()
        
        # Try parsing with the provided format
        if format_string:
            try:
                return datetime.strptime(date_string, format_string)
            except ValueError:
                pass
        
        # Try common formats
        common_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%B %d, %Y',
            '%b %d, %Y',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ'
        ]
        
        for fmt in common_formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        # Try to handle relative dates like "2 days ago", "1 week ago", etc.
        try:
            if "today" in date_string.lower():
                return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            elif "yesterday" in date_string.lower():
                from datetime import timedelta
                return (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif "ago" in date_string.lower():
                from datetime import timedelta
                parts = date_string.lower().split()
                if len(parts) >= 3 and parts[1] in ["day", "days", "week", "weeks", "month", "months"]:
                    try:
                        amount = int(parts[0])
                        unit = parts[1]
                        if unit in ["day", "days"]:
                            return datetime.now() - timedelta(days=amount)
                        elif unit in ["week", "weeks"]:
                            return datetime.now() - timedelta(days=amount * 7)
                        elif unit in ["month", "months"]:
                            return datetime.now() - timedelta(days=amount * 30)
                    except (ValueError, IndexError):
                        pass
        except Exception:
            pass
        
        logger.warning(f"Failed to parse date string: {date_string}")
        return None
    
    @abstractmethod
    def scrape(self):
        """
        Scrape job listings from the job site.
        
        This method should be implemented by concrete scraper classes.
        
        Returns:
            List of dictionaries containing job listing data
        """
        pass
    
    def __del__(self):
        """Clean up resources when the scraper is destroyed."""
        self._close_selenium_driver()
