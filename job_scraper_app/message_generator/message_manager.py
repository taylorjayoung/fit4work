"""
Message Manager for the Job Scraper Application.

This module provides a high-level interface for managing outreach messages,
including generating, storing, and retrieving messages.
"""

import logging
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from ..database import OutreachMessage, JobApplication, JobListing, TailoredResume
from .message_generator import MessageGenerator

logger = logging.getLogger(__name__)

class MessageManager:
    """
    Manager for outreach message operations.
    
    This class provides a high-level interface for managing outreach messages,
    including generating, storing, and retrieving messages.
    """
    
    def __init__(self, config, db_engine):
        """
        Initialize the message manager.
        
        Args:
            config: Application configuration dictionary
            db_engine: SQLAlchemy database engine
        """
        self.config = config
        self.db_engine = db_engine
        self.Session = sessionmaker(bind=db_engine)
        
        # Initialize the message generator
        self.generator = MessageGenerator(config)
    
    def generate_cold_email(self, job_application_id, user_name=None):
        """
        Generate a cold outreach email for a job application.
        
        Args:
            job_application_id: ID of the job application
            user_name: Name of the user (if None, use the name from the resume)
            
        Returns:
            ID of the generated message, or None if generation failed
        """
        session = self.Session()
        try:
            # Get the job application
            job_application = session.query(JobApplication).filter_by(id=job_application_id).first()
            if not job_application:
                logger.error(f"Job application {job_application_id} not found")
                return None
            
            # Get the job listing and resume
            job_listing = job_application.job_listing
            tailored_resume = job_application.resume
            
            if not job_listing:
                logger.error(f"Job listing for application {job_application_id} not found")
                return None
            
            # Get resume data
            resume_data = {}
            if tailored_resume:
                # Use the tailored resume if available
                resume_data = {
                    'name': tailored_resume.name,
                    'content_text': tailored_resume.content_text,
                    'skills': self._extract_skills_from_resume(tailored_resume.content_text),
                    'experience': self._extract_experience_from_resume(tailored_resume.content_text)
                }
            else:
                # Use the base resume if no tailored resume is available
                base_resume = session.query(TailoredResume).filter_by(job_listing_id=job_listing.id).first()
                if base_resume:
                    resume_data = {
                        'name': base_resume.name,
                        'content_text': base_resume.content_text,
                        'skills': self._extract_skills_from_resume(base_resume.content_text),
                        'experience': self._extract_experience_from_resume(base_resume.content_text)
                    }
            
            # Generate the cold email
            job_listing_dict = {
                'title': job_listing.title,
                'company_name': job_listing.company_name,
                'description': job_listing.description,
                'contact_info': job_listing.contact_info
            }
            
            email = self.generator.generate_cold_email(job_listing_dict, resume_data, user_name)
            if not email:
                logger.error(f"Failed to generate cold email for job application {job_application_id}")
                return None
            
            # Create a new outreach message
            message = OutreachMessage(
                message_type='cold_email',
                subject=email['subject'],
                content=email['content'],
                creation_date=datetime.utcnow(),
                job_application_id=job_application_id
            )
            
            session.add(message)
            session.commit()
            
            logger.info(f"Generated cold email for job application {job_application_id}")
            return message.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error generating cold email: {e}", exc_info=True)
            return None
        finally:
            session.close()
    
    def generate_follow_up(self, job_application_id, days_since_application, user_name=None):
        """
        Generate a follow-up email for a job application.
        
        Args:
            job_application_id: ID of the job application
            days_since_application: Number of days since the initial application
            user_name: Name of the user (if None, use the name from the resume)
            
        Returns:
            ID of the generated message, or None if generation failed
        """
        session = self.Session()
        try:
            # Get the job application
            job_application = session.query(JobApplication).filter_by(id=job_application_id).first()
            if not job_application:
                logger.error(f"Job application {job_application_id} not found")
                return None
            
            # Get the job listing and resume
            job_listing = job_application.job_listing
            tailored_resume = job_application.resume
            
            if not job_listing:
                logger.error(f"Job listing for application {job_application_id} not found")
                return None
            
            # Get resume data
            resume_data = {}
            if tailored_resume:
                # Use the tailored resume if available
                resume_data = {
                    'name': tailored_resume.name,
                    'content_text': tailored_resume.content_text
                }
            else:
                # Use the base resume if no tailored resume is available
                base_resume = session.query(TailoredResume).filter_by(job_listing_id=job_listing.id).first()
                if base_resume:
                    resume_data = {
                        'name': base_resume.name,
                        'content_text': base_resume.content_text
                    }
            
            # Generate the follow-up email
            job_listing_dict = {
                'title': job_listing.title,
                'company_name': job_listing.company_name,
                'description': job_listing.description,
                'contact_info': job_listing.contact_info
            }
            
            email = self.generator.generate_follow_up(job_listing_dict, resume_data, days_since_application, user_name)
            if not email:
                logger.error(f"Failed to generate follow-up email for job application {job_application_id}")
                return None
            
            # Create a new outreach message
            message = OutreachMessage(
                message_type='follow_up',
                subject=email['subject'],
                content=email['content'],
                creation_date=datetime.utcnow(),
                job_application_id=job_application_id
            )
            
            session.add(message)
            session.commit()
            
            logger.info(f"Generated follow-up email for job application {job_application_id}")
            return message.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error generating follow-up email: {e}", exc_info=True)
            return None
        finally:
            session.close()
    
    def get_messages(self, job_application_id=None, message_type=None):
        """
        Get outreach messages, optionally filtered by job application or message type.
        
        Args:
            job_application_id: ID of the job application to filter by
            message_type: Type of message to filter by (e.g., 'cold_email', 'follow_up')
            
        Returns:
            List of OutreachMessage objects
        """
        session = self.Session()
        try:
            query = session.query(OutreachMessage)
            
            if job_application_id:
                query = query.filter_by(job_application_id=job_application_id)
            
            if message_type:
                query = query.filter_by(message_type=message_type)
            
            return query.order_by(OutreachMessage.creation_date.desc()).all()
        except Exception as e:
            logger.error(f"Error retrieving outreach messages: {e}", exc_info=True)
            return []
        finally:
            session.close()
    
    def get_message(self, message_id):
        """
        Get an outreach message by ID.
        
        Args:
            message_id: ID of the message to retrieve
            
        Returns:
            OutreachMessage object or None if not found
        """
        session = self.Session()
        try:
            message = session.query(OutreachMessage).filter_by(id=message_id).first()
            return message
        except Exception as e:
            logger.error(f"Error retrieving outreach message {message_id}: {e}", exc_info=True)
            return None
        finally:
            session.close()
    
    def _extract_skills_from_resume(self, content_text):
        """
        Extract skills from resume content text.
        
        Args:
            content_text: Resume content text
            
        Returns:
            List of extracted skills
        """
        # This is a simplified implementation
        # In a real application, you would use NLP techniques to extract skills
        skills_section = self._extract_section(content_text, ['skills', 'technical skills', 'core competencies'])
        if not skills_section:
            return []
        
        # Split by commas, newlines, or bullet points
        skills = []
        for line in skills_section.split('\n'):
            line = line.strip()
            if line:
                # Remove bullet points and other markers
                line = line.lstrip('•-*').strip()
                # Split by commas
                for skill in line.split(','):
                    skill = skill.strip()
                    if skill:
                        skills.append(skill)
        
        return skills
    
    def _extract_experience_from_resume(self, content_text):
        """
        Extract experience from resume content text.
        
        Args:
            content_text: Resume content text
            
        Returns:
            List of extracted experience entries
        """
        # This is a simplified implementation
        # In a real application, you would use NLP techniques to extract experience
        experience_section = self._extract_section(content_text, ['experience', 'work experience', 'employment'])
        if not experience_section:
            return []
        
        # Split into paragraphs
        experience = []
        paragraphs = experience_section.split('\n\n')
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                experience.append(paragraph)
        
        return experience
    
    def _extract_section(self, text, section_keywords):
        """
        Extract a section from text based on section keywords.
        
        Args:
            text: Text to extract section from
            section_keywords: List of keywords that might indicate the section
            
        Returns:
            Extracted section text or None if not found
        """
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Find the start of the section
        section_start = -1
        for keyword in section_keywords:
            # Look for the keyword at the beginning of a line
            pattern = f"\n{keyword}:|\n{keyword}\n"
            index = text_lower.find(pattern)
            if index != -1:
                section_start = index + len(pattern)
                break
        
        if section_start == -1:
            return None
        
        # Find the end of the section (start of the next section)
        common_sections = [
            'education', 'experience', 'work experience', 'employment', 'skills',
            'technical skills', 'projects', 'publications', 'certifications',
            'awards', 'honors', 'languages', 'interests', 'references'
        ]
        
        # Remove the current section from the list of common sections
        for keyword in section_keywords:
            if keyword in common_sections:
                common_sections.remove(keyword)
        
        section_end = len(text)
        for section in common_sections:
            pattern = f"\n{section}:|\n{section}\n"
            index = text_lower.find(pattern, section_start)
            if index != -1:
                section_end = index
                break
        
        # Extract the section text
        section_text = text[section_start:section_end].strip()
        
        return section_text
