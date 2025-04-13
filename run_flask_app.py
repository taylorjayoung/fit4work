#!/usr/bin/env python3
"""
Run script for the Job Scraper Application.

This script directly creates and runs the Flask application without using the main.py file.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Get the path to the job_scraper_app directory
        app_dir = Path(__file__).resolve().parent / "job_scraper_app"
        
        # Add the app directory to the Python path
        sys.path.insert(0, str(app_dir))
        
        # Change to the app directory
        os.chdir(app_dir)
        
        # Import the required modules
        try:
            # Import directly from the modules
            from database.setup import setup_database
            from scrapers.scraper_manager import ScraperManager
            from ui.app import create_app
        except ImportError as e:
            logger.error(f"Failed to import required modules: {e}")
            logger.error("Please ensure all dependencies are installed by running: pip install -r requirements.txt")
            sys.exit(1)
        
        # Load the configuration
        try:
            config_path = app_dir / "config.json"
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info("Configuration loaded successfully")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.error("Please ensure config.json exists and contains valid JSON")
            sys.exit(1)
        
        # Create required directories
        try:
            # Create database directory if it doesn't exist
            db_dir = app_dir / Path(config["database"]["path"]).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # Create resume storage directory if it doesn't exist
            resume_dir = app_dir / config["resume_settings"]["storage_path"]
            resume_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info("Required directories created successfully")
        except Exception as e:
            logger.error(f"Failed to create required directories: {e}")
            sys.exit(1)
        
        # Set up the database
        db_path = app_dir / config["database"]["path"]
        db_engine = setup_database(db_path, rebuild=False)
        
        # Initialize the scraper manager
        scraper_manager = ScraperManager(config, db_engine)
        
        # Create and run the Flask application
        app = create_app(config, db_engine, scraper_manager)
        logger.info("Starting Flask application on http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
