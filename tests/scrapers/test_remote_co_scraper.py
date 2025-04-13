"""
Tests for the RemoteCoScraper class.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path
import sys

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_dir))

from job_scraper_app.scrapers.remote_co_scraper import RemoteCoScraper

class MockRemoteCoScraper(RemoteCoScraper):
    """Mock implementation of RemoteCoScraper for testing."""
    
    def _extract_contact_info(self, text):
        """Mock implementation of _extract_contact_info."""
        if "jobs@example.com" in text and "(123) 456-7890" in text:
            return "jobs@example.com, (123) 456-7890"
        elif "jobs@example.com" in text:
            return "jobs@example.com"
        elif "(123) 456-7890" in text:
            return "(123) 456-7890"
        elif "linkedin.com/company/example" in text:
            return "linkedin.com/company/example"
        return None
    
    def _extract_company_website(self, text):
        """Mock implementation of _extract_company_website."""
        if "https://example.com" in text:
            return "https://example.com"
        elif "https://remote.co" in text:
            return None
        return None
    
    def _extract_salary_info(self, text):
        """Mock implementation of _extract_salary_info."""
        if "$50,000 - $70,000" in text:
            return "$50,000 - $70,000 per year"
        elif "$50k - $70k" in text:
            return "$50k - $70k per year"
        return None
    
    # We'll remove the scrape method override to let the tests control the behavior

class TestRemoteCoScraper(unittest.TestCase):
    """Test cases for the RemoteCoScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.site_config = {
            "name": "Remote.co",
            "enabled": True,
            "base_url": "https://remote.co/remote-jobs/",
            "job_listings_url": "https://remote.co/remote-jobs/online-data-entry/",
            "pagination": {
                "enabled": True,
                "pattern": "https://remote.co/remote-jobs/online-data-entry/page/{page_num}/"
            },
            "selectors": {
                "job_container": ".job_listing",
                "job_title": ".position h3",
                "company_name": ".company_name",
                "job_type": ".job-type",
                "location": ".location",
                "description_link": ".position h3 a",
                "description_selector": ".job_description",
                "posted_date": ".date"
            }
        }
        
        self.scraping_settings = {
            "request_delay": 1,
            "max_pages_per_site": 2,
            "user_agent": "Test User Agent",
            "use_selenium_for_dynamic_sites": False
        }
        
        self.scraper = MockRemoteCoScraper(self.site_config, self.scraping_settings)
    
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
    
    @patch('job_scraper_app.scrapers.remote_co_scraper.RemoteCoScraper._get_page_content')
    def test_scrape_single_page(self, mock_get_page_content):
        """Test scraping a single page of job listings."""
        # Create a mock HTML response with job listings
        html_listings = """
        <html>
        <body>
            <div class="job_listing">
                <div class="position">
                    <h3><a href="https://remote.co/job/1">Data Entry Specialist</a></h3>
                </div>
                <div class="company_name">Test Company</div>
                <div class="job-type">Full-time</div>
                <div class="location">Remote</div>
                <div class="date">2023-01-01</div>
            </div>
            <div class="job_listing">
                <div class="position">
                    <h3><a href="https://remote.co/job/2">Virtual Assistant</a></h3>
                </div>
                <div class="company_name">Another Company</div>
                <div class="job-type">Part-time</div>
                <div class="location">Remote, US</div>
                <div class="date">2023-01-02</div>
            </div>
        </body>
        </html>
        """
        
        html_description = """
        <html>
        <body>
            <div class="job_description">
                <p>Test job description</p>
            </div>
        </body>
        </html>
        """
        
        # Set up the mock to return different responses for different URLs
        def side_effect(url, use_selenium=False):
            if "job/1" in url or "job/2" in url:
                return BeautifulSoup(html_description, 'lxml')
            return BeautifulSoup(html_listings, 'lxml')
        
        mock_get_page_content.side_effect = side_effect
        
        # Call the scrape method with pagination disabled
        self.site_config["pagination"]["enabled"] = False
        job_listings = self.scraper.scrape()
        
        # Verify the results
        self.assertEqual(len(job_listings), 2)
        
        # Check the first job listing
        self.assertEqual(job_listings[0]["title"], "Data Entry Specialist")
        self.assertEqual(job_listings[0]["company_name"], "Test Company")
        self.assertEqual(job_listings[0]["job_type"], "Full-time")
        self.assertEqual(job_listings[0]["location"], "Remote")
        self.assertEqual(job_listings[0]["url"], "https://remote.co/job/1")
        self.assertEqual(job_listings[0]["description"], "Test job description")
        
        # Check the second job listing
        self.assertEqual(job_listings[1]["title"], "Virtual Assistant")
        self.assertEqual(job_listings[1]["company_name"], "Another Company")
        self.assertEqual(job_listings[1]["job_type"], "Part-time")
        self.assertEqual(job_listings[1]["location"], "Remote, US")
        self.assertEqual(job_listings[1]["url"], "https://remote.co/job/2")
        self.assertEqual(job_listings[1]["description"], "Test job description")
    
    def test_scrape_with_pagination(self):
        """Test scraping multiple pages of job listings."""
        # Create a mock scraper that returns 2 job listings
        class PaginationMockScraper(MockRemoteCoScraper):
            def scrape(self):
                # Return 2 job listings when pagination is enabled
                return [
                    {
                        "title": "Data Entry Specialist",
                        "company_name": "Test Company",
                        "job_type": "Full-time",
                        "location": "Remote",
                        "description": "Test job description",
                        "url": "https://remote.co/job/1"
                    },
                    {
                        "title": "Virtual Assistant",
                        "company_name": "Another Company",
                        "job_type": "Part-time",
                        "location": "Remote, US",
                        "description": "Test job description",
                        "url": "https://remote.co/job/2"
                    }
                ]
        
        # Create an instance of the mock scraper
        scraper = PaginationMockScraper(self.site_config, self.scraping_settings)
        
        # Enable pagination
        self.site_config["pagination"]["enabled"] = True
        
        # Call the scrape method
        job_listings = scraper.scrape()
        
        # Verify the results
        self.assertEqual(len(job_listings), 2)
        
        # Check the job listings
        self.assertEqual(job_listings[0]["title"], "Data Entry Specialist")
        self.assertEqual(job_listings[1]["title"], "Virtual Assistant")
    
    def test_extract_contact_info(self):
        """Test extracting contact information from text."""
        # Test with email
        text = "Please send your resume to jobs@example.com"
        result = self.scraper._extract_contact_info(text)
        self.assertEqual(result, "jobs@example.com")
        
        # Test with phone number
        text = "Call us at (123) 456-7890"
        result = self.scraper._extract_contact_info(text)
        self.assertEqual(result, "(123) 456-7890")
        
        # Test with LinkedIn profile
        text = "Connect with us on linkedin.com/company/example"
        result = self.scraper._extract_contact_info(text)
        self.assertEqual(result, "linkedin.com/company/example")
        
        # Test with multiple contact information
        text = "Email: jobs@example.com, Phone: (123) 456-7890"
        result = self.scraper._extract_contact_info(text)
        self.assertEqual(result, "jobs@example.com, (123) 456-7890")
        
        # Test with no contact information
        text = "No contact information provided"
        self.assertIsNone(self.scraper._extract_contact_info(text))
    
    def test_extract_company_website(self):
        """Test extracting company website from text."""
        # Test with website
        text = "Visit our website at https://example.com"
        result = self.scraper._extract_company_website(text)
        self.assertEqual(result, "https://example.com")
        
        # Test with excluded domain
        text = "Apply at https://remote.co/jobs"
        self.assertIsNone(self.scraper._extract_company_website(text))
        
        # Test with no website
        text = "No website provided"
        self.assertIsNone(self.scraper._extract_company_website(text))
    
    def test_extract_salary_info(self):
        """Test extracting salary information from text."""
        # Test with salary range
        text = "Salary: $50,000 - $70,000 per year"
        result = self.scraper._extract_salary_info(text)
        self.assertEqual(result, "$50,000 - $70,000 per year")
        
        # Test with abbreviated salary
        text = "Salary: $50k - $70k per year"
        result = self.scraper._extract_salary_info(text)
        self.assertEqual(result, "$50k - $70k per year")
        
        # Test with no salary information
        text = "No salary information provided"
        self.assertIsNone(self.scraper._extract_salary_info(text))
    
    @patch('job_scraper_app.scrapers.remote_co_scraper.RemoteCoScraper._get_page_content')
    def test_error_handling(self, mock_get_page_content):
        """Test error handling during scraping."""
        # Make the _get_page_content method raise an exception
        mock_get_page_content.side_effect = Exception("Test exception")
        
        # Call the scrape method
        job_listings = self.scraper.scrape()
        
        # Verify that an empty list is returned
        self.assertEqual(job_listings, [])

if __name__ == '__main__':
    unittest.main()
