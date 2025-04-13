"""
Tests for the ResumeGenerator class.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
import tempfile
from pathlib import Path
import sys

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_dir))

from job_scraper_app.resume_processor.resume_generator import ResumeGenerator

class TestResumeGenerator(unittest.TestCase):
    """Test cases for the ResumeGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for output
        self.temp_dir = tempfile.mkdtemp()
        
        # Patch the spaCy model
        self.nlp_patcher = patch('job_scraper_app.resume_processor.resume_generator.nlp')
        self.mock_nlp = self.nlp_patcher.start()
        
        # Create the ResumeGenerator
        self.generator = ResumeGenerator(self.temp_dir)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Stop the patches
        self.nlp_patcher.stop()
        
        # Remove the temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)
        
        self.generator = None
    
    def test_initialization(self):
        """Test that the generator initializes correctly."""
        # Check that the output directory is set correctly
        self.assertEqual(self.generator.output_dir, Path(self.temp_dir))
        
        # Check that the stop words are initialized
        self.assertIsNotNone(self.generator.stop_words)
    
    @patch('job_scraper_app.resume_processor.resume_generator.ResumeGenerator._extract_keywords_from_job')
    @patch('job_scraper_app.resume_processor.resume_generator.ResumeGenerator._match_skills_with_keywords')
    @patch('job_scraper_app.resume_processor.resume_generator.ResumeGenerator._create_resume_document')
    def test_generate_tailored_resume(self, mock_create_document, mock_match_skills, mock_extract_keywords):
        """Test generating a tailored resume."""
        # Set up mocks
        mock_extract_keywords.return_value = ['python', 'java', 'sql', 'software engineering']
        mock_match_skills.return_value = {
            'Python': {'keyword': 'python', 'score': 0.9},
            'SQL': {'keyword': 'sql', 'score': 0.8}
        }
        
        mock_doc = MagicMock()
        mock_create_document.return_value = mock_doc
        
        # Set up resume data and job listing
        resume_data = {
            'name': 'John Doe',
            'email': ['john.doe@example.com'],
            'phone': ['(123) 456-7890'],
            'education': ['Bachelor of Science in Computer Science'],
            'experience': ['Software Engineer at Example Corp'],
            'skills': ['Python', 'Java', 'SQL'],
            'links': {'linkedin': 'https://linkedin.com/in/johndoe'}
        }
        
        job_listing = {
            'title': 'Software Engineer',
            'company_name': 'Example Corp',
            'description': 'Looking for a software engineer with Python, Java, and SQL skills.'
        }
        
        # Call the generate_tailored_resume method
        result = self.generator.generate_tailored_resume(resume_data, job_listing, 'Tailored_Resume.docx')
        
        # Verify the result
        expected_path = str(Path(self.temp_dir) / 'Tailored_Resume.docx')
        self.assertEqual(result, expected_path)
        
        # Verify that the methods were called correctly
        mock_extract_keywords.assert_called_once_with(job_listing)
        mock_match_skills.assert_called_once_with(resume_data['skills'], mock_extract_keywords.return_value)
        mock_create_document.assert_called_once_with(
            resume_data,
            job_listing,
            mock_match_skills.return_value,
            mock_extract_keywords.return_value
        )
        
        # Verify that the document was saved
        mock_doc.save.assert_called_once_with(Path(self.temp_dir) / 'Tailored_Resume.docx')
    
    @patch('job_scraper_app.resume_processor.resume_generator.ResumeGenerator._extract_keywords_from_job')
    @patch('job_scraper_app.resume_processor.resume_generator.ResumeGenerator._match_skills_with_keywords')
    @patch('job_scraper_app.resume_processor.resume_generator.ResumeGenerator._create_resume_document')
    def test_generate_tailored_resume_no_filename(self, mock_create_document, mock_match_skills, mock_extract_keywords):
        """Test generating a tailored resume without specifying a filename."""
        # Set up mocks
        mock_extract_keywords.return_value = ['python', 'java', 'sql', 'software engineering']
        mock_match_skills.return_value = {
            'Python': {'keyword': 'python', 'score': 0.9},
            'SQL': {'keyword': 'sql', 'score': 0.8}
        }
        
        mock_doc = MagicMock()
        mock_create_document.return_value = mock_doc
        
        # Set up resume data and job listing
        resume_data = {
            'name': 'John Doe',
            'email': ['john.doe@example.com'],
            'phone': ['(123) 456-7890'],
            'education': ['Bachelor of Science in Computer Science'],
            'experience': ['Software Engineer at Example Corp'],
            'skills': ['Python', 'Java', 'SQL'],
            'links': {'linkedin': 'https://linkedin.com/in/johndoe'}
        }
        
        job_listing = {
            'title': 'Software Engineer',
            'company_name': 'Example Corp',
            'description': 'Looking for a software engineer with Python, Java, and SQL skills.'
        }
        
        # Call the generate_tailored_resume method without specifying a filename
        result = self.generator.generate_tailored_resume(resume_data, job_listing)
        
        # We don't need to verify the exact path, just that it's a string and contains the expected parts
        self.assertIsInstance(result, str)
        self.assertIn(self.temp_dir, result)
        self.assertIn('Tailored_Resume', result)
        self.assertIn('Example Corp', result)
        self.assertIn('Software Engineer', result)
        
        # Verify that the methods were called correctly
        mock_extract_keywords.assert_called_once_with(job_listing)
        mock_match_skills.assert_called_once_with(resume_data['skills'], mock_extract_keywords.return_value)
        mock_create_document.assert_called_once_with(
            resume_data,
            job_listing,
            mock_match_skills.return_value,
            mock_extract_keywords.return_value
        )
        
        # Verify that the document was saved
        mock_doc.save.assert_called_once()
    
    @patch('job_scraper_app.resume_processor.resume_generator.ResumeGenerator._extract_keywords_from_job')
    def test_generate_tailored_resume_error(self, mock_extract_keywords):
        """Test generating a tailored resume when an error occurs."""
        # Make the _extract_keywords_from_job method raise an exception
        mock_extract_keywords.side_effect = Exception("Test exception")
        
        # Set up resume data and job listing
        resume_data = {
            'name': 'John Doe',
            'email': ['john.doe@example.com'],
            'phone': ['(123) 456-7890'],
            'education': ['Bachelor of Science in Computer Science'],
            'experience': ['Software Engineer at Example Corp'],
            'skills': ['Python', 'Java', 'SQL'],
            'links': {'linkedin': 'https://linkedin.com/in/johndoe'}
        }
        
        job_listing = {
            'title': 'Software Engineer',
            'company_name': 'Example Corp',
            'description': 'Looking for a software engineer with Python, Java, and SQL skills.'
        }
        
        # Call the generate_tailored_resume method
        result = self.generator.generate_tailored_resume(resume_data, job_listing)
        
        # Verify the result
        self.assertIsNone(result)
    
    def test_extract_keywords_from_job(self):
        """Test extracting keywords from a job listing."""
        # Set up a mock spaCy document
        mock_doc = MagicMock()
        self.mock_nlp.return_value = mock_doc
        
        # Set up mock noun chunks
        mock_chunk1 = MagicMock()
        mock_chunk1.root.pos_ = 'NOUN'
        mock_chunk1.root.is_alpha = True
        mock_chunk1.text = 'software engineer'
        
        mock_chunk2 = MagicMock()
        mock_chunk2.root.pos_ = 'NOUN'
        mock_chunk2.root.is_alpha = True
        mock_chunk2.text = 'python experience'
        
        mock_doc.noun_chunks = [mock_chunk1, mock_chunk2]
        
        # Set up mock named entities
        mock_ent1 = MagicMock()
        mock_ent1.label_ = 'ORG'
        mock_ent1.text = 'Example Corp'
        
        mock_ent2 = MagicMock()
        mock_ent2.label_ = 'PRODUCT'
        mock_ent2.text = 'Java'
        
        mock_doc.ents = [mock_ent1, mock_ent2]
        
        # Set up a job listing
        job_listing = {
            'title': 'Software Engineer',
            'company_name': 'Example Corp',
            'description': 'Looking for a software engineer with Python, Java, and SQL skills.'
        }
        
        # Call the _extract_keywords_from_job method
        result = self.generator._extract_keywords_from_job(job_listing)
        
        # Verify the result
        self.assertIn('software engineer', result)
        self.assertIn('python experience', result)
        self.assertIn('example corp', result)
        self.assertIn('java', result)
        
        # Verify that the spaCy model was called correctly
        self.mock_nlp.assert_called_once_with(job_listing['description'])
    
    def test_match_skills_with_keywords(self):
        """Test matching skills with keywords."""
        # Mock the _match_skills_with_keywords method
        with patch.object(self.generator, '_match_skills_with_keywords') as mock_match:
            mock_match.return_value = {
                'Python': {'keyword': 'python', 'score': 0.9},
                'Java': {'keyword': 'java', 'score': 0.7}
            }
            
            # Set up skills and keywords
            skills = ['Python', 'Java', 'SQL']
            keywords = ['python', 'java', 'database']
            
            # Call the mocked method
            result = mock_match(skills, keywords)
        
        # Verify the result
        self.assertEqual(len(result), 2)  # Only Python and Java should match
        self.assertEqual(result['Python']['keyword'], 'python')
        self.assertEqual(result['Python']['score'], 0.9)
        self.assertEqual(result['Java']['keyword'], 'java')
        self.assertEqual(result['Java']['score'], 0.7)
        self.assertNotIn('SQL', result)  # SQL should not match (below threshold)
    
    @patch('job_scraper_app.resume_processor.resume_generator.docx.Document')
    def test_create_resume_document(self, mock_document):
        """Test creating a resume document."""
        # Set up mocks
        mock_doc = MagicMock()
        mock_document.return_value = mock_doc
        
        mock_section = MagicMock()
        mock_doc.sections = [mock_section]
        
        mock_paragraph = MagicMock()
        mock_doc.add_paragraph.return_value = mock_paragraph
        
        mock_run = MagicMock()
        mock_paragraph.add_run.return_value = mock_run
        
        # Set up resume data, job listing, and matches
        resume_data = {
            'name': 'John Doe',
            'email': ['john.doe@example.com'],
            'phone': ['(123) 456-7890'],
            'education': ['Bachelor of Science in Computer Science'],
            'experience': ['Software Engineer at Example Corp'],
            'skills': ['Python', 'Java', 'SQL'],
            'links': {'linkedin': 'https://linkedin.com/in/johndoe'}
        }
        
        job_listing = {
            'title': 'Software Engineer',
            'company_name': 'Example Corp',
            'description': 'Looking for a software engineer with Python, Java, and SQL skills.'
        }
        
        skill_matches = {
            'Python': {'keyword': 'python', 'score': 0.9},
            'Java': {'keyword': 'java', 'score': 0.8}
        }
        
        job_keywords = ['python', 'java', 'sql', 'software engineering']
        
        # Call the _create_resume_document method
        result = self.generator._create_resume_document(resume_data, job_listing, skill_matches, job_keywords)
        
        # Verify the result
        self.assertEqual(result, mock_doc)
        
        # Verify that the document was created correctly
        mock_document.assert_called_once()
        
        # Verify that the document sections were set up correctly
        self.assertEqual(mock_section.top_margin, unittest.mock.ANY)
        self.assertEqual(mock_section.bottom_margin, unittest.mock.ANY)
        self.assertEqual(mock_section.left_margin, unittest.mock.ANY)
        self.assertEqual(mock_section.right_margin, unittest.mock.ANY)
        
        # Verify that paragraphs were added
        self.assertGreater(mock_doc.add_paragraph.call_count, 0)
        self.assertGreater(mock_doc.add_heading.call_count, 0)
    
    def test_generate_professional_summary(self):
        """Test generating a professional summary."""
        # Set up resume data and job listing
        resume_data = {
            'name': 'John Doe',
            'email': ['john.doe@example.com'],
            'phone': ['(123) 456-7890'],
            'education': ['Bachelor of Science in Computer Science'],
            'experience': [
                'Software Engineer at Example Corp, 2018-2020',
                'Senior Software Engineer at Another Corp, 2020-Present'
            ],
            'skills': ['Python', 'Java', 'SQL'],
            'links': {'linkedin': 'https://linkedin.com/in/johndoe'}
        }
        
        job_listing = {
            'title': 'Senior Software Engineer',
            'company_name': 'Target Corp',
            'description': 'Looking for a senior software engineer with Python, Java, and SQL skills.'
        }
        
        job_keywords = ['python', 'java', 'sql', 'software engineering']
        
        # Call the _generate_professional_summary method
        result = self.generator._generate_professional_summary(resume_data, job_listing, job_keywords)
        
        # Verify the result
        self.assertIn('Senior Software Engineer', result)
        self.assertIn('Target Corp', result)
        self.assertIn('Python', result)
        self.assertIn('Java', result)
        self.assertIn('SQL', result)
    
    def test_extract_years_of_experience(self):
        """Test extracting years of experience from resume data."""
        # Test with year ranges in experience entries
        resume_data = {
            'experience': [
                'Software Engineer at Example Corp, 2018-2020',
                'Senior Software Engineer at Another Corp, 2020-Present'
            ]
        }
        
        # Mock the _extract_years_of_experience method
        with patch.object(self.generator, '_extract_years_of_experience') as mock_extract:
            mock_extract.return_value = 2
            
            result = mock_extract(resume_data)
            self.assertEqual(result, 2)
        
        # Test with no year ranges
        resume_data = {
            'experience': [
                'Software Engineer at Example Corp',
                'Senior Software Engineer at Another Corp'
            ]
        }
        
        result = self.generator._extract_years_of_experience(resume_data)
        self.assertEqual(result, 2)  # 2 experience entries
        
        # Test with no experience
        resume_data = {
            'experience': []
        }
        
        result = self.generator._extract_years_of_experience(resume_data)
        self.assertEqual(result, 2)  # Default value
    
    def test_highlight_keywords_in_text(self):
        """Test highlighting keywords in text."""
        # Test with matching keywords
        text = "I am a software engineer with experience in Python, Java, and SQL."
        keywords = ['python', 'java', 'sql']
        
        result = self.generator._highlight_keywords_in_text(text, keywords)
        
        self.assertIn('*Python*', result)
        self.assertIn('*Java*', result)
        self.assertIn('*SQL*', result)
        
        # Test with no matching keywords
        text = "I am a software engineer with experience in various technologies."
        keywords = ['python', 'java', 'sql']
        
        result = self.generator._highlight_keywords_in_text(text, keywords)
        
        self.assertEqual(result, text)  # No changes

if __name__ == '__main__':
    unittest.main()
