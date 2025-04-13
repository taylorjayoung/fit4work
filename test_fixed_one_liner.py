#!/usr/bin/env python3
"""
Test script for the fixed one-liner.

This script demonstrates how to test the fixed one-liner by:
1. Importing the function from syntax_error_fix.py
2. Calling the function
3. Verifying the results
"""

import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run the test for the fixed one-liner."""
    try:
        # Import the function from syntax_error_fix.py
        logger.info("Importing scrape_and_print from syntax_error_fix.py...")
        from syntax_error_fix import scrape_and_print
        
        # Call the function
        logger.info("Calling scrape_and_print()...")
        results = scrape_and_print()
        
        # Verify the results
        if results:
            logger.info(f"Success! Scraped {len(results)} job listings.")
            
            # Print details of the first job listing
            if len(results) > 0:
                job = results[0]
                logger.info(f"First job listing:")
                logger.info(f"Title: {job.title}")
                logger.info(f"Company: {job.company_name}")
                logger.info(f"Location: {job.location}")
                logger.info(f"Date Posted: {job.date_posted}")
                logger.info(f"URL: {job.url}")
            
            return 0  # Success
        else:
            logger.error("Failed to scrape job listings.")
            return 1  # Failure
    
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure syntax_error_fix.py is in the current directory.")
        return 1  # Failure
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1  # Failure

if __name__ == "__main__":
    sys.exit(main())
