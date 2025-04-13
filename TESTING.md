# Testing Guide for Job Scraper Application

This guide explains how to test the different components of the Job Scraper Application.

## Running All Tests and Examples

The easiest way to run all tests and examples is to use the `run_all_tests_and_examples.py` script:

```bash
python run_all_tests_and_examples.py
```

This script will:
1. Run all unit tests
2. Run the one-liner example
3. Run the fixed syntax error example
4. Run the resume processor example
5. Run the test scripts for the fixed one-liner and resume processor

If you only want to run the unit tests, you can use the `run_tests.py` script:

```bash
python run_tests.py
```

This script will discover and run all unit tests in the project.

## Running Specific Tests

You can also run specific tests by providing a path to the `run_tests.py` script:

```bash
# Run all tests in the scrapers directory
python run_tests.py tests/scrapers

# Run all tests in the resume_processor directory
python run_tests.py tests/resume_processor
```

Alternatively, you can use the `unittest` module directly:

```bash
# Run all tests
python -m unittest discover -v

# Run specific test modules
python -m unittest tests.scrapers.test_base_scraper
python -m unittest tests.scrapers.test_remote_co_scraper
python -m unittest tests.scrapers.test_scraper_manager
python -m unittest tests.resume_processor.test_resume_parser
python -m unittest tests.resume_processor.test_resume_generator
python -m unittest tests.resume_processor.test_resume_manager
```

## Testing the Job Scraper

To test the job scraper functionality, you can run the example scripts:

```bash
# Test the one-liner example
python one_liner_example.py

# Test the fixed syntax error example
python syntax_error_fix.py

# See explanations of the syntax error and fixes
python fix_syntax_error.py

# Run a test script for the fixed one-liner
python test_fixed_one_liner.py
```

These scripts demonstrate how to use the job scraper to scrape job listings from Remote.co.

## Testing the Resume Processor

To test the resume processor functionality, you can run the resume processor example scripts:

```bash
# Run the basic resume processor example
python resume_processor_example.py

# Run a more comprehensive test that creates a sample resume
python test_resume_processor.py
```

This script demonstrates how to:
1. Upload and parse a resume
2. Scrape job listings
3. Generate a tailored resume for a job listing
4. Get tailored resumes for a specific resume

**Note**: This script requires a sample resume file in DOCX or PDF format. You'll need to create a sample resume and save it in the resume directory specified in the configuration file.

## Manual Testing

You can also manually test the components by importing them in your own scripts or in an interactive Python session:

```python
# Import the ScraperManager
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

## Testing with Different Job Sites

The job scraper supports multiple job sites. You can test scraping from different sites by changing the site name in the `scrape_site` method:

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

## Testing with Different Resume Formats

The resume processor supports both DOCX and PDF formats. You can test parsing different resume formats by providing different file paths to the `upload_resume` method:

```python
# Upload a DOCX resume
resume_id = resume_manager.upload_resume('path/to/resume.docx', 'My DOCX Resume', True)

# Upload a PDF resume
resume_id = resume_manager.upload_resume('path/to/resume.pdf', 'My PDF Resume', True)
```

## Troubleshooting

If you encounter any issues while testing, check the following:

1. **Configuration**: Make sure the configuration file (`job_scraper_app/config.json`) exists and contains the correct settings.
2. **Dependencies**: Make sure all required dependencies are installed.
3. **File Paths**: Make sure the file paths in your scripts are correct.
4. **Database**: Make sure the database is set up correctly if you're using database functionality.
5. **Logs**: Check the log files for error messages.

## Conclusion

By following this testing guide, you can ensure that all components of the Job Scraper Application are working correctly. If you encounter any issues, refer to the documentation or check the test files for examples of how to use the different components.
