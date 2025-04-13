"""
Tests for the ResumeManager class.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import sys

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_dir))

from job_scraper_app.resume_processor.resume_manager import ResumeManager

class TestResumeManager(unittest.TestCase):
    """Test cases for the ResumeManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "resume_settings": {
                "storage_path": "/tmp/test_resumes"
            }
        }
        
        # Create a mock database engine
        self.db_engine = MagicMock()
        
        # Create a mock Session class
        self.mock_session = MagicMock()
        self.mock_session_instance = MagicMock()
        self.mock_session.return_value = self.mock_session_instance
        
        # Create mock Resume and JobListing classes
        self.mock_resume = MagicMock()
        self.mock_job_listing = MagicMock()
        self.mock_tailored_resume = MagicMock()
        
        # Patch the sessionmaker, Resume, and JobListing
        self.sessionmaker_patcher = patch('job_scraper_app.resume_processor.resume_manager.sessionmaker', return_value=self.mock_session)
        self.resume_patcher = patch('job_scraper_app.resume_processor.resume_manager.Resume', self.mock_resume)
        self.job_listing_patcher = patch('job_scraper_app.resume_processor.resume_manager.JobListing', self.mock_job_listing)
        self.tailored_resume_patcher = patch('job_scraper_app.resume_processor.resume_manager.TailoredResume', self.mock_tailored_resume)
        
        # Patch the ResumeParser and ResumeGenerator
        self.parser_patcher = patch('job_scraper_app.resume_processor.resume_manager.ResumeParser')
        self.generator_patcher = patch('job_scraper_app.resume_processor.resume_manager.ResumeGenerator')
        
        # Patch os.makedirs
        self.makedirs_patcher = patch('os.makedirs')
        
        # Start the patches
        self.mock_sessionmaker = self.sessionmaker_patcher.start()
        self.mock_resume_class = self.resume_patcher.start()
        self.mock_job_listing_class = self.job_listing_patcher.start()
        self.mock_tailored_resume_class = self.tailored_resume_patcher.start()
        self.mock_parser_class = self.parser_patcher.start()
        self.mock_generator_class = self.generator_patcher.start()
        self.mock_makedirs = self.makedirs_patcher.start()
        
        # Create mock instances for parser and generator
        self.mock_parser = MagicMock()
        self.mock_generator = MagicMock()
        self.mock_parser_class.return_value = self.mock_parser
        self.mock_generator_class.return_value = self.mock_generator
        
        # Create the ResumeManager
        self.manager = ResumeManager(self.config, self.db_engine)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Stop the patches
        self.sessionmaker_patcher.stop()
        self.resume_patcher.stop()
        self.job_listing_patcher.stop()
        self.tailored_resume_patcher.stop()
        self.parser_patcher.stop()
        self.generator_patcher.stop()
        self.makedirs_patcher.stop()
        
        self.manager = None
    
    def test_initialization(self):
        """Test that the manager initializes correctly."""
        # Check that the config and db_engine are set correctly
        self.assertEqual(self.manager.config, self.config)
        self.assertEqual(self.manager.db_engine, self.db_engine)
        
        # Check that the Session is created correctly
        self.mock_sessionmaker.assert_called_once_with(bind=self.db_engine)
        self.assertEqual(self.manager.Session, self.mock_session)
        
        # Check that the storage directories are created
        self.mock_makedirs.assert_any_call(Path('/tmp/test_resumes'), exist_ok=True)
        self.mock_makedirs.assert_any_call(Path('/tmp/test_resumes/tailored'), exist_ok=True)
        
        # Check that the parser and generator are initialized correctly
        self.mock_parser_class.assert_called_once()
        self.mock_generator_class.assert_called_once_with(Path('/tmp/test_resumes/tailored'))
        self.assertEqual(self.manager.parser, self.mock_parser)
        self.assertEqual(self.manager.generator, self.mock_generator)
    
    @patch('pathlib.Path.exists')
    @patch('shutil.copy2')
    def test_upload_resume(self, mock_copy2, mock_exists):
        """Test uploading a resume."""
        # Set up mocks
        mock_exists.return_value = True
        
        # Set up the parser to return resume data
        resume_data = {
            'name': 'John Doe',
            'email': ['john.doe@example.com'],
            'phone': ['(123) 456-7890'],
            'education': ['Bachelor of Science in Computer Science'],
            'experience': ['Software Engineer at Example Corp'],
            'skills': ['Python', 'Java', 'SQL'],
            'links': {'linkedin': 'https://linkedin.com/in/johndoe'},
            'content_text': 'Test resume content'
        }
        self.mock_parser.parse.return_value = resume_data
        
        # Set up the mock resume instance
        mock_resume_instance = MagicMock()
        mock_resume_instance.id = 123
        self.mock_resume.return_value = mock_resume_instance
        
        # Call the upload_resume method
        result = self.manager.upload_resume('test_resume.docx', 'John Doe Resume', True)
        
        # Verify the result
        self.assertEqual(result, 123)
        
        # Verify that the parser was called correctly
        self.mock_parser.parse.assert_called_once()
        
        # Verify that the file was copied
        mock_copy2.assert_called_once()
        
        # Verify that the session was used correctly
        self.mock_session.assert_called_once()
        
        # Verify that the primary flag was reset on all resumes
        self.mock_session_instance.query.assert_called_once_with(self.mock_resume_class)
        self.mock_session_instance.query.return_value.update.assert_called_once_with({self.mock_resume_class.is_primary: False})
        
        # Verify that the resume was created correctly
        self.mock_resume_class.assert_called_once_with(
            name='John Doe Resume',
            file_path=str(Path('/tmp/test_resumes/John Doe Resume.docx')),
            content_text='Test resume content',
            upload_date=unittest.mock.ANY,
            is_primary=True
        )
        
        # Verify that the session was committed
        self.mock_session_instance.add.assert_called_once_with(mock_resume_instance)
        self.mock_session_instance.commit.assert_called_once()
        
        # Verify that the session was closed
        self.mock_session_instance.close.assert_called_once()
    
    @patch('pathlib.Path.exists')
    def test_upload_resume_file_not_found(self, mock_exists):
        """Test uploading a resume that doesn't exist."""
        # Set up mocks
        mock_exists.return_value = False
        
        # Call the upload_resume method
        result = self.manager.upload_resume('nonexistent_resume.docx')
        
        # Verify the result
        self.assertIsNone(result)
        
        # Verify that the session was not used
        self.mock_session.assert_not_called()
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.suffix', new_callable=MagicMock)
    def test_upload_resume_unsupported_format(self, mock_suffix, mock_exists):
        """Test uploading a resume with an unsupported format."""
        # Set up mocks
        mock_exists.return_value = True
        mock_suffix.return_value = '.txt'
        
        # Call the upload_resume method
        result = self.manager.upload_resume('test_resume.txt')
        
        # Verify the result
        self.assertIsNone(result)
        
        # Verify that the session was not used
        self.mock_session.assert_not_called()
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.suffix', new_callable=MagicMock)
    def test_upload_resume_parse_error(self, mock_suffix, mock_exists):
        """Test uploading a resume that can't be parsed."""
        # Set up mocks
        mock_exists.return_value = True
        mock_suffix.return_value = '.docx'
        
        # Set up the parser to return None (parse error)
        self.mock_parser.parse.return_value = None
        
        # Call the upload_resume method
        result = self.manager.upload_resume('test_resume.docx')
        
        # Verify the result
        self.assertIsNone(result)
        
        # Verify that the session was not used
        self.mock_session.assert_not_called()
    
    def test_generate_tailored_resume(self):
        """Test generating a tailored resume."""
        # Set up mock resume and job listing
        mock_resume_instance = MagicMock()
        mock_resume_instance.id = 123
        mock_resume_instance.name = 'John Doe Resume'
        mock_resume_instance.file_path = '/tmp/test_resumes/John Doe Resume.docx'
        
        mock_job_listing_instance = MagicMock()
        mock_job_listing_instance.id = 456
        mock_job_listing_instance.title = 'Software Engineer'
        mock_job_listing_instance.company_name = 'Example Corp'
        mock_job_listing_instance.description = 'Job description'
        
        # Set up the session to return the mock instances
        self.mock_session_instance.query.return_value.filter_by.return_value.first.side_effect = [
            mock_resume_instance,
            mock_job_listing_instance
        ]
        
        # Set up the parser to return resume data
        resume_data = {
            'name': 'John Doe',
            'email': ['john.doe@example.com'],
            'phone': ['(123) 456-7890'],
            'education': ['Bachelor of Science in Computer Science'],
            'experience': ['Software Engineer at Example Corp'],
            'skills': ['Python', 'Java', 'SQL'],
            'links': {'linkedin': 'https://linkedin.com/in/johndoe'},
            'content_text': 'Test resume content'
        }
        self.mock_parser.parse.return_value = resume_data
        
        # Set up the generator to return a file path
        output_path = '/tmp/test_resumes/tailored/Tailored_Resume_John_Doe_Resume_Example_Corp_Software_Engineer.docx'
        self.mock_generator.generate_tailored_resume.return_value = output_path
        
        # Set up the mock tailored resume instance
        mock_tailored_resume_instance = MagicMock()
        mock_tailored_resume_instance.id = 789
        self.mock_tailored_resume.return_value = mock_tailored_resume_instance
        
        # Call the generate_tailored_resume method
        result = self.manager.generate_tailored_resume(123, 456)
        
        # Verify the result
        self.assertEqual(result, 789)
        
        # Verify that the session was used correctly
        self.mock_session.assert_called_once()
        
        # Verify that the resume and job listing were queried
        self.mock_session_instance.query.assert_any_call(self.mock_resume_class)
        self.mock_session_instance.query.assert_any_call(self.mock_job_listing_class)
        self.mock_session_instance.query.return_value.filter_by.assert_any_call(id=123)
        self.mock_session_instance.query.return_value.filter_by.assert_any_call(id=456)
        
        # Verify that the parser was called correctly
        self.mock_parser.parse.assert_called_once_with(mock_resume_instance.file_path)
        
        # Verify that the generator was called correctly
        self.mock_generator.generate_tailored_resume.assert_called_once_with(
            resume_data,
            {
                'title': 'Software Engineer',
                'company_name': 'Example Corp',
                'description': 'Job description'
            },
            'Tailored_Resume_John Doe Resume_Example Corp_Software Engineer.docx'
        )
        
        # Verify that the tailored resume was created correctly
        self.mock_tailored_resume.assert_called_once_with(
            name='John Doe Resume for Example Corp - Software Engineer',
            file_path=output_path,
            content_text='Test resume content',
            creation_date=unittest.mock.ANY,
            base_resume_id=123,
            job_listing_id=456
        )
        
        # Verify that the session was committed
        self.mock_session_instance.add.assert_called_once_with(mock_tailored_resume_instance)
        self.mock_session_instance.commit.assert_called_once()
        
        # Verify that the session was closed
        self.mock_session_instance.close.assert_called_once()
    
    def test_generate_tailored_resume_not_found(self):
        """Test generating a tailored resume when the resume or job listing is not found."""
        # Set up the session to return None (resume not found)
        self.mock_session_instance.query.return_value.filter_by.return_value.first.return_value = None
        
        # Call the generate_tailored_resume method
        result = self.manager.generate_tailored_resume(123, 456)
        
        # Verify the result
        self.assertIsNone(result)
        
        # Verify that the session was used correctly
        self.mock_session.assert_called_once()
        
        # Verify that the parser was not called
        self.mock_parser.parse.assert_not_called()
        
        # Verify that the generator was not called
        self.mock_generator.generate_tailored_resume.assert_not_called()
        
        # Verify that the session was closed
        self.mock_session_instance.close.assert_called_once()
    
    def test_get_tailored_resumes(self):
        """Test getting tailored resumes."""
        # Set up mock tailored resumes
        mock_tailored_resume1 = MagicMock()
        mock_tailored_resume2 = MagicMock()
        
        # Set up the session to return the mock tailored resumes
        mock_query = self.mock_session_instance.query.return_value
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value.all.return_value = [mock_tailored_resume1, mock_tailored_resume2]
        
        # Call the get_tailored_resumes method
        result = self.manager.get_tailored_resumes(resume_id=123, job_listing_id=456)
        
        # Verify the result
        self.assertEqual(result, [mock_tailored_resume1, mock_tailored_resume2])
        
        # Verify that the session was used correctly
        self.mock_session.assert_called_once()
        
        # Verify that the tailored resumes were queried
        self.mock_session_instance.query.assert_called_once_with(self.mock_tailored_resume_class)
        mock_query.filter_by.assert_any_call(base_resume_id=123)
        mock_query.filter_by.assert_any_call(job_listing_id=456)
        mock_query.order_by.assert_called_once()
        mock_query.order_by.return_value.all.assert_called_once()
        
        # Verify that the session was closed
        self.mock_session_instance.close.assert_called_once()
    
    def test_get_tailored_resumes_error(self):
        """Test getting tailored resumes when an error occurs."""
        # Make the session raise an exception
        self.mock_session_instance.query.side_effect = Exception("Test exception")
        
        # Call the get_tailored_resumes method
        result = self.manager.get_tailored_resumes()
        
        # Verify the result
        self.assertEqual(result, [])
        
        # Verify that the session was used correctly
        self.mock_session.assert_called_once()
        
        # Verify that the session was closed
        self.mock_session_instance.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
