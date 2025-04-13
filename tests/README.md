# Job Scraper Application Test Suite

This directory contains the test suite for the Job Scraper Application. The tests are organized by feature/component to make it easy to understand and maintain.

## Test Structure

The test suite is organized as follows:

```
tests/
├── __init__.py
├── README.md
├── scrapers/
│   ├── __init__.py
│   ├── test_base_scraper.py
│   ├── test_remote_co_scraper.py
│   └── test_scraper_manager.py
└── resume_processor/
    ├── __init__.py
    ├── test_resume_parser.py
    ├── test_resume_manager.py
    └── test_resume_generator.py
```

### Scrapers Tests

The `scrapers` directory contains tests for the scraper components:

- `test_base_scraper.py`: Tests for the `BaseScraper` class, which provides common functionality for all scrapers.
- `test_remote_co_scraper.py`: Tests for the `RemoteCoScraper` class, which scrapes job listings from Remote.co.
- `test_scraper_manager.py`: Tests for the `ScraperManager` class, which manages the scrapers and stores the scraped job listings.

### Resume Processor Tests

The `resume_processor` directory contains tests for the resume processing components:

- `test_resume_parser.py`: Tests for the `ResumeParser` class, which parses resumes in different formats (PDF, DOCX) and extracts structured information.
- `test_resume_manager.py`: Tests for the `ResumeManager` class, which manages resume operations like uploading, storing, and generating tailored resumes.
- `test_resume_generator.py`: Tests for the `ResumeGenerator` class, which generates tailored resumes based on job listings and user resumes.

## Running the Tests

You can run the tests using the `run_tests.py` script in the project root directory:

```bash
python run_tests.py
```

This will discover and run all tests in the `tests` directory.

You can also run individual test files:

```bash
python -m unittest tests/scrapers/test_base_scraper.py
python -m unittest tests/scrapers/test_remote_co_scraper.py
python -m unittest tests/scrapers/test_scraper_manager.py
```

Or run specific test cases or methods:

```bash
python -m unittest tests.scrapers.test_base_scraper.TestBaseScraper
python -m unittest tests.scrapers.test_base_scraper.TestBaseScraper.test_initialization
```

## Test Coverage

The tests cover the following functionality:

### BaseScraper Tests

- Initialization
- Getting page content
- Extracting text and attributes from HTML elements
- Parsing dates

### RemoteCoScraper Tests

- Initialization
- Scraping a single page of job listings
- Scraping multiple pages with pagination
- Getting job descriptions
- Error handling

### ScraperManager Tests

- Initialization
- Initializing scrapers
- Scraping a specific site
- Scraping all sites
- Storing job listings in the database
- Retrieving job listings from the database
- Error handling

### ResumeParser Tests

- Initialization
- Parsing resumes in different formats (PDF, DOCX)
- Extracting structured information from resumes (name, email, phone, education, experience, skills, links)
- Error handling

### ResumeManager Tests

- Initialization
- Uploading and processing resumes
- Storing resumes in the database
- Generating tailored resumes for specific job listings
- Retrieving tailored resumes
- Error handling

### ResumeGenerator Tests

- Initialization
- Extracting keywords from job listings
- Matching resume skills with job keywords
- Creating tailored resume documents
- Generating professional summaries
- Highlighting relevant skills and experience

## Adding New Tests

When adding new features to the application, you should also add corresponding tests. Follow these guidelines:

1. Create a new test file in the appropriate directory (e.g., `tests/scrapers/test_new_feature.py`).
2. Use the `unittest` framework and follow the existing test structure.
3. Use mocks and patches to isolate the code being tested.
4. Test both normal operation and error handling.
5. Run the tests to ensure they pass.

## Test Dependencies

The tests use the following dependencies:

- `unittest`: The standard Python testing framework
- `unittest.mock`: For mocking objects and patching functions
- `BeautifulSoup`: For parsing HTML
- `pathlib`: For working with file paths
