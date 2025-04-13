# How to Run Fit4Work

This guide will help you set up and run the Fit4Work application, including how to configure the Anthropic API for AI-powered resume parsing.

## Prerequisites

1. Python 3.8 or higher
2. Git
3. An Anthropic API key (optional, but recommended for better resume parsing)

## Setup Instructions

### 1. Clone the Repository

If you haven't already cloned the repository:

```bash
git clone https://github.com/taylorjayoung/fit4work.git
cd fit4work
```

### 2. Install Dependencies

Install all required dependencies:

```bash
pip install -r job_scraper_app/requirements.txt
```

### 3. Configure Anthropic API (Optional but Recommended)

To use the AI-powered resume parsing feature:

1. Sign up for an account at [Anthropic](https://www.anthropic.com/)
2. Generate an API key from your account dashboard
3. Open `job_scraper_app/config.json`
4. Replace `"YOUR_ANTHROPIC_API_KEY"` with your actual API key:

```json
"ai_services": {
  "anthropic": {
    "enabled": true,
    "api_key": "YOUR_ACTUAL_API_KEY_HERE",
    "model": "claude-3-opus-20240229",
    "max_tokens": 4096,
    "temperature": 0.2
  }
}
```

**Important Security Note**: Never commit your actual API key to a public repository. The config.json file in the repository uses a placeholder value for security reasons.

### 4. Run the Application

Start the Flask application:

```bash
python run_flask_app.py
```

The application will be available at http://localhost:8080

## Using the Application

### 1. Upload a Resume

- Click "Upload Resume" on the home page
- Select your resume file (PDF, DOCX, or TXT format)
- Give it a name and set as primary if desired

### 2. Scrape Job Listings

- Click "Scrape Jobs" on the home page
- Browse the job listings that appear

### 3. Generate Tailored Resumes

- From a job listing page, click "Generate Tailored Resume"
- The system will create a version optimized for that specific job

### 4. Create Applications

- From a job listing page, click "Create Application"
- Track your application status

## Troubleshooting

### Resume Parsing Issues

If you encounter issues with resume parsing:

1. Check that your Anthropic API key is correctly configured
2. Ensure your resume is in a supported format (PDF, DOCX, or TXT)
3. Check the application logs in `app.log` for detailed error messages

### Database Issues

If you encounter database issues, you can rebuild the database:

```bash
python run_flask_app.py --rebuild-db
```

## Additional Information

- Resumes are stored in `job_scraper_app/user_data/resumes/`
- The database is located at `job_scraper_app/database/jobs.db`
- Configuration settings are in `job_scraper_app/config.json`
- For more detailed usage instructions, see `FIT4WORK_USAGE.md`
