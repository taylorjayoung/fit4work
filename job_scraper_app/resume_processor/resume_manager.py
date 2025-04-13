"""
Resume Manager for the Job Scraper Application.

This module provides a high-level interface for managing resumes,
including parsing, storing, and generating tailored resumes.
"""

import os
import logging
import shutil
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from ..database import Resume, TailoredResume, JobListing
from .resume_parser import ResumeParser
from .resume_generator import ResumeGenerator

logger = logging.getLogger(__name__)

class ResumeManager:
    """
    Manager for resume operations.
    
    This class provides a high-level interface for managing resumes,
    including uploading, parsing, storing, and generating tailored resumes.
    """
    
    def __init__(self, config, db_engine):
        """Initialize the resume manager."""
        self.config = config
        self.db_engine = db_engine
        self.Session = sessionmaker(bind=db_engine)
        
        # Initialize the resume storage directory
        self.storage_dir = Path(config["resume_settings"]["storage_path"])
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(self.storage_dir / "tailored", exist_ok=True)
        
        # Initialize the resume parser and generator
        self.parser = ResumeParser()
        self.generator = ResumeGenerator(self.storage_dir / "tailored")
    
    def upload_resume(self, file_path, name=None, make_primary=False):
        """Upload and process a resume file."""
        try:
            file_path = Path(file_path)
            
            # Check if the file exists and format is supported
            if not file_path.exists():
                logger.error(f"Resume file not found: {file_path}")
                return None
            
            if file_path.suffix.lower() not in ['.docx', '.pdf']:
                logger.error(f"Unsupported file format: {file_path.suffix}")
                return None
            
            # Parse the resume
            resume_data = self.parser.parse(file_path)
            if not resume_data:
                logger.error(f"Failed to parse resume: {file_path}")
                return None
            
            # Generate a name if not provided
            if not name:
                name = file_path.stem
            
            # Copy the file to the storage directory
            storage_path = self.storage_dir / f"{name}{file_path.suffix}"
            shutil.copy2(file_path, storage_path)
            
            # Store the resume in the database
            session = self.Session()
            try:
                # If make_primary is True, reset primary flag on all resumes
                if make_primary:
                    session.query(Resume).update({Resume.is_primary: False})
                
                # Create a new resume record
                resume = Resume(
                    name=name,
                    file_path=str(storage_path),
                    content_text=resume_data['content_text'],
                    upload_date=datetime.utcnow(),
                    is_primary=make_primary
                )
                
                session.add(resume)
                session.commit()
                
                logger.info(f"Successfully uploaded resume: {name}")
                return resume.id
            except Exception as e:
                session.rollback()
                logger.error(f"Error storing resume in database: {e}", exc_info=True)
                return None
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error uploading resume: {e}", exc_info=True)
            return None
    
    def generate_tailored_resume(self, resume_id, job_listing_id):
        """Generate a tailored resume for a job listing."""
        session = self.Session()
        try:
            # Get the resume and job listing
            resume = session.query(Resume).filter_by(id=resume_id).first()
            job_listing = session.query(JobListing).filter_by(id=job_listing_id).first()
            
            if not resume or not job_listing:
                logger.error(f"Resume {resume_id} or job listing {job_listing_id} not found")
                return None
            
            # Parse the resume if not already parsed
            resume_data = self.parser.parse(resume.file_path)
            if not resume_data:
                logger.error(f"Failed to parse resume: {resume.file_path}")
                return None
            
            # Generate a tailored resume
            output_filename = f"Tailored_Resume_{resume.name}_{job_listing.company_name}_{job_listing.title}.docx"
            output_path = self.generator.generate_tailored_resume(
                resume_data, 
                {
                    'title': job_listing.title,
                    'company_name': job_listing.company_name,
                    'description': job_listing.description
                },
                output_filename
            )
            
            if not output_path:
                logger.error(f"Failed to generate tailored resume")
                return None
            
            # Create a tailored resume record
            tailored_resume = TailoredResume(
                name=f"{resume.name} for {job_listing.company_name} - {job_listing.title}",
                file_path=output_path,
                content_text=resume_data['content_text'],
                creation_date=datetime.utcnow(),
                base_resume_id=resume_id,
                job_listing_id=job_listing_id
            )
            
            session.add(tailored_resume)
            session.commit()
            
            logger.info(f"Generated tailored resume: {tailored_resume.name}")
            return tailored_resume.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error generating tailored resume: {e}", exc_info=True)
            return None
        finally:
            session.close()
    
    def get_tailored_resumes(self, resume_id=None, job_listing_id=None):
        """Get tailored resumes, optionally filtered by resume or job listing."""
        session = self.Session()
        try:
            query = session.query(TailoredResume)
            
            if resume_id:
                query = query.filter_by(base_resume_id=resume_id)
            
            if job_listing_id:
                query = query.filter_by(job_listing_id=job_listing_id)
            
            return query.order_by(TailoredResume.creation_date.desc()).all()
        except Exception as e:
            logger.error(f"Error retrieving tailored resumes: {e}", exc_info=True)
            return []
        finally:
            session.close()
