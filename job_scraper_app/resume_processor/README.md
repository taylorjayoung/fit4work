# Resume Processor

The Resume Processor is a component of the Job Scraper Application that provides functionality for parsing resumes, extracting structured information, and generating tailored resumes for specific job listings.

## Features

- **Resume Parsing**: Parse resumes in different formats (PDF, DOCX) and extract structured information.
- **Information Extraction**: Extract name, email, phone, education, experience, skills, and links from resumes.
- **Tailored Resume Generation**: Generate tailored resumes for specific job listings, highlighting relevant skills and experience.
- **Resume Management**: Upload, store, and retrieve resumes and tailored resumes.

## Components

### ResumeParser

The `ResumeParser` class provides functionality for parsing resumes in different formats and extracting structured information.

```python
from job_scraper_app.resume_processor.resume_parser import ResumeParser

# Create a parser
parser = ResumeParser()

# Parse a resume
resume_data = parser.parse('path/to/resume.docx')

# Access extracted information
name = resume_data['name']
email = resume_data['email']
phone = resume_data['phone']
education = resume_data['education']
experience = resume_data['experience']
skills = resume_data['skills']
links = resume_data['links']
```

### ResumeGenerator

The `ResumeGenerator` class provides functionality for generating tailored resumes based on job listings and user resumes.

```python
from job_scraper_app.resume_processor.resume_generator import ResumeGenerator

# Create a generator
generator = ResumeGenerator('path/to/output/directory')

# Generate a tailored resume
output_path = generator.generate_tailored_resume(
    resume_data,
    job_listing,
    'Tailored_Resume.docx'
)
```

### ResumeManager

The `ResumeManager` class provides a high-level interface for managing resumes, including uploading, parsing, storing, and generating tailored resumes.

```python
from job_scraper_app.resume_processor.resume_manager import ResumeManager

# Create a manager
manager = ResumeManager(config, db_engine)

# Upload a resume
resume_id = manager.upload_resume('path/to/resume.docx', 'My Resume', True)

# Generate a tailored resume
tailored_resume_id = manager.generate_tailored_resume(resume_id, job_listing_id)

# Get tailored resumes
tailored_resumes = manager.get_tailored_resumes(resume_id=resume_id)
```

## Usage

See the `resume_processor_example.py` script for a complete example of how to use the Resume Processor.

```bash
python resume_processor_example.py
```

## Dependencies

- **docx**: For parsing DOCX files.
- **pdfminer.six**: For parsing PDF files.
- **nltk**: For natural language processing.
- **spacy**: For advanced natural language processing.
- **sqlalchemy**: For database operations.

## Configuration

The Resume Processor requires the following configuration settings:

```json
{
  "resume_settings": {
    "storage_path": "path/to/resume/storage"
  }
}
```

## Database Schema

The Resume Processor uses the following database tables:

- **Resume**: Stores information about uploaded resumes.
- **TailoredResume**: Stores information about tailored resumes.
- **JobListing**: Stores information about job listings (used for generating tailored resumes).

## Testing

The Resume Processor includes a comprehensive test suite. You can run the tests using the following command:

```bash
python -m unittest discover -v
```

Or run specific tests:

```bash
python -m unittest tests.resume_processor.test_resume_parser
python -m unittest tests.resume_processor.test_resume_generator
python -m unittest tests.resume_processor.test_resume_manager
