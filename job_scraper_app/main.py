#!/usr/bin/env python3
"""
Job Scraper Application - Main Entry Point

This script initializes and runs the job scraper application, which:
1. Scrapes job listings from configured job sites
2. Stores job information in a database
3. Processes user resumes
4. Generates tailored application materials
5. Provides a web interface for user interaction
"""

import os
import sys
import json
import logging
from pathlib import Path
import argparse

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

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Import application modules
try:
    # Use relative imports
    from database.setup import setup_database
    from scrapers.scraper_manager import ScraperManager
    from ui.app import create_app
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.error("Please ensure all dependencies are installed by running: pip install -r requirements.txt")
    sys.exit(1)

def load_config():
    """Load the application configuration from config.json"""
    try:
        config_path = project_dir / "config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info("Configuration loaded successfully")
        return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load configuration: {e}")
        logger.error("Please ensure config.json exists and contains valid JSON")
        sys.exit(1)

def create_required_directories(config):
    """Create any required directories specified in the configuration"""
    try:
        # Create database directory if it doesn't exist
        db_dir = project_dir / Path(config["database"]["path"]).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Create resume storage directory if it doesn't exist
        resume_dir = project_dir / config["resume_settings"]["storage_path"]
        resume_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Required directories created successfully")
    except Exception as e:
        logger.error(f"Failed to create required directories: {e}")
        sys.exit(1)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Job Scraper Application")
    parser.add_argument("--scrape-only", action="store_true", help="Run only the scraper without starting the web interface")
    parser.add_argument("--rebuild-db", action="store_true", help="Rebuild the database from scratch")
    parser.add_argument("--config", type=str, help="Path to an alternative config file")
    return parser.parse_args()

def main():
    """Main entry point for the application"""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Load configuration
        config = load_config()
        if args.config:
            with open(args.config, 'r') as f:
                custom_config = json.load(f)
                config.update(custom_config)
        
        # Create required directories
        create_required_directories(config)
        
        # Set up the database
        db_path = project_dir / config["database"]["path"]
        db_engine = setup_database(db_path, rebuild=args.rebuild_db)
        
        # Initialize the scraper manager
        scraper_manager = ScraperManager(config, db_engine)
        
        # If scrape-only mode is enabled, run the scraper and exit
        if args.scrape_only:
            logger.info("Running in scrape-only mode")
            scraper_manager.scrape_all_sites()
            logger.info("Scraping completed successfully")
            return
        
        # Create and run the Flask application
        app = create_app(config, db_engine, scraper_manager)
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
