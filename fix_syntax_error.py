#!/usr/bin/env python3
"""
Script to fix the syntax error in the one-liner example.

The original code had a syntax error:
```
from scrapers.scraper_manager import ScraperManager; import json; with open('config.json', 'r') as f: config = json.load(f); scraper = ScraperManager(config, None); results = scraper.scrape_site('Remote.co'); print(f'Scraped {len(results)} job listings')
```

The error was due to trying to use a `with` statement in a one-liner, which is not allowed in Python.
This script shows the correct way to write this code.
"""

def main():
    """Run the fixed one-liner example."""
    # The original one-liner with syntax error:
    # from scrapers.scraper_manager import ScraperManager; import json; with open('config.json', 'r') as f: config = json.load(f); scraper = ScraperManager(config, None); results = scraper.scrape_site('Remote.co'); print(f'Scraped {len(results)} job listings')
    
    # Fixed version 1: Split into multiple lines
    print("Fixed version 1: Split into multiple lines")
    print("```python")
    print("from job_scraper_app.scrapers.scraper_manager import ScraperManager")
    print("import json")
    print("with open('job_scraper_app/config.json', 'r') as f:")
    print("    config = json.load(f)")
    print("scraper = ScraperManager(config, None)")
    print("results = scraper.scrape_site('Remote.co')")
    print("print(f'Scraped {len(results)} job listings')")
    print("```")
    
    # Fixed version 2: Use a function to read the config file
    print("\nFixed version 2: Use a function to read the config file")
    print("```python")
    print("from job_scraper_app.scrapers.scraper_manager import ScraperManager")
    print("import json")
    print("def read_config(file_path):")
    print("    with open(file_path, 'r') as f:")
    print("        return json.load(f)")
    print("config = read_config('job_scraper_app/config.json')")
    print("scraper = ScraperManager(config, None)")
    print("results = scraper.scrape_site('Remote.co')")
    print("print(f'Scraped {len(results)} job listings')")
    print("```")
    
    # Fixed version 3: Use a one-liner without the with statement
    print("\nFixed version 3: Use a one-liner without the with statement")
    print("```python")
    print("from job_scraper_app.scrapers.scraper_manager import ScraperManager; import json; import os; config = json.load(open('job_scraper_app/config.json', 'r')); scraper = ScraperManager(config, None); results = scraper.scrape_site('Remote.co'); print(f'Scraped {len(results)} job listings')")
    print("```")
    print("Note: This version doesn't properly close the file, which is not recommended for production code.")
    
    # Fixed version 4: Use a context manager in a function
    print("\nFixed version 4: Use a context manager in a function (recommended)")
    print("```python")
    print("def scrape_and_print():")
    print("    from job_scraper_app.scrapers.scraper_manager import ScraperManager")
    print("    import json")
    print("    with open('job_scraper_app/config.json', 'r') as f:")
    print("        config = json.load(f)")
    print("    scraper = ScraperManager(config, None)")
    print("    results = scraper.scrape_site('Remote.co')")
    print("    print(f'Scraped {len(results)} job listings')")
    print("    return results")
    print("results = scrape_and_print()")
    print("```")

if __name__ == "__main__":
    main()
