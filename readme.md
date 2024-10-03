# LinkedIn Job Scraper

## Overview

This Python script scrapes job listings from LinkedIn based on provided keywords and locations. It collects job details such as job title, company, location, description, and application URLs. The results are saved in a JSON file.

## Features

- Scrapes job data from LinkedIn, including job title, location, company, and description.
- Handles pagination to retrieve multiple pages of job listings.
- Automatically saves job data to a JSON file, either appending to an existing file or creating a new one.
- Includes retry logic for handling network errors or request failures.
- Mimics browser requests with custom headers to avoid getting blocked by LinkedIn's security measures.

## Requirements

- Python 3.x
- `requests` library
- `beautifulsoup4` library
- `lxml` parser for BeautifulSoup

You can install the required libraries using the following command:

```bash
pip install requests beautifulsoup4 lxml
```
