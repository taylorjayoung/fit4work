"""
Flask application for the Job Scraper Application.

This module provides a web interface for the application, allowing users to
interact with job listings, resumes, and outreach messages.
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy.orm import sessionmaker

from ..database import JobListing, Resume, TailoredResume, JobApplication, OutreachMessage
from ..scrapers import ScraperManager
from ..resume_processor import ResumeManager
from ..message_generator import MessageManager

logger = logging.getLogger(__name__)

def create_app(config, db_engine, scraper_manager=None):
    """
    Create and configure the Flask application.
    
    Args:
        config: Application configuration dictionary
        db_engine: SQLAlchemy database engine
        scraper_manager: ScraperManager instance (if None, create a new one)
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    
    # Configure the application
    app.config['UPLOAD_FOLDER'] = Path(config["resume_settings"]["storage_path"])
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
    
    # Create the upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize managers
    Session = sessionmaker(bind=db_engine)
    if scraper_manager is None:
        scraper_manager = ScraperManager(config, db_engine)
    resume_manager = ResumeManager(config, db_engine)
    message_manager = MessageManager(config, db_engine)
    
    # Register routes
    
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
            # Get filter parameters
            title = request.args.get('title', '')
            company = request.args.get('company', '')
            job_type = request.args.get('job_type', '')
            location = request.args.get('location', '')
            source_site = request.args.get('source_site', '')
            
            # Build filters
            filters = {}
            if title:
                filters['title'] = title
            if company:
                filters['company'] = company
            if job_type:
                filters['job_type'] = job_type
            if location:
                filters['location'] = location
            if source_site:
                filters['source_site'] = source_site
            
            # Get job listings
            job_listings = scraper_manager.get_job_listings(filters=filters)
            
            # Get unique values for filter dropdowns
            source_sites = session.query(JobListing.source_site).distinct().all()
            job_types = session.query(JobListing.job_type).distinct().all()
            
            return render_template('job_listings.html', 
                                  job_listings=job_listings,
                                  source_sites=source_sites,
                                  job_types=job_types,
                                  filters=filters)
        finally:
            session.close()
    
    @app.route('/job_listing/<int:job_id>')
    def job_listing(job_id):
        """Render the job listing detail page."""
        session = Session()
        try:
            # Get the job listing
            job_listing = session.query(JobListing).filter_by(id=job_id).first_or_404()
            
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
            resume = session.query(Resume).filter_by(id=resume_id).first_or_404()
            
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
            job_application = session.query(JobApplication).filter_by(id=application_id).first_or_404()
            
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
    
    # Return the configured application
    return app
