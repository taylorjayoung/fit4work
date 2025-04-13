"""
Message Generator package for the Job Scraper Application.

This package contains modules for generating customized outreach messages
for job applications.
"""

from .message_generator import MessageGenerator
from .message_manager import MessageManager

__all__ = [
    'MessageGenerator',
    'MessageManager'
]
