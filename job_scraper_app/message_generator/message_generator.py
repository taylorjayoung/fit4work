"""
Message Generator for the Job Scraper Application.

This module provides functionality for generating customized outreach messages
for job applications based on job listings and user resumes.
"""

import logging
import re
import random
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageGenerator:
    """
    Generator for creating customized outreach messages.
    
    This class provides methods for generating cold outreach and follow-up
    messages based on job listings and user resumes.
    """
    
    def __init__(self, config):
        """
        Initialize the message generator.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.templates = config.get("message_templates", {})
    
    def generate_cold_email(self, job_listing, resume_data, user_name=None):
        """
        Generate a cold outreach email for a job application.
        
        Args:
            job_listing: Dictionary containing job listing information
            resume_data: Dictionary containing resume information
            user_name: Name of the user (if None, use the name from the resume)
            
        Returns:
            Dictionary containing the generated email subject and content
        """
        try:
            # Get the template
            template = self.templates.get("cold_email", "")
            if not template:
                logger.error("Cold email template not found in configuration")
                return None
            
            # Extract information from job listing and resume
            job_title = job_listing.get("title", "the position")
            company_name = job_listing.get("company_name", "your company")
            hiring_manager = self._extract_hiring_manager(job_listing) or "Hiring Manager"
            
            # Get user name from resume if not provided
            if not user_name:
                user_name = resume_data.get("name", "")
            
            # Extract relevant skills from resume
            skills = resume_data.get("skills", [])
            relevant_skills_text = ", ".join(skills[:3]) if skills else ""
            
            # Generate a custom paragraph
            custom_paragraph = self._generate_custom_paragraph(job_listing, resume_data)
            
            # Fill in the template
            content = template.format(
                hiring_manager=hiring_manager,
                job_title=job_title,
                company_name=company_name,
                relevant_skills=relevant_skills_text,
                custom_paragraph=custom_paragraph,
                user_name=user_name
            )
            
            # Generate a subject line
            subject = f"Application for {job_title} position at {company_name}"
            
            return {
                "subject": subject,
                "content": content
            }
            
        except Exception as e:
            logger.error(f"Error generating cold email: {e}", exc_info=True)
            return None
    
    def generate_follow_up(self, job_listing, resume_data, days_since_application, user_name=None):
        """
        Generate a follow-up email for a job application.
        
        Args:
            job_listing: Dictionary containing job listing information
            resume_data: Dictionary containing resume information
            days_since_application: Number of days since the initial application
            user_name: Name of the user (if None, use the name from the resume)
            
        Returns:
            Dictionary containing the generated email subject and content
        """
        try:
            # Get the template
            template = self.templates.get("follow_up", "")
            if not template:
                logger.error("Follow-up email template not found in configuration")
                return None
            
            # Extract information from job listing and resume
            job_title = job_listing.get("title", "the position")
            company_name = job_listing.get("company_name", "your company")
            hiring_manager = self._extract_hiring_manager(job_listing) or "Hiring Manager"
            
            # Get user name from resume if not provided
            if not user_name:
                user_name = resume_data.get("name", "")
            
            # Fill in the template
            content = template.format(
                hiring_manager=hiring_manager,
                job_title=job_title,
                company_name=company_name,
                user_name=user_name
            )
            
            # Generate a subject line
            subject = f"Following up on {job_title} application at {company_name}"
            
            return {
                "subject": subject,
                "content": content
            }
            
        except Exception as e:
            logger.error(f"Error generating follow-up email: {e}", exc_info=True)
            return None
    
    def _extract_hiring_manager(self, job_listing):
        """
        Extract the hiring manager's name from a job listing.
        
        Args:
            job_listing: Dictionary containing job listing information
            
        Returns:
            Extracted hiring manager name or None if not found
        """
        # Extract text from the job description
        description = job_listing.get("description", "")
        if not description:
            return None
        
        # Look for common patterns indicating a hiring manager
        patterns = [
            r'(?:please\s+(?:contact|email|send|submit))(?:\s+to)?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'(?:contact|email|send|submit)(?:\s+to)?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'(?:hiring\s+manager|recruiter|hr\s+manager|point\s+of\s+contact)(?:\s+is)?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            if matches:
                return matches[0]
        
        # If no hiring manager is found, look for contact information
        contact_info = job_listing.get("contact_info", "")
        if contact_info:
            # Look for names in the contact information
            name_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
            matches = re.findall(name_pattern, contact_info)
            if matches:
                return matches[0]
        
        return None
    
    def _generate_custom_paragraph(self, job_listing, resume_data):
        """
        Generate a custom paragraph for the cold email.
        
        Args:
            job_listing: Dictionary containing job listing information
            resume_data: Dictionary containing resume information
            
        Returns:
            Generated custom paragraph
        """
        # Extract job requirements and experience from the job listing
        description = job_listing.get("description", "")
        job_title = job_listing.get("title", "the position")
        company_name = job_listing.get("company_name", "your company")
        
        # Extract experience from the resume
        experience = resume_data.get("experience", [])
        experience_text = " ".join(experience) if experience else ""
        
        # Generate a custom paragraph
        paragraphs = [
            f"I am particularly interested in this {job_title} role at {company_name} because it aligns perfectly with my career goals and expertise. My background in similar roles has prepared me well for the challenges and responsibilities outlined in the job description.",
            
            f"After reviewing the job description, I am confident that my experience and skills make me a strong candidate for the {job_title} position. I have successfully handled similar responsibilities in my previous roles, and I am excited about the opportunity to bring my expertise to {company_name}.",
            
            f"What excites me most about this opportunity at {company_name} is the chance to apply my skills in a new environment while contributing to your team's success. I believe my background and approach would be a great fit for the {job_title} role."
        ]
        
        return random.choice(paragraphs)
