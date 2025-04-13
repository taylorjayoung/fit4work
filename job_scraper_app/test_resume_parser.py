#!/usr/bin/env python3
"""
Test script for the resume parser with the new configuration.

This script tests the resume parser with the new configuration and prompt.
It will parse a resume file and print the extracted information.

Usage:
    python test_resume_parser.py [path_to_resume_file]
"""

import os
import sys
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Import the config_loader and resume_parser modules
from config_loader import load_config
from resume_processor.resume_parser import ResumeParser

def print_separator(title):
    """Print a separator with a title."""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50, "="))
    print("=" * 50 + "\n")

def test_resume_parser(resume_path=None):
    """
    Test the resume parser with the new configuration.
    
    Args:
        resume_path: Path to the resume file to parse
    """
    print_separator("Testing Resume Parser")
    
    # Load the configuration
    config = load_config()
    
    # Check if the Anthropic API key is set
    if 'ai_services' in config and 'anthropic' in config['ai_services']:
        api_key = config['ai_services']['anthropic'].get('api_key', '')
        if api_key and api_key != 'YOUR_ANTHROPIC_API_KEY':
            print(f"Anthropic API key is configured: {api_key[:5]}...{api_key[-4:] if len(api_key) > 10 else ''}")
        else:
            print("Anthropic API key is not set or is using the placeholder value.")
            print("Please set your API key using one of the methods described in API_KEY_SETUP.md")
            return
    else:
        print("Anthropic API configuration not found in config.")
        return
    
    # Initialize the resume parser
    parser = ResumeParser(config)
    
    # Check if the Anthropic client is initialized
    if not parser.anthropic_client:
        print("Anthropic client is not initialized. Please check your API key.")
        return
    
    # If no resume path is provided, look for resumes in the default location
    if not resume_path:
        resume_dir = project_dir / config.get('resume_settings', {}).get('storage_path', 'user_data/resumes/')
        resume_files = list(resume_dir.glob('*.pdf')) + list(resume_dir.glob('*.docx')) + list(resume_dir.glob('*.txt'))
        
        if not resume_files:
            print(f"No resume files found in {resume_dir}")
            print("Please provide a path to a resume file or add resume files to the default location.")
            return
        
        resume_path = resume_files[0]
        print(f"Using resume file: {resume_path}")
    else:
        resume_path = Path(resume_path)
        if not resume_path.exists():
            print(f"Resume file not found: {resume_path}")
            return
    
    # Parse the resume
    print(f"Parsing resume: {resume_path}")
    resume_data = parser.parse(resume_path)
    
    if resume_data:
        print("\nParsed resume data:")
        
        # Print personal information
        print("\nPersonal Information:")
        print(f"Name: {resume_data.get('name')}")
        print(f"Email: {', '.join(resume_data.get('email', []))}")
        print(f"Phone: {', '.join(resume_data.get('phone', []))}")
        if 'location' in resume_data:
            print(f"Location: {resume_data.get('location')}")
        
        # Print links
        if resume_data.get('links'):
            print("\nLinks:")
            for link_type, link in resume_data.get('links', {}).items():
                if isinstance(link, list):
                    print(f"{link_type.capitalize()}: {', '.join(link)}")
                else:
                    print(f"{link_type.capitalize()}: {link}")
        
        # Print education
        if resume_data.get('education'):
            print("\nEducation:")
            for edu in resume_data.get('education', []):
                print(f"- {edu}")
        
        # Print experience
        if resume_data.get('experience'):
            print("\nExperience:")
            for exp in resume_data.get('experience', []):
                print(f"- {exp.split(chr(10))[0]}")  # Print only the first line
                if len(exp.split(chr(10))) > 1:
                    print(f"  ({len(exp.split(chr(10)) ) - 1} more lines...)")
        
        # Print skills
        if resume_data.get('skills'):
            print("\nSkills:")
            skills = resume_data.get('skills', [])
            if len(skills) > 10:
                print(f"- {', '.join(skills[:10])} (and {len(skills) - 10} more...)")
            else:
                print(f"- {', '.join(skills)}")
        
        print("\nResume parsing successful!")
    else:
        print("Failed to parse resume.")

if __name__ == "__main__":
    # Get the resume path from the command line arguments
    resume_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Test the resume parser
    test_resume_parser(resume_path)
