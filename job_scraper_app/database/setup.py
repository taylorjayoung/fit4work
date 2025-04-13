"""
Database setup and models for the Job Scraper Application.

This module defines the database schema and provides functions to initialize
and set up the database.
"""

import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

logger = logging.getLogger(__name__)

# Create the declarative base
Base = declarative_base()

class JobListing(Base):
    """Model representing a job listing scraped from a job site."""
    __tablename__ = 'job_listings'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    job_type = Column(String(100))
    location = Column(String(255))
    description = Column(Text)
    url = Column(String(512), nullable=False, unique=True)
    contact_info = Column(Text)
    company_website = Column(String(512))
    salary_info = Column(String(255))
    posted_date = Column(DateTime)
    scraped_date = Column(DateTime, default=datetime.utcnow)
    source_site = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    applications = relationship("JobApplication", back_populates="job_listing", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<JobListing(id={self.id}, title='{self.title}', company='{self.company_name}')>"

class Resume(Base):
    """Model representing a user's resume."""
    __tablename__ = 'resumes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    content_text = Column(Text)
    upload_date = Column(DateTime, default=datetime.utcnow)
    is_primary = Column(Boolean, default=False)
    
    # Relationships
    tailored_resumes = relationship("TailoredResume", back_populates="base_resume", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Resume(id={self.id}, name='{self.name}')>"

class TailoredResume(Base):
    """Model representing a resume tailored for a specific job."""
    __tablename__ = 'tailored_resumes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    content_text = Column(Text)
    creation_date = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    base_resume_id = Column(Integer, ForeignKey('resumes.id'), nullable=False)
    job_listing_id = Column(Integer, ForeignKey('job_listings.id'), nullable=False)
    
    # Relationships
    base_resume = relationship("Resume", back_populates="tailored_resumes")
    job_listing = relationship("JobListing")
    
    def __repr__(self):
        return f"<TailoredResume(id={self.id}, name='{self.name}')>"

class OutreachMessage(Base):
    """Model representing an outreach message for a job application."""
    __tablename__ = 'outreach_messages'
    
    id = Column(Integer, primary_key=True)
    message_type = Column(String(50), nullable=False)  # e.g., 'cold_email', 'follow_up'
    subject = Column(String(255))
    content = Column(Text, nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    job_application_id = Column(Integer, ForeignKey('job_applications.id'), nullable=False)
    
    # Relationships
    job_application = relationship("JobApplication", back_populates="outreach_messages")
    
    def __repr__(self):
        return f"<OutreachMessage(id={self.id}, type='{self.message_type}')>"

class JobApplication(Base):
    """Model representing a job application."""
    __tablename__ = 'job_applications'
    
    id = Column(Integer, primary_key=True)
    status = Column(String(50), default='pending')  # e.g., 'pending', 'applied', 'interviewed', 'rejected', 'offered'
    application_date = Column(DateTime)
    notes = Column(Text)
    
    # Foreign keys
    job_listing_id = Column(Integer, ForeignKey('job_listings.id'), nullable=False)
    resume_id = Column(Integer, ForeignKey('tailored_resumes.id'))
    
    # Relationships
    job_listing = relationship("JobListing", back_populates="applications")
    resume = relationship("TailoredResume")
    outreach_messages = relationship("OutreachMessage", back_populates="job_application", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<JobApplication(id={self.id}, status='{self.status}')>"

class KeywordMatch(Base):
    """Model for tracking keyword matches between resumes and job listings."""
    __tablename__ = 'keyword_matches'
    
    id = Column(Integer, primary_key=True)
    keyword = Column(String(100), nullable=False)
    context = Column(Text)
    match_score = Column(Float)
    
    # Foreign keys
    job_listing_id = Column(Integer, ForeignKey('job_listings.id'), nullable=False)
    resume_id = Column(Integer, ForeignKey('resumes.id'), nullable=False)
    
    # Relationships
    job_listing = relationship("JobListing")
    resume = relationship("Resume")
    
    def __repr__(self):
        return f"<KeywordMatch(id={self.id}, keyword='{self.keyword}', score={self.match_score})>"

def setup_database(db_path, rebuild=False):
    """
    Set up the database and create all tables.
    
    Args:
        db_path: Path to the SQLite database file
        rebuild: If True, drop all existing tables and recreate them
        
    Returns:
        SQLAlchemy engine instance
    """
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Create the database engine
    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url)
    
    # Drop all tables if rebuild is True
    if rebuild and os.path.exists(db_path):
        logger.info("Rebuilding database: dropping all tables")
        Base.metadata.drop_all(engine)
    
    # Create all tables
    logger.info("Creating database tables")
    Base.metadata.create_all(engine)
    
    # Create a session factory
    Session = sessionmaker(bind=engine)
    
    logger.info("Database setup completed successfully")
    return engine

def get_session(engine):
    """
    Create and return a new database session.
    
    Args:
        engine: SQLAlchemy engine instance
        
    Returns:
        SQLAlchemy session
    """
    Session = sessionmaker(bind=engine)
    return Session()
