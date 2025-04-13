# Fit4Work Application Usage Guide

Fit4Work is a comprehensive job application tool that helps you manage your job search process, from finding job listings to creating tailored resumes and tracking applications.

## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r job_scraper_app/requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python improved_flask_app.py
   ```

3. **Access the Application**:
   Open your web browser and go to http://localhost:8080

## Core Features

### 1. Resume Management

#### Uploading a Resume
1. From the home page, click the "Upload Resume" button
2. In the modal that appears:
   - Select your resume file (PDF or DOCX format)
   - Give your resume a name (optional)
   - Check "Make this my primary resume" if it's your main resume
   - Click "Upload"

#### Managing Resumes
1. Click "Manage Resumes" from the home page
2. Here you can:
   - View all your uploaded resumes
   - Set a resume as your primary resume
   - Delete resumes
   - View resume details

#### Viewing Resume Details
1. Click "View Details" on any resume
2. On the resume detail page, you can:
   - See the resume content
   - View skills detected from your resume
   - See improvement suggestions
   - View tailored versions of this resume

### 2. Job Listings

#### Scraping Job Listings
1. From the home page, click the "Scrape Jobs" button
2. The application will scrape job listings from multiple job boards
3. Once complete, you'll be redirected to the job listings page

#### Browsing Job Listings
1. Click "View Job Listings" from the home page
2. Here you can:
   - Browse all scraped job listings
   - Filter listings by title, company, job type, etc.
   - Click on any listing to view details

#### Viewing Job Listing Details
1. Click on any job listing to view its details
2. On the job listing detail page, you can:
   - See the full job description
   - Generate a tailored resume for this job
   - Create an application for this job

### 3. Tailored Resumes

#### Generating a Tailored Resume
1. From a job listing detail page, click "Generate Tailored Resume"
2. Select your base resume (your primary resume is selected by default)
3. The system will analyze the job description and your resume to create a tailored version
4. The tailored resume will highlight skills and experience relevant to the specific job

### 4. Job Applications

#### Creating an Application
1. From a job listing detail page, click "Create Application"
2. Select a resume to attach (either your regular resume or a tailored one)
3. Add any notes about the application
4. Click "Create Application"

#### Managing Applications
1. Click "View Applications" from the home page
2. Here you can:
   - View all your job applications
   - Track the status of each application
   - Click on any application to view details

#### Viewing Application Details
1. Click on any application to view its details
2. On the application detail page, you can:
   - See the job listing and resume used
   - Generate outreach messages
   - Update the application status

### 5. Outreach Messages

#### Generating Outreach Messages
1. From an application detail page, click "Generate Message"
2. Select the message type (cold email or follow-up)
3. The system will generate a customized message based on the job listing and your resume

## Workflow Example

1. **Upload your resume**
   - Click "Upload Resume" on the home page
   - Select your resume file and give it a name
   - Set it as your primary resume

2. **Scrape job listings**
   - Click "Scrape Jobs" on the home page
   - Browse the job listings and find interesting opportunities

3. **Generate tailored resumes**
   - For each interesting job, click "Generate Tailored Resume"
   - The system will create a version of your resume optimized for that job

4. **Create applications**
   - For each job you want to apply to, click "Create Application"
   - Attach the tailored resume and add any notes

5. **Generate outreach messages**
   - For each application, generate a cold email or follow-up message
   - Use these messages when contacting employers

## Troubleshooting

If you encounter any issues:

1. Check the application logs in `app.log`
2. Ensure all dependencies are installed
3. Make sure the database and resume storage directories exist and are writable
4. If the application fails to start, try running with the `--rebuild-db` flag:
   ```bash
   python improved_flask_app.py --rebuild-db
   ```

## AI-Powered Resume Parsing

Fit4Work now includes AI-powered resume parsing using Anthropic's Claude API. This feature provides more intelligent and accurate extraction of information from your resumes, regardless of their format or structure.

### Setting Up Anthropic API

1. **Get an API Key**:
   - Sign up for an account at [Anthropic](https://www.anthropic.com/)
   - Generate an API key from your account dashboard

2. **Configure the API Key**:
   - Open `job_scraper_app/config.json`
   - Find the `ai_services` section
   - Replace `"YOUR_ANTHROPIC_API_KEY"` with your actual API key:
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

3. **Benefits of AI Parsing**:
   - More accurate identification of resume sections
   - Better extraction of skills, experience, and education
   - Works with various resume formats and structures
   - Provides more detailed and structured information

## Additional Information

- Resumes are stored in `job_scraper_app/user_data/resumes/`
- The database is located at `job_scraper_app/database/jobs.db`
- Configuration settings are in `job_scraper_app/config.json`
- Supported resume formats: PDF, DOCX, and TXT
