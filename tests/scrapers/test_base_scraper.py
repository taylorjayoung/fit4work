"""
Tests for the BaseScraper class.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path
import sys

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_dir))

from job_scraper_app.scrapers.base_scraper import BaseScraper

class MockBaseScraper(BaseScraper):
    """Mock implementation of BaseScraper for testing."""
    
    def scrape(self):
        """Implement the abstract method for testing."""
        return []

class TestBaseScraper(unittest.TestCase):
    """Test cases for the BaseScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.site_config = {
            "name": "Test Site",
            "enabled": True,
            "base_url": "https://example.com/",
            "job_listings_url": "https://example.com/jobs/",
            "pagination": {
                "enabled": False
            },
            "selectors": {
                "job_container": ".job",
                "job_title": ".title",
                "company_name": ".company",
                "job_type": ".job-type",
                "location": ".location",
                "description_link": ".title a",
                "description_selector": ".description",
                "posted_date": ".date"
            }
        }
        
        self.scraping_settings = {
            "request_delay": 1,
            "max_pages_per_site": 2,
            "user_agent": "Test User Agent",
            "use_selenium_for_dynamic_sites": False
        }
        
        self.scraper = MockBaseScraper(self.site_config, self.scraping_settings)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.scraper = None
    
    def test_initialization(self):
        """Test that the scraper initializes correctly."""
        self.assertEqual(self.scraper.site_config, self.site_config)
        self.assertEqual(self.scraper.scraping_settings, self.scraping_settings)
        self.assertIsNotNone(self.scraper.session)
        self.assertEqual(self.scraper.session.headers["User-Agent"], "Test User Agent")
        self.assertIsNone(self.scraper.driver)
    
    @patch('requests.Session.get')
    def test_get_page_content(self, mock_get):
        """Test the _get_page_content method."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.text = "<html><body><div class='job'>Test Job</div></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Call the method
        soup = self.scraper._get_page_content("https://example.com/jobs/")
        
        # Verify the result
        self.assertIsInstance(soup, BeautifulSoup)
        self.assertEqual(soup.select_one('.job').text, "Test Job")
        
        # Verify the mock was called correctly
        mock_get.assert_called_once_with("https://example.com/jobs/", timeout=30)
        mock_response.raise_for_status.assert_called_once()
    
    def test_extract_text(self):
        """Test the _extract_text method."""
        # Test with a valid element
        soup = BeautifulSoup("<div>Test Text</div>", "lxml")
        element = soup.select_one("div")
        self.assertEqual(self.scraper._extract_text(element), "Test Text")
        
        # Test with None
        self.assertIsNone(self.scraper._extract_text(None))
    
    def test_extract_attribute(self):
        """Test the _extract_attribute method."""
        # Test with a valid element
        soup = BeautifulSoup("<a href='https://example.com'>Link</a>", "lxml")
        element = soup.select_one("a")
        self.assertEqual(self.scraper._extract_attribute(element, "href"), "https://example.com")
        
        # Test with None
        self.assertIsNone(self.scraper._extract_attribute(None, "href"))
        
        # Test with missing attribute
        self.assertIsNone(self.scraper._extract_attribute(element, "id"))
    
    def test_parse_date(self):
        """Test the _parse_date method."""
        # Test with a valid date string
        date_string = "2023-01-01"
        expected_date = datetime(2023, 1, 1)
        self.assertEqual(self.scraper._parse_date(date_string), expected_date)
        
        # Test with None
        self.assertIsNone(self.scraper._parse_date(None))
        
        # Test with invalid date string
        self.assertIsNone(self.scraper._parse_date("invalid date"))
        
        # Test with relative date strings
        self.assertIsNotNone(self.scraper._parse_date("today"))
        self.assertIsNotNone(self.scraper._parse_date("yesterday"))
        self.assertIsNotNone(self.scraper._parse_date("2 days ago"))
        self.assertIsNotNone(self.scraper._parse_date("1 week ago"))
        self.assertIsNotNone(self.scraper._parse_date("3 months ago"))

if __name__ == '__main__':
    unittest.main()
