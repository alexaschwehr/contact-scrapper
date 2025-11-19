from typing import Dict, Any, List
from langchain_core.tools import tool
from job_scraper import JobScraper
from scrapein import ScrapinClient


_job_scraper = JobScraper()
_scrapin_client = None  # Will be initialized lazily


def _get_scrapin_client() -> ScrapinClient:
    global _scrapin_client
    if _scrapin_client is None:
        try:
            _scrapin_client = ScrapinClient()
        except Exception:
            pass
    return _scrapin_client


@tool
def get_job_info_tool(job_url: str) -> Dict[str, Any]:
    return _job_scraper.get_job_info(job_url)


@tool
def find_recruiter_candidates_tool(
    company_name: str,
    job_title: str = "",
) -> List[Dict[str, Any]]:
    try:
        client = _get_scrapin_client()
        if client is None:
            return []
        return client.search_recruiters_for_company(
            company_name, 
            job_title or None, 
            limit=10
        )
    except Exception:
        return []
