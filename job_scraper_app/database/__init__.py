"""
Database package for the Job Scraper Application.

This package contains modules for database setup, models, and operations.
"""

from .setup import setup_database, get_session, Base
from .setup import JobListing, Resume, TailoredResume, OutreachMessage, JobApplication, KeywordMatch

__all__ = [
    'setup_database',
    'get_session',
    'Base',
    'JobListing',
    'Resume',
    'TailoredResume',
    'OutreachMessage',
    'JobApplication',
    'KeywordMatch'
]
