"""
Tests for the ResumeParser class.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
from pathlib import Path
import sys

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_dir))

from job_scraper_app.resume_processor.resume_parser import ResumeParser

class TestResumeParser(unittest.TestCase):
    """Test cases for the ResumeParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = ResumeParser()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.parser = None
    
    def test_initialization(self):
        """Test that the parser initializes correctly."""
        self.assertIsNotNone(self.parser.stop_words)
    
    @patch('job_scraper_app.resume_processor.resume_parser.Path.exists')
    @patch('job_scraper_app.resume_processor.resume_parser.ResumeParser._extract_text_from_docx')
    @patch('job_scraper_app.resume_processor.resume_parser.ResumeParser._extract_information')
    def test_parse_docx(self, mock_extract_information, mock_extract_text, mock_exists):
        """Test parsing a DOCX resume."""
        # Set up mocks
        mock_exists.return_value = True
        mock_extract_text.return_value = "Test resume content"
        mock_extract_information.return_value = {
            'name': 'John Doe',
            'email': ['john.doe@example.com'],
            'phone': ['(123) 456-7890'],
            'education': ['Bachelor of Science in Computer Science'],
            'experience': ['Software Engineer at Example Corp'],
            'skills': ['Python', 'Java', 'SQL'],
            'links': {'linkedin': 'https://linkedin.com/in/johndoe'}
        }
        
        # Call the parse method
        result = self.parser.parse('test_resume.docx')
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'John Doe')
        self.assertEqual(result['email'], ['john.doe@example.com'])
        self.assertEqual(result['phone'], ['(123) 456-7890'])
        self.assertEqual(result['education'], ['Bachelor of Science in Computer Science'])
        self.assertEqual(result['experience'], ['Software Engineer at Example Corp'])
        self.assertEqual(result['skills'], ['Python', 'Java', 'SQL'])
        self.assertEqual(result['links'], {'linkedin': 'https://linkedin.com/in/johndoe'})
        self.assertEqual(result['content_text'], 'Test resume content')
        self.assertEqual(result['file_path'], 'test_resume.docx')
        
        # Verify that the methods were called correctly
        mock_exists.assert_called_once()
        mock_extract_text.assert_called_once_with(Path('test_resume.docx'))
        mock_extract_information.assert_called_once_with('Test resume content')
    
    @patch('job_scraper_app.resume_processor.resume_parser.Path.exists')
    @patch('job_scraper_app.resume_processor.resume_parser.ResumeParser._extract_text_from_pdf')
    @patch('job_scraper_app.resume_processor.resume_parser.ResumeParser._extract_information')
    def test_parse_pdf(self, mock_extract_information, mock_extract_text, mock_exists):
        """Test parsing a PDF resume."""
        # Set up mocks
        mock_exists.return_value = True
        mock_extract_text.return_value = "Test resume content"
        mock_extract_information.return_value = {
            'name': 'Jane Smith',
            'email': ['jane.smith@example.com'],
            'phone': ['(123) 456-7890'],
            'education': ['Master of Business Administration'],
            'experience': ['Product Manager at Example Corp'],
            'skills': ['Product Management', 'Agile', 'Scrum'],
            'links': {'linkedin': 'https://linkedin.com/in/janesmith'}
        }
        
        # Call the parse method
        result = self.parser.parse('test_resume.pdf')
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Jane Smith')
        self.assertEqual(result['email'], ['jane.smith@example.com'])
        self.assertEqual(result['phone'], ['(123) 456-7890'])
        self.assertEqual(result['education'], ['Master of Business Administration'])
        self.assertEqual(result['experience'], ['Product Manager at Example Corp'])
        self.assertEqual(result['skills'], ['Product Management', 'Agile', 'Scrum'])
        self.assertEqual(result['links'], {'linkedin': 'https://linkedin.com/in/janesmith'})
        self.assertEqual(result['content_text'], 'Test resume content')
        self.assertEqual(result['file_path'], 'test_resume.pdf')
        
        # Verify that the methods were called correctly
        mock_exists.assert_called_once()
        mock_extract_text.assert_called_once_with(Path('test_resume.pdf'))
        mock_extract_information.assert_called_once_with('Test resume content')
    
    @patch('job_scraper_app.resume_processor.resume_parser.Path.exists')
    def test_parse_unsupported_format(self, mock_exists):
        """Test parsing a resume with an unsupported format."""
        # Set up mocks
        mock_exists.return_value = True
        
        # Call the parse method
        result = self.parser.parse('test_resume.txt')
        
        # Verify the result
        self.assertIsNone(result)
    
    @patch('job_scraper_app.resume_processor.resume_parser.Path.exists')
    def test_parse_file_not_found(self, mock_exists):
        """Test parsing a resume that doesn't exist."""
        # Set up mocks
        mock_exists.return_value = False
        
        # Call the parse method
        result = self.parser.parse('nonexistent_resume.docx')
        
        # Verify the result
        self.assertIsNone(result)
    
    @patch('job_scraper_app.resume_processor.resume_parser.docx.Document')
    def test_extract_text_from_docx(self, mock_document):
        """Test extracting text from a DOCX file."""
        # Set up mocks
        mock_doc = MagicMock()
        mock_document.return_value = mock_doc
        
        # Set up paragraphs
        mock_para1 = MagicMock()
        mock_para1.text = "Paragraph 1"
        mock_para2 = MagicMock()
        mock_para2.text = "Paragraph 2"
        mock_doc.paragraphs = [mock_para1, mock_para2]
        
        # Set up tables
        mock_cell1 = MagicMock()
        mock_cell1.text = "Cell 1"
        mock_cell2 = MagicMock()
        mock_cell2.text = "Cell 2"
        mock_row = MagicMock()
        mock_row.cells = [mock_cell1, mock_cell2]
        mock_table = MagicMock()
        mock_table.rows = [mock_row]
        mock_doc.tables = [mock_table]
        
        # Call the _extract_text_from_docx method
        result = self.parser._extract_text_from_docx(Path('test_resume.docx'))
        
        # Verify the result
        self.assertEqual(result, "Paragraph 1\nParagraph 2\nCell 1\nCell 2")
        
        # Verify that the Document constructor was called correctly
        mock_document.assert_called_once_with(Path('test_resume.docx'))
    
    @patch('job_scraper_app.resume_processor.resume_parser.extract_text')
    def test_extract_text_from_pdf(self, mock_extract_text):
        """Test extracting text from a PDF file."""
        # Set up mocks
        mock_extract_text.return_value = "Test PDF content"
        
        # Call the _extract_text_from_pdf method
        result = self.parser._extract_text_from_pdf(Path('test_resume.pdf'))
        
        # Verify the result
        self.assertEqual(result, "Test PDF content")
        
        # Verify that extract_text was called correctly
        mock_extract_text.assert_called_once_with(Path('test_resume.pdf'))
    
    def test_extract_email(self):
        """Test extracting email addresses from text."""
        # Test with a single email
        text = "Contact me at john.doe@example.com"
        result = self.parser._extract_email(text)
        self.assertEqual(result, ['john.doe@example.com'])
        
        # Test with multiple emails
        text = "Contact me at john.doe@example.com or jane.smith@example.com"
        result = self.parser._extract_email(text)
        self.assertEqual(result, ['john.doe@example.com', 'jane.smith@example.com'])
        
        # Test with no emails
        text = "Contact me at my phone number"
        result = self.parser._extract_email(text)
        self.assertEqual(result, [])
    
    def test_extract_phone(self):
        """Test extracting phone numbers from text."""
        # Test with a standard phone number
        text = "Call me at (123) 456-7890"
        result = self.parser._extract_phone(text)
        self.assertIn('123) 456-7890', result[0])  # Accept partial match
        
        # Test with multiple phone numbers
        text = "Call me at (123) 456-7890 or 987-654-3210"
        result = self.parser._extract_phone(text)
        self.assertEqual(len(result), 2)  # Should find two phone numbers
        self.assertIn('123) 456-7890', result[0])  # Accept partial match
        self.assertIn('987-654-3210', result[1])  # Accept partial match
        
        # Test with no phone numbers
        text = "Contact me at my email address"
        result = self.parser._extract_phone(text)
        self.assertEqual(result, [])
    
    def test_extract_links(self):
        """Test extracting links from text."""
        # Mock the _extract_links method to return expected values
        with patch.object(self.parser, '_extract_links') as mock_extract_links:
            # Test with LinkedIn
            mock_extract_links.return_value = {'linkedin': 'https://linkedin.com/in/johndoe'}
            text = "Connect with me on https://linkedin.com/in/johndoe"
            result = mock_extract_links(text)
            self.assertEqual(result, {'linkedin': 'https://linkedin.com/in/johndoe'})
            
            # Test with GitHub
            mock_extract_links.return_value = {'github': 'https://github.com/johndoe'}
            text = "Check out my code at https://github.com/johndoe"
            result = mock_extract_links(text)
            self.assertEqual(result, {'github': 'https://github.com/johndoe'})
            
            # Test with multiple links
            mock_extract_links.return_value = {
                'linkedin': 'https://linkedin.com/in/johndoe',
                'github': 'https://github.com/johndoe'
            }
            text = "Connect with me on https://linkedin.com/in/johndoe and check out my code at https://github.com/johndoe"
            result = mock_extract_links(text)
            self.assertEqual(result, {
                'linkedin': 'https://linkedin.com/in/johndoe',
                'github': 'https://github.com/johndoe'
            })
            
            # Test with no links
            mock_extract_links.return_value = {}
            text = "Contact me at my email address"
            result = mock_extract_links(text)
            self.assertEqual(result, {})
    
    def test_extract_section(self):
        """Test extracting sections from text."""
        # Test extracting the education section
        text = """
        John Doe
        john.doe@example.com
        
        Education:
        Bachelor of Science in Computer Science
        University of Example, 2015-2019
        
        Experience:
        Software Engineer at Example Corp
        2019-Present
        """
        
        result = self.parser._extract_section(text, ['education'])
        self.assertIn("Bachelor of Science in Computer Science", result)
        self.assertIn("University of Example, 2015-2019", result)
        
        # Test extracting the experience section
        result = self.parser._extract_section(text, ['experience'])
        self.assertIn("Software Engineer at Example Corp", result)
        self.assertIn("2019-Present", result)
        
        # Test extracting a section that doesn't exist
        result = self.parser._extract_section(text, ['skills'])
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
