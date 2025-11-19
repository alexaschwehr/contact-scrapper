import os
import requests
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

load_dotenv()


class ScrapinError(Exception):
    pass


class ScrapinClient:
    BASE_URL = "https://api.scrapin.io/v1"
    
    # Keywords to identify recruiter/HR roles
    RECRUITER_KEYWORDS = [
        "recruiter",
        "talent",
        "hr",
        "human resources",
        "people ops",
        "people operations",
        "talent acquisition",
        "technical recruiter",
        "people partner",
        "hiring",
        "recruitment",
        "staffing",
        "sourcer",
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SCRAPIN_API_KEY")
        if not self.api_key:
            raise ScrapinError("SCRAPIN_API_KEY is not set in environment.")
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "X-API-KEY": self.api_key,
        }
    
    def _is_recruiter_title(self, title: str) -> bool:
        if not title:
            return False
        t = title.lower()
        return any(keyword in t for keyword in self.RECRUITER_KEYWORDS)
    
    def _extract_person_data(self, person: Dict[str, Any]) -> Dict[str, Any]:
        first_name = (
            person.get('firstName') 
            or person.get('first_name') 
            or person.get('firstname') 
            or ""
        )
        last_name = (
            person.get('lastName') 
            or person.get('last_name') 
            or person.get('lastname') 
            or ""
        )
        name = f"{first_name} {last_name}".strip()

        if not name:
            name = person.get("name") or person.get("fullName") or ""
        
        # Extract title
        title = (
            person.get("headline") 
            or person.get("title") 
            or person.get("jobTitle") 
            or person.get("position") 
            or ""
        )

        email = (
            person.get("email") 
            or person.get("workEmail") 
            or person.get("work_email")
            or person.get("primaryEmail")
            or person.get("contactEmail")
            or None
        )

        linkedin_url = (
            person.get("linkedInUrl") 
            or person.get("linkedin_url")
            or person.get("linkedin")
            or person.get("socialUrl")
            or person.get("profileUrl")
            or None
        )
        
        return {
            "name": name or "Unknown",
            "title": title or "Unknown",
            "email": email,
            "linkedin": linkedin_url,
        }
    
    def search_recruiters_for_company(
        self,
        company_name: str,
        job_title: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:

        if not company_name:
            return []

        endpoint = f"{self.BASE_URL}/person/search"
        
        # Build search parameters
        params = {
            "company": company_name,
            "limit": limit,
        }
        
        # Add job title to search if provided
        if job_title:
            params["title"] = job_title

        try:
            resp = requests.get(
                endpoint, 
                headers=self._get_headers(), 
                params=params, 
                timeout=60
            )
            
            if not resp.ok:
                endpoint_alt = f"{self.BASE_URL}/persons/search"
                resp = requests.get(
                    endpoint_alt, 
                    headers=self._get_headers(), 
                    params=params, 
                    timeout=60
                )
                
                if not resp.ok:
                    raise ScrapinError(
                        f"Scrapin API error: {resp.status_code} - {resp.text}"
                    )

            data = resp.json()

            persons = (
                data.get("data") 
                or data.get("persons") 
                or data.get("results") 
                or data.get("items") 
                or []
            )
            
            # If the response is a list directly
            if isinstance(data, list):
                persons = data

            candidates: List[Dict[str, Any]] = []
            for person in persons:
                person_data = self._extract_person_data(person)
                
                # Filter for recruiter/HR roles
                if person_data["title"] and not self._is_recruiter_title(person_data["title"]):
                    continue

                candidates.append(person_data)

            return candidates
            
        except requests.exceptions.RequestException as e:
            raise ScrapinError(f"Network error calling Scrapin API: {str(e)}")
        except Exception as e:
            raise ScrapinError(f"Error processing Scrapin API response: {str(e)}")


# Backward compatibility function
def search_recruiters_for_company(
    company_name: str,
    job_title: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    client = ScrapinClient()
    return client.search_recruiters_for_company(company_name, job_title, limit)
