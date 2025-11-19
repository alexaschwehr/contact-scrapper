# Recruiter Finder - Job Posting to Recruiter Email Tool

This tool uses a LangChain agent to automatically find recruiter/HR contact emails from job postings on LinkedIn, Glassdoor, or ZipRecruiter.

## How It Works

1. **Input**: You provide a job posting URL (LinkedIn, Glassdoor, or ZipRecruiter)
2. **Job Scraping**: The tool scrapes the job posting to extract:
   - Company name
   - Job title
   - Job source
   - Job URL
3. **Recruiter Search**: Uses Scrapin.io API to find recruiter/HR contacts for that company
4. **Output**: Returns structured JSON with recruiter information including:
   - Name
   - Job title
   - Email address
   - LinkedIn profile URL

## Setup

### 0. Python Version Requirement

**Python 3.10 or higher is required.**

This project uses:
- **LangChain 1.0+** which requires Python 3.10+ (Python 3.9 reached end-of-life in October 2025)
- **Playwright** which works best with Python 3.10+
- Modern type hints and features that are well-supported in Python 3.10+

**Recommended:** Python 3.10, 3.11, or 3.12

Check your Python version:
```bash
python --version
```

If you need to install or upgrade Python, download it from [python.org](https://www.python.org/downloads/).

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright (for job scraping)

```bash
playwright install chromium
```

### 3. Set Up API Keys

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```
GROK_API_KEY=your_grok_api_key_here
SCRAPIN_API_KEY=your_scrapin_api_key_here
```

**Get API Keys:**
- **Grok API Key**: https://x.ai/api (xAI Developer Platform)
- **Scrapin.io API Key**: https://scrapin.io (Dashboard > Integrations)

## Usage

### Basic Usage

Run the script and paste a job URL when prompted:

```bash
python run_test.py
```

### Command Line Usage

You can also pass the job URL as an argument:

```bash
python run_test.py "https://www.linkedin.com/jobs/view/1234567890"
```

### Example Output

```
============================================================
RECRUITER SEARCH RESULTS
============================================================

📋 Job Information:
   Company: Google
   Job Title: Software Engineer
   Source: linkedin
   URL: https://www.linkedin.com/jobs/view/1234567890

👥 Found 3 Recruiter(s):
------------------------------------------------------------

1. John Doe
   Title: Technical Recruiter
   📧 Email: john.doe@google.com
   🔗 LinkedIn: https://linkedin.com/in/johndoe

2. Jane Smith
   Title: Talent Acquisition Specialist
   📧 Email: jane.smith@google.com
   🔗 LinkedIn: https://linkedin.com/in/janesmith

============================================================
```

Results are also saved to `recruiter_results.json` for easy access.

## Supported Job Sites

- ✅ LinkedIn
- ✅ Glassdoor
- ✅ ZipRecruiter

## Project Structure

- `agent.py` - LangChain agent that orchestrates the workflow
- `tools.py` - LangChain tools (job scraping, recruiter search)
- `job_scraper.py` - Scrapes job information from URLs using Playwright
- `scrapein.py` - Scrapin.io API client for finding recruiters
- `run_test.py` - Main entry point and CLI interface

## Notes

- The tool filters results to only show people with recruiter/HR-related job titles
- Email addresses may not always be available depending on Scrapin.io data coverage
- The agent uses Grok (grok-beta) by default (can be changed in `agent.py`)
- Rate limits: Scrapin.io allows 500 requests per minute

## Troubleshooting

**Error: "SCRAPIN_API_KEY is not set"**
- Make sure you've created a `.env` file with your Scrapin.io API key

**Error: "GROK_API_KEY is not set"**
- Make sure you've added your Grok API key to the `.env` file

**No recruiters found**
- The company might not have recruiter data in Scrapin.io
- Try a different company or job posting

**Job scraping fails**
- Make sure Playwright is installed: `playwright install chromium`
- The job URL might be invalid or the site structure changed

