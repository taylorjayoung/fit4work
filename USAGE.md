# Job Scraper Application Usage Guide

This guide explains how to use the Job Scraper Application, including the job scraper and resume processor functionality.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fit4work.git
   cd fit4work
   ```

2. Install the required dependencies:
   ```bash
   pip install -r job_scraper_app/requirements.txt
   ```

3. Set up the database:
   ```bash
   python job_scraper_app/database/setup.py
   ```

## Job Scraper Usage

### Basic Usage

The simplest way to use the job scraper is to use the `ScraperManager` class:

```python
from job_scraper_app.scrapers.scraper_manager import ScraperManager
import json

# Load configuration
with open('job_scraper_app/config.json', 'r') as f:
    config = json.load(f)

# Create a ScraperManager instance
scraper = ScraperManager(config, None)

# Scrape job listings from Remote.co
results = scraper.scrape_site('Remote.co')

# Print the results
print(f'Scraped {len(results)} job listings')
```

### Available Scrapers

The Job Scraper Application includes scrapers for the following job sites:

- Remote.co
- FlexJobs
- RemoteOK
- WeWorkRemotely

You can scrape job listings from a specific site using the `scrape_site` method:

```python
# Scrape job listings from Remote.co
results = scraper.scrape_site('Remote.co')

# Scrape job listings from FlexJobs
results = scraper.scrape_site('FlexJobs')

# Scrape job listings from RemoteOK
results = scraper.scrape_site('RemoteOK')

# Scrape job listings from WeWorkRemotely
results = scraper.scrape_site('WeWorkRemotely')
```

You can also scrape job listings from all available sites using the `scrape_all_sites` method:

```python
# Scrape job listings from all available sites
results = scraper.scrape_all_sites()
```

### Storing Job Listings

The `ScraperManager` class can store job listings in a database. To use this functionality, you need to provide a database engine:

```python
from sqlalchemy import create_engine

# Create a database engine
db_url = 'sqlite:///job_listings.db'
engine = create_engine(db_url)

# Create a ScraperManager instance with the database engine
scraper = ScraperManager(config, engine)

# Scrape job listings and store them in the database
results = scraper.scrape_site('Remote.co')
```

### Retrieving Job Listings

You can retrieve job listings from the database using the `get_job_listings` method:

```python
# Get all job listings
job_listings = scraper.get_job_listings()

# Get job listings from a specific site
job_listings = scraper.get_job_listings(site='Remote.co')

# Get job listings with a specific keyword in the title
job_listings = scraper.get_job_listings(keyword='python')

# Get job listings from a specific site with a specific keyword in the title
job_listings = scraper.get_job_listings(site='Remote.co', keyword='python')
```

## Resume Processor Usage

### Uploading and Parsing Resumes

You can upload and parse resumes using the `ResumeManager` class:

```python
from job_scraper_app.resume_processor.resume_manager import ResumeManager
from sqlalchemy import create_engine

# Create a database engine
db_url = 'sqlite:///job_listings.db'
engine = create_engine(db_url)

# Create a ResumeManager instance
resume_manager = ResumeManager(config, engine)

# Upload a resume
resume_id = resume_manager.upload_resume('path/to/resume.docx', 'My Resume', True)
```

### Generating Tailored Resumes

You can generate tailored resumes for specific job listings:

```python
# Generate a tailored resume for a job listing
tailored_resume_id = resume_manager.generate_tailored_resume(resume_id, job_listing_id)
```

### Retrieving Tailored Resumes

You can retrieve tailored resumes from the database:

```python
# Get all tailored resumes for a specific resume
tailored_resumes = resume_manager.get_tailored_resumes(resume_id=resume_id)

# Get all tailored resumes for a specific job listing
tailored_resumes = resume_manager.get_tailored_resumes(job_listing_id=job_listing_id)

# Get all tailored resumes for a specific resume and job listing
tailored_resumes = resume_manager.get_tailored_resumes(resume_id=resume_id, job_listing_id=job_listing_id)
```

## Example Scripts

The repository includes several example scripts that demonstrate how to use the Job Scraper Application:

- `one_liner_example.py`: Demonstrates how to use the job scraper in a one-liner.
- `resume_processor_example.py`: Demonstrates how to use the resume processor functionality.
- `fix_syntax_error.py`: Explains how to fix a syntax error in a one-liner.
- `syntax_error_fix.py`: Implements the fixed one-liner.

You can run these scripts to see the Job Scraper Application in action:

```bash
python one_liner_example.py
python resume_processor_example.py
python fix_syntax_error.py
python syntax_error_fix.py
```

## Testing

The Job Scraper Application includes a comprehensive test suite. You can run the tests using the following command:

```bash
python -m unittest discover -v
```

Or run specific tests:

```bash
python -m unittest tests.scrapers.test_base_scraper
python -m unittest tests.scrapers.test_remote_co_scraper
python -m unittest tests.scrapers.test_scraper_manager
python -m unittest tests.resume_processor.test_resume_parser
python -m unittest tests.resume_processor.test_resume_generator
python -m unittest tests.resume_processor.test_resume_manager
```

## Configuration

The Job Scraper Application uses a configuration file (`job_scraper_app/config.json`) to store settings. The configuration file should include the following settings:

```json
{
  "database_url": "sqlite:///job_listings.db",
  "resume_settings": {
    "storage_path": "path/to/resume/storage"
  },
  "scraper_settings": {
    "Remote.co": {
      "base_url": "https://remote.co/remote-jobs/",
      "max_pages": 5
    },
    "FlexJobs": {
      "base_url": "https://www.flexjobs.com/remote-jobs",
      "max_pages": 5
    },
    "RemoteOK": {
      "base_url": "https://remoteok.io/remote-jobs",
      "max_pages": 5
    },
    "WeWorkRemotely": {
      "base_url": "https://weworkremotely.com/remote-jobs",
      "max_pages": 5
    }
  }
}
```

You can modify these settings to customize the behavior of the Job Scraper Application.
