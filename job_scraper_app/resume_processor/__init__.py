"""
Resume Processor package for the Job Scraper Application.

This package contains modules for parsing, analyzing, and generating resumes.
"""

from .resume_parser import ResumeParser
from .resume_generator import ResumeGenerator
from .resume_manager import ResumeManager

__all__ = [
    'ResumeParser',
    'ResumeGenerator',
    'ResumeManager'
]
