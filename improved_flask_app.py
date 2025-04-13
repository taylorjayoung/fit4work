#!/usr/bin/env python3
"""
Improved Flask application for the Job Scraper App.

This script creates a Flask application that implements the core functionality
of the Job Scraper App, including resume upload, job scraping, and application tracking.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    from job_scraper_app.database.setup import setup_database, JobListing, Resume, TailoredResume, JobApplication, OutreachMessage
    from job_scraper_app.scrapers.scraper_manager import ScraperManager
    from job_scraper_app.resume_processor.resume_manager import ResumeManager
    from job_scraper_app.message_generator.message_manager import MessageManager
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.error("Please ensure all dependencies are installed by running: pip install -r job_scraper_app/requirements.txt")
    sys.exit(1)

# Load configuration
try:
    config_path = project_dir / "job_scraper_app" / "config.json"
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
    db_dir = project_dir / "job_scraper_app" / Path(config["database"]["path"]).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Create resume storage directory if it doesn't exist
    resume_dir = project_dir / "job_scraper_app" / config["resume_settings"]["storage_path"]
    resume_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Required directories created successfully")
except Exception as e:
    logger.error(f"Failed to create required directories: {e}")
    sys.exit(1)

# Set up the database
db_path = project_dir / "job_scraper_app" / config["database"]["path"]
db_engine = setup_database(db_path, rebuild=False)
Session = sessionmaker(bind=db_engine)

# Initialize managers
scraper_manager = ScraperManager(config, db_engine)
resume_manager = ResumeManager(config, db_engine)
message_manager = MessageManager(config, db_engine)

# Create Flask application
app = Flask(__name__, 
            template_folder=str(project_dir / "job_scraper_app" / "ui" / "templates"),
            static_folder=str(project_dir / "job_scraper_app" / "ui" / "static"))
app.secret_key = os.urandom(24)

# Add custom Jinja2 filters
@app.template_filter('extract_skills')
def extract_skills_filter(text):
    """Extract skills from resume text."""
    if not text:
        return []
    
    # Simple skill extraction based on common skills
    common_skills = [
        'python', 'java', 'javascript', 'html', 'css', 'sql', 'react', 'angular', 'vue',
        'node', 'express', 'django', 'flask', 'spring', 'aws', 'azure', 'docker', 'kubernetes',
        'git', 'agile', 'scrum', 'leadership', 'communication', 'teamwork', 'problem-solving'
    ]
    
    text_lower = text.lower()
    return [skill for skill in common_skills if skill in text_lower]

@app.template_filter('extract_experience')
def extract_experience_filter(text):
    """Extract experience from resume text."""
    if not text:
        return []
    
    # Simple experience extraction - look for lines with years
    lines = text.split('\n')
    experience = []
    
    for line in lines:
        # Look for lines that might contain job titles or years
        if any(year in line for year in ['2020', '2021', '2022', '2023', '2024', '2025']):
            experience.append(line.strip())
    
    return experience[:5]  # Return at most 5 experiences

@app.template_filter('contains')
def contains_filter(value, substring):
    """Check if a string contains a substring."""
    if not value:
        return False
    return substring in value

# Configure the application
app.config['UPLOAD_FOLDER'] = resume_dir
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# Define routes

@app.route('/')
def index():
    """Render the home page."""
    session = Session()
    try:
        # Get recent job listings
        job_listings = session.query(JobListing).order_by(JobListing.scraped_date.desc()).limit(10).all()
        
        # Get recent job applications
        job_applications = session.query(JobApplication).order_by(JobApplication.application_date.desc()).limit(5).all()
        
        # Get resumes
        resumes = session.query(Resume).all()
        
        return render_template('index.html', 
                              job_listings=job_listings, 
                              job_applications=job_applications,
                              resumes=resumes)
    finally:
        session.close()

@app.route('/job_listings')
def job_listings():
    """Render the job listings page."""
    session = Session()
    try:
        # Get all job listings
        job_listings = session.query(JobListing).order_by(JobListing.scraped_date.desc()).all()
        
        # Get unique values for filter dropdowns
        source_sites = session.query(JobListing.source_site).distinct().all()
        job_types = session.query(JobListing.job_type).distinct().all()
        
        return render_template('job_listings.html', 
                              job_listings=job_listings,
                              source_sites=source_sites,
                              job_types=job_types,
                              filters={})
    finally:
        session.close()

@app.route('/job_listing/<int:job_id>')
def job_listing(job_id):
    """Render the job listing detail page."""
    session = Session()
    try:
        # Get the job listing
        job_listing = session.query(JobListing).filter_by(id=job_id).first()
        if not job_listing:
            return "Job listing not found", 404
        
        # Get resumes for generating tailored resumes
        resumes = session.query(Resume).all()
        
        # Get tailored resumes for this job listing
        tailored_resumes = session.query(TailoredResume).filter_by(job_listing_id=job_id).all()
        
        # Get job applications for this job listing
        job_applications = session.query(JobApplication).filter_by(job_listing_id=job_id).all()
        
        return render_template('job_listing.html', 
                              job_listing=job_listing,
                              resumes=resumes,
                              tailored_resumes=tailored_resumes,
                              job_applications=job_applications)
    finally:
        session.close()

@app.route('/scrape', methods=['POST'])
def scrape():
    """Scrape job listings from configured job sites."""
    try:
        # Get the site to scrape (if specified)
        site_name = request.form.get('site_name')
        
        if site_name:
            # Scrape a specific site
            results = scraper_manager.scrape_site(site_name)
            flash(f"Scraped {len(results)} job listings from {site_name}")
        else:
            # Scrape all sites
            results = scraper_manager.scrape_all_sites()
            total_jobs = sum(len(listings) for listings in results.values())
            flash(f"Scraped {total_jobs} job listings from {len(results)} sites")
        
        return redirect(url_for('job_listings'))
    except Exception as e:
        logger.error(f"Error scraping job listings: {e}", exc_info=True)
        flash(f"Error scraping job listings: {str(e)}", "error")
        return redirect(url_for('job_listings'))

@app.route('/resumes')
def resumes():
    """Render the resumes page."""
    session = Session()
    try:
        # Get resumes
        resumes = session.query(Resume).order_by(Resume.upload_date.desc()).all()
        
        return render_template('resumes.html', resumes=resumes)
    finally:
        session.close()

@app.route('/resume/<int:resume_id>')
def resume(resume_id):
    """Render the resume detail page."""
    session = Session()
    try:
        # Get the resume
        resume = session.query(Resume).filter_by(id=resume_id).first()
        if not resume:
            return "Resume not found", 404
        
        # Get tailored resumes based on this resume
        tailored_resumes = session.query(TailoredResume).filter_by(base_resume_id=resume_id).all()
        
        return render_template('resume.html', 
                              resume=resume,
                              tailored_resumes=tailored_resumes)
    finally:
        session.close()

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    """Upload a resume."""
    try:
        # Check if a file was uploaded
        if 'resume' not in request.files:
            flash("No file part", "error")
            return redirect(url_for('resumes'))
        
        file = request.files['resume']
        
        # Check if a file was selected
        if file.filename == '':
            flash("No file selected", "error")
            return redirect(url_for('resumes'))
        
        # Check if the file has an allowed extension
        allowed_extensions = ['.docx', '.pdf']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            flash(f"File extension {file_ext} not allowed", "error")
            return redirect(url_for('resumes'))
        
        # Save the file to a temporary location
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_' + filename)
        file.save(temp_path)
        
        # Get the resume name and primary flag
        name = request.form.get('name', os.path.splitext(filename)[0])
        make_primary = 'make_primary' in request.form
        
        # Upload the resume
        resume_id = resume_manager.upload_resume(temp_path, name, make_primary)
        
        # Remove the temporary file
        os.remove(temp_path)
        
        if resume_id:
            flash(f"Resume '{name}' uploaded successfully")
            return redirect(url_for('resume', resume_id=resume_id))
        else:
            flash("Failed to upload resume", "error")
            return redirect(url_for('resumes'))
    except Exception as e:
        logger.error(f"Error uploading resume: {e}", exc_info=True)
        flash(f"Error uploading resume: {str(e)}", "error")
        return redirect(url_for('resumes'))

@app.route('/generate_tailored_resume', methods=['POST'])
def generate_tailored_resume():
    """Generate a tailored resume for a job listing."""
    try:
        # Get the resume and job listing IDs
        resume_id = request.form.get('resume_id')
        job_listing_id = request.form.get('job_listing_id')
        
        if not resume_id or not job_listing_id:
            flash("Resume ID and job listing ID are required", "error")
            return redirect(url_for('job_listings'))
        
        # Generate the tailored resume
        tailored_resume_id = resume_manager.generate_tailored_resume(int(resume_id), int(job_listing_id))
        
        if tailored_resume_id:
            flash("Tailored resume generated successfully")
            return redirect(url_for('job_listing', job_id=job_listing_id))
        else:
            flash("Failed to generate tailored resume", "error")
            return redirect(url_for('job_listing', job_id=job_listing_id))
    except Exception as e:
        logger.error(f"Error generating tailored resume: {e}", exc_info=True)
        flash(f"Error generating tailored resume: {str(e)}", "error")
        return redirect(url_for('job_listings'))

@app.route('/applications')
def applications():
    """Render the job applications page."""
    session = Session()
    try:
        # Get job applications
        job_applications = session.query(JobApplication).order_by(JobApplication.application_date.desc()).all()
        
        return render_template('applications.html', job_applications=job_applications)
    finally:
        session.close()

@app.route('/application/<int:application_id>')
def application(application_id):
    """Render the job application detail page."""
    session = Session()
    try:
        # Get the job application
        job_application = session.query(JobApplication).filter_by(id=application_id).first()
        if not job_application:
            return "Job application not found", 404
        
        # Get outreach messages for this application
        outreach_messages = session.query(OutreachMessage).filter_by(job_application_id=application_id).order_by(OutreachMessage.creation_date.desc()).all()
        
        return render_template('application.html', 
                              job_application=job_application,
                              outreach_messages=outreach_messages)
    finally:
        session.close()

@app.route('/create_application', methods=['POST'])
def create_application():
    """Create a job application."""
    session = Session()
    try:
        # Get the job listing and resume IDs
        job_listing_id = request.form.get('job_listing_id')
        resume_id = request.form.get('resume_id')
        
        if not job_listing_id:
            flash("Job listing ID is required", "error")
            return redirect(url_for('job_listings'))
        
        # Create the job application
        job_application = JobApplication(
            job_listing_id=int(job_listing_id),
            resume_id=int(resume_id) if resume_id else None,
            status='pending',
            application_date=datetime.utcnow(),
            notes=request.form.get('notes', '')
        )
        
        session.add(job_application)
        session.commit()
        
        flash("Job application created successfully")
        return redirect(url_for('application', application_id=job_application.id))
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating job application: {e}", exc_info=True)
        flash(f"Error creating job application: {str(e)}", "error")
        return redirect(url_for('job_listings'))
    finally:
        session.close()

@app.route('/generate_message', methods=['POST'])
def generate_message():
    """Generate an outreach message for a job application."""
    try:
        # Get the job application ID and message type
        job_application_id = request.form.get('job_application_id')
        message_type = request.form.get('message_type')
        
        if not job_application_id or not message_type:
            flash("Job application ID and message type are required", "error")
            return redirect(url_for('applications'))
        
        # Generate the message
        if message_type == 'cold_email':
            message_id = message_manager.generate_cold_email(int(job_application_id))
        elif message_type == 'follow_up':
            days_since_application = int(request.form.get('days_since_application', 7))
            message_id = message_manager.generate_follow_up(int(job_application_id), days_since_application)
        else:
            flash(f"Invalid message type: {message_type}", "error")
            return redirect(url_for('application', application_id=job_application_id))
        
        if message_id:
            flash("Outreach message generated successfully")
            return redirect(url_for('application', application_id=job_application_id))
        else:
            flash("Failed to generate outreach message", "error")
            return redirect(url_for('application', application_id=job_application_id))
    except Exception as e:
        logger.error(f"Error generating outreach message: {e}", exc_info=True)
        flash(f"Error generating outreach message: {str(e)}", "error")
        return redirect(url_for('applications'))

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download a file."""
    try:
        # Ensure the file is within the upload folder
        requested_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        upload_folder = os.path.abspath(app.config['UPLOAD_FOLDER'])
        
        if not requested_path.startswith(upload_folder):
            flash("Invalid file path", "error")
            return redirect(url_for('index'))
        
        # Get the directory and filename
        directory = os.path.dirname(requested_path)
        filename = os.path.basename(requested_path)
        
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading file: {e}", exc_info=True)
        flash(f"Error downloading file: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/set_primary_resume', methods=['POST'])
def set_primary_resume():
    """Set a resume as the primary resume."""
    session = Session()
    try:
        # Get the resume ID
        resume_id = request.form.get('resume_id')
        
        if not resume_id:
            flash("Resume ID is required", "error")
            return redirect(url_for('resumes'))
        
        # Set all resumes as not primary
        session.query(Resume).update({Resume.is_primary: False})
        
        # Set the selected resume as primary
        resume = session.query(Resume).filter_by(id=int(resume_id)).first()
        if resume:
            resume.is_primary = True
            session.commit()
            flash(f"Resume '{resume.name}' set as primary")
        else:
            flash("Resume not found", "error")
        
        return redirect(url_for('resumes'))
    except Exception as e:
        session.rollback()
        logger.error(f"Error setting primary resume: {e}", exc_info=True)
        flash(f"Error setting primary resume: {str(e)}", "error")
        return redirect(url_for('resumes'))
    finally:
        session.close()

@app.route('/delete_resume', methods=['POST'])
def delete_resume():
    """Delete a resume."""
    session = Session()
    try:
        # Get the resume ID
        resume_id = request.form.get('resume_id')
        
        if not resume_id:
            flash("Resume ID is required", "error")
            return redirect(url_for('resumes'))
        
        # Get the resume
        resume = session.query(Resume).filter_by(id=int(resume_id)).first()
        
        if resume:
            # Delete the resume file
            if os.path.exists(resume.file_path):
                os.remove(resume.file_path)
            
            # Delete the resume from the database
            session.delete(resume)
            session.commit()
            
            flash(f"Resume '{resume.name}' deleted successfully")
        else:
            flash("Resume not found", "error")
        
        return redirect(url_for('resumes'))
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting resume: {e}", exc_info=True)
        flash(f"Error deleting resume: {str(e)}", "error")
        return redirect(url_for('resumes'))
    finally:
        session.close()

# Create a simple home page template if the UI templates are not available
@app.route('/simple')
def simple_home():
    """Render a simple home page if the UI templates are not available."""
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Job Scraper App</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/">Job Scraper App</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <a class="nav-link" href="/job_listings">Job Listings</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/resumes">Resumes</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/applications">Applications</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="row">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h1 class="h4 mb-0">Job Scraper App</h1>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4">
                                    <div class="card">
                                        <div class="card-header bg-info text-white">
                                            <h5 class="mb-0"><i class="fas fa-search"></i> Job Scraping</h5>
                                        </div>
                                        <div class="card-body">
                                            <p>Scrape job listings from multiple job boards.</p>
                                            <form action="/scrape" method="post">
                                                <button type="submit" class="btn btn-info">Scrape Jobs</button>
                                            </form>
                                            <a href="/job_listings" class="btn btn-outline-info mt-2">View Job Listings</a>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card">
                                        <div class="card-header bg-success text-white">
                                            <h5 class="mb-0"><i class="fas fa-file-alt"></i> Resume Management</h5>
                                        </div>
                                        <div class="card-body">
                                            <p>Upload and manage your resumes.</p>
                                            <button type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#uploadResumeModal">
                                                Upload Resume
                                            </button>
                                            <a href="/resumes" class="btn btn-outline-success mt-2">Manage Resumes</a>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card">
                                        <div class="card-header bg-warning text-dark">
                                            <h5 class="mb-0"><i class="fas fa-briefcase"></i> Applications</h5>
                                        </div>
                                        <div class="card-body">
                                            <p>Track your job applications.</p>
                                            <a href="/applications" class="btn btn-warning">View Applications</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Upload Resume Modal -->
        <div class="modal fade" id="uploadResumeModal" tabindex="-1" aria-labelledby="uploadResumeModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="uploadResumeModalLabel">Upload Resume</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <form action="/upload_resume" method="post" enctype="multipart/form-data">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label for="resumeFile" class="form-label">Resume File (PDF or DOCX)</label>
                                <input class="form-control" type="file" id="resumeFile" name="resume" accept=".pdf,.docx" required>
                            </div>
                            <div class="mb-3">
                                <label for="resumeName" class="form-label">Resume Name</label>
                                <input type="text" class="form-control" id="resumeName" name="name" placeholder="e.g., Software Developer Resume">
                                <div class="form-text">If left blank, the filename will be used.</div>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="makePrimary" name="make_primary">
                                <label class="form-check-label" for="makePrimary">
                                    Make this my primary resume
                                </label>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-primary">Upload</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """)

if __name__ == '__main__':
    print("Starting Flask application on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)
