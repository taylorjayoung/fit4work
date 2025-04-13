"""
Tests for the ScraperManager class.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import json
from datetime import datetime
from pathlib import Path
import sys

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_dir))

from job_scraper_app.scrapers.scraper_manager import ScraperManager
from job_scraper_app.scrapers.base_scraper import BaseScraper

class MockScraper(BaseScraper):
    """Mock scraper for testing."""
    
    def __init__(self, site_config, scraping_settings, job_listings=None):
        """Initialize the mock scraper."""
        super().__init__(site_config, scraping_settings)
        self.job_listings = job_listings or []
    
    def scrape(self):
        """Return mock job listings."""
        return self.job_listings

class TestScraperManager(unittest.TestCase):
    """Test cases for the ScraperManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "job_sites": [
                {
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
                },
                {
                    "name": "We Work Remotely",
                    "enabled": True,
                    "base_url": "https://weworkremotely.com/",
                    "job_listings_url": "https://weworkremotely.com/remote-jobs/search?term=data+entry",
                    "pagination": {
                        "enabled": False
                    },
                    "selectors": {
                        "job_container": ".job",
                        "job_title": ".title",
                        "company_name": ".company",
                        "job_type": ".job-type",
                        "location": ".region",
                        "description_link": ".title a",
                        "description_selector": ".listing-container",
                        "posted_date": ".date"
                    }
                },
                {
                    "name": "Disabled Site",
                    "enabled": False,
                    "base_url": "https://example.com/",
                    "job_listings_url": "https://example.com/jobs/",
                    "pagination": {
                        "enabled": False
                    },
                    "selectors": {}
                }
            ],
            "scraping_settings": {
                "request_delay": 1,
                "max_pages_per_site": 2,
                "user_agent": "Test User Agent",
                "use_selenium_for_dynamic_sites": False
            }
        }
        
        # Create a mock database engine
        self.db_engine = MagicMock()
        
        # Create a mock Session class
        self.mock_session = MagicMock()
        self.mock_session_instance = MagicMock()
        self.mock_session.return_value = self.mock_session_instance
        
        # Create a mock JobListing class
        self.mock_job_listing = MagicMock()
        
        # Patch the sessionmaker and JobListing
        self.sessionmaker_patcher = patch('job_scraper_app.scrapers.scraper_manager.sessionmaker', return_value=self.mock_session)
        self.job_listing_patcher = patch('job_scraper_app.scrapers.scraper_manager.JobListing', self.mock_job_listing)
        
        # Start the patches
        self.mock_sessionmaker = self.sessionmaker_patcher.start()
        self.mock_job_listing_class = self.job_listing_patcher.start()
        
        # Create the ScraperManager
        self.scraper_manager = ScraperManager(self.config, self.db_engine)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Stop the patches
        self.sessionmaker_patcher.stop()
        self.job_listing_patcher.stop()
        
        self.scraper_manager = None
    
    def test_initialization(self):
        """Test that the ScraperManager initializes correctly."""
        # Check that the config and db_engine are set correctly
        self.assertEqual(self.scraper_manager.config, self.config)
        self.assertEqual(self.scraper_manager.db_engine, self.db_engine)
        
        # Check that the Session is created correctly
        self.mock_sessionmaker.assert_called_once_with(bind=self.db_engine)
        self.assertEqual(self.scraper_manager.Session, self.mock_session)
        
        # Check that the scrapers are initialized correctly
        self.assertEqual(len(self.scraper_manager.scrapers), 2)
        self.assertIn("Remote.co", self.scraper_manager.scrapers)
        self.assertIn("We Work Remotely", self.scraper_manager.scrapers)
        self.assertNotIn("Disabled Site", self.scraper_manager.scrapers)
    
    @patch('job_scraper_app.scrapers.scraper_manager.RemoteCoScraper')
    @patch('job_scraper_app.scrapers.scraper_manager.WeWorkRemotelyScraper')
    def test_initialize_scrapers(self, mock_wwr_scraper, mock_remote_co_scraper):
        """Test the _initialize_scrapers method."""
        # Create mock scraper instances
        mock_remote_co_instance = MagicMock()
        mock_wwr_instance = MagicMock()
        mock_remote_co_scraper.return_value = mock_remote_co_instance
        mock_wwr_scraper.return_value = mock_wwr_instance
        
        # Create a new ScraperManager to trigger _initialize_scrapers
        scraper_manager = ScraperManager(self.config, self.db_engine)
        
        # Check that the scrapers are created correctly
        mock_remote_co_scraper.assert_called_once_with(
            self.config["job_sites"][0],
            self.config["scraping_settings"]
        )
        mock_wwr_scraper.assert_called_once_with(
            self.config["job_sites"][1],
            self.config["scraping_settings"]
        )
        
        # Check that the scrapers are stored correctly
        self.assertEqual(scraper_manager.scrapers["Remote.co"], mock_remote_co_instance)
        self.assertEqual(scraper_manager.scrapers["We Work Remotely"], mock_wwr_instance)
    
    def test_scrape_site(self):
        """Test the scrape_site method."""
        # Create mock job listings
        job_listings = [
            {
                "title": "Data Entry Specialist",
                "company_name": "Test Company",
                "job_type": "Full-time",
                "location": "Remote",
                "description": "Test job description",
                "url": "https://remote.co/job/1",
                "posted_date": "2023-01-01"
            },
            {
                "title": "Virtual Assistant",
                "company_name": "Another Company",
                "job_type": "Part-time",
                "location": "Remote, US",
                "description": "Another job description",
                "url": "https://remote.co/job/2",
                "posted_date": "2023-01-02"
            }
        ]
        
        # Replace the Remote.co scraper with our mock
        self.scraper_manager.scrapers["Remote.co"] = MockScraper(
            self.config["job_sites"][0],
            self.config["scraping_settings"],
            job_listings
        )
        
        # Mock the _store_job_listings method
        self.scraper_manager._store_job_listings = MagicMock()
        
        # Call the scrape_site method
        result = self.scraper_manager.scrape_site("Remote.co")
        
        # Verify the results
        self.assertEqual(result, job_listings)
        
        # Verify that _store_job_listings was called correctly
        self.scraper_manager._store_job_listings.assert_called_once_with(job_listings, "Remote.co")
    
    def test_scrape_site_not_found(self):
        """Test the scrape_site method with a non-existent site."""
        # Call the scrape_site method with a non-existent site
        result = self.scraper_manager.scrape_site("Non-existent Site")
        
        # Verify that an empty list is returned
        self.assertEqual(result, [])
    
    def test_scrape_site_error(self):
        """Test the scrape_site method when an error occurs."""
        # Replace the Remote.co scraper with a mock that raises an exception
        mock_scraper = MagicMock()
        mock_scraper.scrape.side_effect = Exception("Test exception")
        self.scraper_manager.scrapers["Remote.co"] = mock_scraper
        
        # Call the scrape_site method
        result = self.scraper_manager.scrape_site("Remote.co")
        
        # Verify that an empty list is returned
        self.assertEqual(result, [])
    
    @patch('job_scraper_app.scrapers.scraper_manager.ThreadPoolExecutor')
    def test_scrape_all_sites(self, mock_executor_class):
        """Test the scrape_all_sites method."""
        # Create mock job listings for each site
        remote_co_listings = [
            {
                "title": "Data Entry Specialist",
                "company_name": "Test Company",
                "url": "https://remote.co/job/1"
            }
        ]
        
        wwr_listings = [
            {
                "title": "Virtual Assistant",
                "company_name": "Another Company",
                "url": "https://weworkremotely.com/job/1"
            }
        ]
        
        # Create mock scrapers
        self.scraper_manager.scrapers["Remote.co"] = MockScraper(
            self.config["job_sites"][0],
            self.config["scraping_settings"],
            remote_co_listings
        )
        
        self.scraper_manager.scrapers["We Work Remotely"] = MockScraper(
            self.config["job_sites"][1],
            self.config["scraping_settings"],
            wwr_listings
        )
        
        # Create a mock executor
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        # Create mock futures
        mock_future1 = MagicMock()
        mock_future1.result.return_value = remote_co_listings
        
        mock_future2 = MagicMock()
        mock_future2.result.return_value = wwr_listings
        
        # Set up the mock executor to return the futures
        mock_executor.submit.side_effect = [mock_future1, mock_future2]
        mock_executor.__iter__.return_value = [mock_future1, mock_future2]
        
        # Call the scrape_all_sites method
        results = self.scraper_manager.scrape_all_sites()
        
        # Verify the results
        self.assertEqual(results["Remote.co"], remote_co_listings)
        self.assertEqual(results["We Work Remotely"], wwr_listings)
        
        # Verify that the executor was used correctly
        mock_executor_class.assert_called_once_with(max_workers=4)
        mock_executor.submit.assert_has_calls([
            call(self.scraper_manager.scrape_site, "Remote.co"),
            call(self.scraper_manager.scrape_site, "We Work Remotely")
        ])
    
    def test_store_job_listings(self):
        """Test the _store_job_listings method."""
        # Create mock job listings
        job_listings = [
            {
                "title": "Data Entry Specialist",
                "company_name": "Test Company",
                "job_type": "Full-time",
                "location": "Remote",
                "description": "Test job description",
                "url": "https://remote.co/job/1",
                "contact_info": "jobs@test.com",
                "company_website": "https://test.com",
                "salary_info": "$40,000 - $50,000",
                "posted_date": "2023-01-01"
            },
            {
                "title": "Virtual Assistant",
                "company_name": "Another Company",
                "job_type": "Part-time",
                "location": "Remote, US",
                "description": "Another job description",
                "url": "https://remote.co/job/2",
                "contact_info": None,
                "company_website": None,
                "salary_info": None,
                "posted_date": None
            }
        ]
        
        # Set up the mock session to return None for the first job (new) and an existing job for the second
        existing_job = MagicMock()
        self.mock_session_instance.query.return_value.filter_by.return_value.first.side_effect = [None, existing_job]
        
        # Call the _store_job_listings method
        self.scraper_manager._store_job_listings(job_listings, "Remote.co")
        
        # Verify that the session was used correctly
        self.mock_session.assert_called_once()
        
        # Verify that JobListing was created for the first job
        self.mock_job_listing_class.assert_called_once_with(
            title="Data Entry Specialist",
            company_name="Test Company",
            job_type="Full-time",
            location="Remote",
            description="Test job description",
            url="https://remote.co/job/1",
            contact_info="jobs@test.com",
            company_website="https://test.com",
            salary_info="$40,000 - $50,000",
            posted_date="2023-01-01",
            scraped_date=unittest.mock.ANY,
            source_site="Remote.co",
            is_active=True
        )
        
        # Verify that the session was committed
        self.mock_session_instance.commit.assert_called_once()
        
        # Verify that the session was closed
        self.mock_session_instance.close.assert_called_once()
    
    def test_store_job_listings_error(self):
        """Test the _store_job_listings method when an error occurs."""
        # Create mock job listings
        job_listings = [
            {
                "title": "Data Entry Specialist",
                "company_name": "Test Company",
                "url": "https://remote.co/job/1"
            }
        ]
        
        # Make the session raise an exception
        self.mock_session_instance.commit.side_effect = Exception("Test exception")
        
        # Call the _store_job_listings method
        self.scraper_manager._store_job_listings(job_listings, "Remote.co")
        
        # Verify that the session was rolled back
        self.mock_session_instance.rollback.assert_called_once()
        
        # Verify that the session was closed
        self.mock_session_instance.close.assert_called_once()
    
    def test_get_job_listings(self):
        """Test the get_job_listings method."""
        # Create mock job listings
        mock_job_listings = [MagicMock(), MagicMock()]
        
        # Set up the mock session to return the mock job listings
        mock_query = self.mock_session_instance.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = mock_job_listings
        
        # Call the get_job_listings method with various filters
        filters = {
            "title": "Data Entry",
            "company": "Test",
            "job_type": "Full-time",
            "location": "Remote",
            "source_site": "Remote.co",
            "is_active": True
        }
        result = self.scraper_manager.get_job_listings(filters, limit=10, offset=0)
        
        # Verify the results
        self.assertEqual(result, mock_job_listings)
        
        # Verify that the session was used correctly
        self.mock_session.assert_called_once()
        self.mock_session_instance.query.assert_called_once_with(self.mock_job_listing_class)
        
        # Verify that the filters were applied
        mock_query.filter.assert_called()
        mock_query.order_by.assert_called_once()
        mock_query.limit.assert_called_once_with(10)
        mock_query.offset.assert_called_once_with(0)
        mock_query.all.assert_called_once()
        
        # Verify that the session was closed
        self.mock_session_instance.close.assert_called_once()
    
    def test_get_job_listings_error(self):
        """Test the get_job_listings method when an error occurs."""
        # Make the session raise an exception
        self.mock_session_instance.query.side_effect = Exception("Test exception")
        
        # Call the get_job_listings method
        result = self.scraper_manager.get_job_listings()
        
        # Verify that an empty list is returned
        self.assertEqual(result, [])
        
        # Verify that the session was closed
        self.mock_session_instance.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
