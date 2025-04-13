# Job Scraper Application

A comprehensive tool for job seekers to automate the job search process, from finding listings to crafting personalized applications.

## Features

- **Multi-site Job Scraping**: Automatically scrape job listings from multiple configurable job boards
- **Detailed Information Extraction**: Extract company name, job type, description, contact info, and more
- **Centralized Job Database**: Store all job listings in a searchable database
- **Resume Management**: Upload and manage multiple resume versions
- **Tailored Resume Generator**: Create job-specific resumes based on the listing requirements
- **Outreach Message Drafting**: Generate customized cold outreach and follow-up messages
- **Interactive Dashboard**: User-friendly interface to manage the entire job application process

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd job_scraper_app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   python -m database.setup
   ```

5. Download NLP models:
   ```
   python -m spacy download en_core_web_md
   python -m nltk.downloader punkt wordnet stopwords
   ```

## Usage

1. Start the application:
   ```
   python main.py
   ```

2. Access the web interface at `http://localhost:5000`

3. Configure job sites in the `config.json` file or through the web interface

4. Upload your resume(s)

5. Start scraping job listings

6. Review job listings, generate tailored resumes, and draft outreach messages

## Configuration

The application is highly configurable through the `config.json` file:

- **Job Sites**: Add or modify job boards to scrape
- **Scraping Settings**: Adjust request delays, user agents, and other scraping parameters
- **Database Settings**: Configure the database connection
- **Resume Settings**: Set up resume storage and processing options
- **Message Templates**: Customize outreach message templates

## Project Structure

```
job_scraper_app/
├── scrapers/           # Job scraping modules
├── database/           # Database models and operations
├── resume_processor/   # Resume parsing and generation
├── message_generator/  # Outreach message creation
├── ui/                 # Web interface
├── config.json         # Application configuration
├── requirements.txt    # Dependencies
└── main.py             # Application entry point
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
