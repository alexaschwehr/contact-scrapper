from typing import Dict, Any, Optional
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import os
import json
import re
from job_scraper import JobScraper
from dotenv import load_dotenv

load_dotenv()

_job_scraper = JobScraper()
_grok_model = None  # Will be initialized lazily


def _get_grok_model() -> Optional[ChatOpenAI]:
    global _grok_model
    if _grok_model is None:
        try:
            api_key = os.getenv("GROK_API_KEY")
            if api_key:
                _grok_model = ChatOpenAI(
                    model="grok-3",
                    temperature=0,
                    api_key=api_key,
                    base_url="https://api.x.ai/v1",
                )
        except Exception:
            pass
    return _grok_model


@tool
def get_job_info_tool(job_url: str) -> Dict[str, Any]:
    """
    Scrapes a job posting URL to extract company name, job title, location, and source.
    Supports LinkedIn, Glassdoor, and ZipRecruiter job postings.
    """
    return _job_scraper.get_job_info(job_url)


@tool
def find_executive_profiles_tool(company_name: str,location: str = "",) -> Dict[str, Any]:
    """
    Uses Grok to find CEO, CTO, CFO, HR, and recruiter LinkedIn profiles for a company.
    Returns a dictionary with profiles organized by role.
    """
    model = _get_grok_model()
    if model is None:
        return {
            "error": "Grok API not available. Please set GROK_API_KEY in environment."
        }
    
    location_context = f" located in {location}" if location else ""
    
    prompt = f"""Please find LinkedIn profiles for key executives and HR/recruitment staff at {company_name}{location_context}.

            I need you to find and provide LinkedIn profile URLs for:
            1. CEO (Chief Executive Officer)
            2. CTO (Chief Technology Officer)
            3. CFO (Chief Financial Officer)
            4. HR Director/Manager or Head of Human Resources
            5. Recruiters or Talent Acquisition staff

            For each person found, provide:
            - Full name
            - Job title/position
            - LinkedIn profile URL (full URL, e.g., https://www.linkedin.com/in/username)

            Please return the results as a JSON object with this exact structure:
            {{
              "company": "{company_name}",
              "location": "{location}",
              "ceo": {{
                "name": "Full Name",
                "title": "Job Title",
                "linkedin": "https://www.linkedin.com/in/username"
              }},
              "cto": {{
                "name": "Full Name",
                "title": "Job Title",
                "linkedin": "https://www.linkedin.com/in/username"
              }},
              "cfo": {{
                "name": "Full Name",
                "title": "Job Title",
                "linkedin": "https://www.linkedin.com/in/username"
              }},
              "hr": [
                {{
                  "name": "Full Name",
                  "title": "Job Title",
                  "linkedin": "https://www.linkedin.com/in/username"
                }}
              ],
              "recruiters": [
                {{
                  "name": "Full Name",
                  "title": "Job Title",
                  "linkedin": "https://www.linkedin.com/in/username"
                }}
              ]
            }}

            If you cannot find a specific role, set that field to null. For HR and recruiters, return an array (can be empty).
            Return ONLY valid JSON, no additional text or markdown formatting."""

    try:
        response = model.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Extract JSON from response
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        else:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
        
        # Parse JSON
        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse JSON from Grok response",
                "raw_content": content[:500]
            }
    except Exception as e:
        return {
            "error": f"Error querying Grok: {str(e)}"
        }
