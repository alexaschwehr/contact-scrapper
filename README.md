# LinkedIn Scraper - Job Posting to Recruiter Contact Finder

This tool uses a LangChain agent to automatically find recruiter, HR, and executive contact details from job postings on LinkedIn, Glassdoor, or ZipRecruiter. It can process batch process multiple jobs from an Excel file.

## How It Works

1. **Input**: You provide a job posting URL (LinkedIn, Glassdoor, or ZipRecruiter) or an Excel file with job URLs
2. **Job Scraping**: The tool scrapes the job posting to extract:
   - Company name
   - Job title
   - Location
   - Job source
   - Job URL
3. **Executive Profile Search**: Uses Grok AI to find executive profiles (CEO, CTO, CFO) and HR/recruiter LinkedIn profiles for that company
4. **Email Enrichment** (Optional): Uses SalesQL API to enrich profiles with email addresses
5. **Output**: Returns structured JSON with contact information including:
   - Executive profiles (CEO, CTO, CFO)
   - HR contacts
   - Recruiter contacts
   - Name, title, LinkedIn profile URL, and email (if enriched)

## Setup

### Python Version Requirement

**Python 3.10 or higher is required.**

This project uses:
- **LangChain 1.0+** which requires Python 3.10+
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
SALESQL_API_KEY=your_salesql_api_key_here
SALESQL_ENABLED=true
```

**Get API Keys:**
- **Grok API Key**: https://x.ai/api (xAI Developer Platform)
- **SalesQL API Key**: https://salesql.com (for email enrichment)

## Usage


### Batch Processing from Excel File

The `process_excel_jobs.py` script allows you to process multiple job URLs from an Excel file at once.

#### Excel File Format

Create an Excel file (`.xlsx`) with job URLs. The script will automatically detect the column containing URLs by looking for columns with "url" or "link" in the header. If no such column is found, it defaults to the first column.

Example Excel structure:
- Column A (or any column with "URL" or "Link" in header): Job URLs
- Each row should contain a valid job URL starting with `http://` or `https://`

#### Running process_excel_jobs

**Basic usage** (uses default file `linkedin_jobpost.xlsx` and output `executive_profiles_results.json`):

```bash
python process_excel_jobs.py
```


#### Process Flow for process_excel_jobs

1. **Read Excel File**: The script reads job URLs from the specified Excel file
   - Automatically detects the URL column by searching for "url" or "link" in column headers
   - Validates that URLs start with `http://` or `https://`
   - Skips empty rows and invalid URLs

2. **Initialize Agent**: Creates a RecruiterFinderAgent instance to process each job

3. **Process Each Job URL**: For each URL in the Excel file:
   - Scrapes the job posting to extract company name, job title, location, and source
   - Uses Grok AI to find executive profiles (CEO, CTO, CFO) and HR/recruiter contacts
   - Displays progress and summary for each job processed

4. **Save Results**: All results are saved to a JSON file with the following structure:
   ```json
   [
     {
       "company": "Company Name",
       "location": "Location",
       "job_title": "Job Title",
       "source": "linkedin",
       "job_url": "https://...",
       "ceo": {"name": "...", "title": "...", "linkedin": "..."},
       "cto": {"name": "...", "title": "...", "linkedin": "..."},
       "cfo": {"name": "...", "title": "...", "linkedin": "..."},
       "hr": [{"name": "...", "title": "...", "linkedin": "..."}],
       "recruiters": [{"name": "...", "title": "...", "linkedin": "..."}]
     }
   ]
   ```

5. **Email Enrichment** (if enabled): After processing all jobs, the script can enrich the profiles with email addresses using SalesQL API
   - Only runs if `enable_email_enrichment=True` and `SALESQL_ENABLED=true` in environment
   - Updates the JSON file with email addresses for found profiles

#### Example Output

When running `process_excel_jobs.py`, you'll see progress for each job:

```
============================================================
EXCEL JOB PROCESSOR - Executive Profile Finder
============================================================

 Reading job URLs from: linkedin_jobpost.xlsx
 Found 3 job URL(s) in Excel file

 Initializing agent...
 Agent initialized successfully

 Processing 3 job posting(s)...
============================================================

[1/3] Processing: https://www.linkedin.com/jobs/view/1234567890
------------------------------------------------------------
   Company: Google
   CEO: Found
   CTO: Found
   CFO: Found
   HR: 2 profile(s)
   Recruiters: 3 profile(s)

[2/3] Processing: https://www.linkedin.com/jobs/view/0987654321
------------------------------------------------------------
   Company: Microsoft
   CEO: Found
   CTO: Not found
   CFO: Found
   HR: 1 profile(s)
   Recruiters: 2 profile(s)

============================================================
 Saving results to: executive_profiles_results.json
 Results saved successfully!
   Total jobs processed: 3

============================================================
 Processing complete!

============================================================
 EMAIL ENRICHMENT - SalesQL Integration
============================================================
[... enrichment process ...]
```

## Supported Job Sites

- LinkedIn
- Glassdoor
- ZipRecruiter
- Generic job sites (basic scraping)

## Project Structure

- `agent.py` - LangChain agent that orchestrates the workflow
- `tools.py` - LangChain tools (job scraping, executive profile search)
- `job_scraper.py` - Scrapes job information from URLs using Playwright
- `process_excel_jobs.py` - Batch processes job URLs from Excel files
- `salesql_enricher.py` - SalesQL API integration for email enrichment
- `scrapein_integration/scrapein.py` - Scrapin.io API client
- `tests/run_test.py` - Single job URL processing entry point
- `tests/test_job_scraping.py` - Tests for job scraping functionality
- `tests/test_grok_job_title.py` - Tests for Grok integration

## Configuration

### Environment Variables

- `GROK_API_KEY` - Required for finding executive profiles
- `SALESQL_API_KEY` - Optional, for email enrichment
- `SALESQL_ENABLED` - Set to `true` or `false` to enable/disable email enrichment (default: `true`)

## Notes

- The tool filters results to show executive profiles (CEO, CTO, CFO) and HR/recruiter contacts
- Email addresses may not always be available depending on SalesQL data coverage
- The agent uses Grok (grok-3) by default (can be changed in `agent.py`)
- Rate limits: Scrapin.io allows 500 requests per minute
- Processing multiple jobs from Excel may take time depending on the number of URLs

## Troubleshooting

**Error: "GROK_API_KEY is not set"**
- Make sure you've added your Grok API key to the `.env` file

**Error: "Excel file not found"**
- Make sure the Excel file path is correct
- Check that the file exists in the specified location

**No recruiters found**
- The company might not have recruiter data available
- Try a different company or job posting

**Job scraping fails**
- Make sure Playwright is installed: `playwright install chromium`
- The job URL might be invalid or the site structure changed
- Some job sites may have anti-scraping measures

**Email enrichment not working**
- Check that `SALESQL_API_KEY` is set in your `.env` file
- Verify that `SALESQL_ENABLED=true` in your `.env` file
- Check your SalesQL API quota and rate limits

