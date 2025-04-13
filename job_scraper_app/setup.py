from setuptools import setup, find_packages

setup(
    name="job_scraper_app",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
        "httpx",
        "beautifulsoup4",
        "lxml",
        "selenium",
        "webdriver-manager",
        "pandas",
        "sqlalchemy",
        "alembic",
        "flask",
        "flask-wtf",
        "flask-login",
        "python-docx",
        "pdfminer.six",
        "nltk",
        "spacy",
        "python-dotenv",
        "tqdm",
    ],
    entry_points={
        "console_scripts": [
            "job-scraper=job_scraper_app.main:main",
        ],
    },
)
