# Job Scraper Application

A comprehensive application for scraping job listings from multiple job sites, managing resumes, generating tailored application materials, and tracking job applications.

## Features

- **Job Scraping**: Automatically scrape job listings from multiple job boards (Remote.co, WeWorkRemotely, RemoteOK, FlexJobs)
- **Resume Management**: Upload and manage resumes, generate tailored versions for specific job listings
- **Application Tracking**: Track job applications, their status, and related materials
- **Outreach Message Generation**: Generate customized cold emails and follow-up messages
- **Web Interface**: User-friendly web interface for all functionality

## Project Structure

```
job_scraper_app/
├── database/           # Database models and operations
├── scrapers/           # Job scraping modules
├── resume_processor/   # Resume parsing and generation
├── message_generator/  # Outreach message creation
├── ui/                 # Web interface (Flask)
│   └── templates/      # HTML templates
├── config.json         # Application configuration
├── requirements.txt    # Dependencies
└── main.py             # Application entry point
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/job-scraper-app.git
   cd job-scraper-app
   ```

2. Install dependencies:
   ```
   pip install -r job_scraper_app/requirements.txt
   ```

## Usage

### Running the Demo Application

To run a simple demo of the application:

```
python simple_flask_app.py
```

This will start a Flask server on http://localhost:8080 that displays information about the Job Scraper App.

### Development Status

The application is currently under development. The following components have been implemented:

- Database models and setup
- Job scrapers for multiple sites
- Resume processing
- Message generation
- Web interface templates

We're currently working on resolving some import issues to get the full application running.

## Configuration

The application is configured using the `config.json` file, which includes settings for:

- Database location
- Resume storage path
- Job scraper settings
- Message generation settings

## Dependencies

- Flask: Web framework
- SQLAlchemy: Database ORM
- BeautifulSoup4: HTML parsing
- Requests: HTTP requests
- python-docx: Resume processing
- pdfminer.six: PDF processing
- NLTK and spaCy: Natural language processing

## License

This project is licensed under the MIT License - see the LICENSE file for details.
