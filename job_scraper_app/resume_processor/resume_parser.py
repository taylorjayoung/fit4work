"""
Resume Parser for the Job Scraper Application.

This module provides functionality for parsing and extracting information
from user resumes in various formats (DOCX, PDF).
"""

import os
import re
import logging
from pathlib import Path
import docx
from pdfminer.high_level import extract_text
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

logger = logging.getLogger(__name__)

# Ensure NLTK resources are downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ResumeParser:
    """
    Parser for extracting information from resumes.
    
    This class provides methods for parsing resumes in different formats
    and extracting structured information from them.
    """
    
    def __init__(self):
        """Initialize the resume parser."""
        self.stop_words = set(stopwords.words('english'))
    
    def parse(self, file_path):
        """
        Parse a resume file and extract structured information.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Dictionary containing extracted resume information
        """
        try:
            file_path = Path(file_path)
            
            # Check if the file exists
            if not file_path.exists():
                logger.error(f"Resume file not found: {file_path}")
                return None
            
            # Extract text based on file format
            if file_path.suffix.lower() == '.docx':
                text = self._extract_text_from_docx(file_path)
            elif file_path.suffix.lower() == '.pdf':
                text = self._extract_text_from_pdf(file_path)
            else:
                logger.error(f"Unsupported file format: {file_path.suffix}")
                return None
            
            if not text:
                logger.error(f"Failed to extract text from resume: {file_path}")
                return None
            
            # Extract structured information from the text
            resume_data = self._extract_information(text)
            resume_data['file_path'] = str(file_path)
            resume_data['content_text'] = text
            
            logger.info(f"Successfully parsed resume: {file_path}")
            return resume_data
            
        except Exception as e:
            logger.error(f"Error parsing resume {file_path}: {e}", exc_info=True)
            return None
    
    def _extract_text_from_docx(self, file_path):
        """
        Extract text from a DOCX file.
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Extracted text as a string
        """
        try:
            doc = docx.Document(file_path)
            full_text = []
            
            # Extract text from paragraphs
            for para in doc.paragraphs:
                full_text.append(para.text)
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        full_text.append(cell.text)
            
            return '\n'.join(full_text)
        except Exception as e:
            logger.error(f"Error extracting text from DOCX file {file_path}: {e}", exc_info=True)
            return None
    
    def _extract_text_from_pdf(self, file_path):
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
        """
        try:
            return extract_text(file_path)
        except Exception as e:
            logger.error(f"Error extracting text from PDF file {file_path}: {e}", exc_info=True)
            return None
    
    def _extract_information(self, text):
        """
        Extract structured information from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary containing extracted information
        """
        resume_data = {
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'education': self._extract_education(text),
            'experience': self._extract_experience(text),
            'skills': self._extract_skills(text),
            'links': self._extract_links(text)
        }
        
        return resume_data
    
    def _extract_name(self, text):
        """
        Extract the candidate's name from the resume text.
        
        Args:
            text: Resume text
            
        Returns:
            Extracted name or None if not found
        """
        # Typically, the name is at the beginning of the resume
        lines = text.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        if non_empty_lines:
            # Assume the first non-empty line is the name
            # This is a simple heuristic and may need to be improved
            return non_empty_lines[0]
        
        return None
    
    def _extract_email(self, text):
        """
        Extract email addresses from the resume text.
        
        Args:
            text: Resume text
            
        Returns:
            List of extracted email addresses
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    def _extract_phone(self, text):
        """
        Extract phone numbers from the resume text.
        
        Args:
            text: Resume text
            
        Returns:
            List of extracted phone numbers
        """
        phone_pattern = r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        return re.findall(phone_pattern, text)
    
    def _extract_education(self, text):
        """
        Extract education information from the resume text.
        
        Args:
            text: Resume text
            
        Returns:
            List of extracted education entries
        """
        education = []
        
        # Look for education section
        education_section = self._extract_section(text, ['education', 'academic background', 'academic history'])
        
        if education_section:
            # Look for degree keywords
            degree_keywords = [
                'bachelor', 'master', 'phd', 'doctorate', 'bs', 'ba', 'ms', 'ma', 'mba',
                'associate', 'certificate', 'certification', 'diploma'
            ]
            
            # Split into lines and look for lines containing degree keywords
            lines = education_section.split('\n')
            for i, line in enumerate(lines):
                if any(keyword in line.lower() for keyword in degree_keywords):
                    # Include this line and possibly the next few lines as one education entry
                    entry = line
                    for j in range(1, 3):  # Look at the next 2 lines
                        if i + j < len(lines) and lines[i + j].strip():
                            entry += ' ' + lines[i + j]
                    
                    education.append(entry.strip())
        
        return education
    
    def _extract_experience(self, text):
        """
        Extract work experience information from the resume text.
        
        Args:
            text: Resume text
            
        Returns:
            List of extracted experience entries
        """
        experience = []
        
        # Look for experience section
        experience_section = self._extract_section(text, ['experience', 'work experience', 'employment', 'work history'])
        
        if experience_section:
            # Split into paragraphs (assuming each job is a paragraph)
            paragraphs = re.split(r'\n\s*\n', experience_section)
            
            for paragraph in paragraphs:
                if paragraph.strip():
                    experience.append(paragraph.strip())
        
        return experience
    
    def _extract_skills(self, text):
        """
        Extract skills from the resume text.
        
        Args:
            text: Resume text
            
        Returns:
            List of extracted skills
        """
        skills = []
        
        # Look for skills section
        skills_section = self._extract_section(text, ['skills', 'technical skills', 'core competencies', 'proficiencies'])
        
        if skills_section:
            # Tokenize and filter out stop words
            tokens = word_tokenize(skills_section.lower())
            filtered_tokens = [token for token in tokens if token.isalpha() and token not in self.stop_words]
            
            # Look for common skill keywords
            skill_keywords = [
                'python', 'java', 'javascript', 'html', 'css', 'sql', 'nosql', 'react', 'angular', 'vue',
                'node', 'express', 'django', 'flask', 'spring', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
                'git', 'agile', 'scrum', 'jira', 'confluence', 'excel', 'word', 'powerpoint', 'photoshop',
                'illustrator', 'indesign', 'figma', 'sketch', 'leadership', 'management', 'communication',
                'teamwork', 'problem-solving', 'analytical', 'critical thinking', 'time management',
                'project management', 'research', 'writing', 'editing', 'public speaking', 'customer service',
                'sales', 'marketing', 'finance', 'accounting', 'hr', 'recruiting', 'training', 'coaching',
                'mentoring', 'data analysis', 'data visualization', 'machine learning', 'ai', 'nlp',
                'computer vision', 'statistics', 'calculus', 'linear algebra', 'probability'
            ]
            
            # Extract skills from the skills section
            for keyword in skill_keywords:
                if keyword in ' '.join(filtered_tokens):
                    skills.append(keyword)
            
            # Also look for skills in bullet points
            bullet_points = re.findall(r'[•\-\*]\s*(.*?)(?:\n|$)', skills_section)
            for point in bullet_points:
                if point.strip():
                    skills.append(point.strip())
        
        return skills
    
    def _extract_links(self, text):
        """
        Extract links (e.g., LinkedIn, GitHub, portfolio) from the resume text.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary mapping link types to URLs
        """
        links = {}
        
        # Extract URLs
        url_pattern = r'https?://(?:www\.)?([A-Za-z0-9][-A-Za-z0-9]*\.)+[A-Za-z]{2,}(?:/[^\\s]*)?'
        urls = re.findall(url_pattern, text)
        
        # Categorize URLs
        for url in urls:
            if 'linkedin.com' in url.lower():
                links['linkedin'] = url
            elif 'github.com' in url.lower():
                links['github'] = url
            elif 'stackoverflow.com' in url.lower():
                links['stackoverflow'] = url
            elif any(domain in url.lower() for domain in ['portfolio', 'personal', 'website']):
                links['portfolio'] = url
            else:
                links.setdefault('other', []).append(url)
        
        return links
    
    def _extract_section(self, text, section_keywords):
        """
        Extract a section from the resume text based on section keywords.
        
        Args:
            text: Resume text
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
            pattern = r'(?:^|\n)(?:\s*)({})[:\s]'.format(re.escape(keyword))
            match = re.search(pattern, text_lower)
            if match:
                section_start = match.start()
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
            pattern = r'(?:^|\n)(?:\s*)({})[:\s]'.format(re.escape(section))
            match = re.search(pattern, text_lower[section_start + 1:])
            if match:
                section_end = section_start + 1 + match.start()
                break
        
        # Extract the section text
        section_text = text[section_start:section_end].strip()
        
        # Remove the section header
        lines = section_text.split('\n')
        if lines:
            section_text = '\n'.join(lines[1:])
        
        return section_text.strip()
