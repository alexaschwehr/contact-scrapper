from typing import Dict, Any
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import time

class JobScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
    
    def _scrape_linkedin_job(self, page: Page) -> Dict[str, Any]:
        page.wait_for_timeout(2000)

        job_title = ""
        company_name = ""
        location = ""

        try:
            job_title = page.locator("h1").first.text_content() or ""
            print("Getting job info...")
            time.sleep(4)
        except Exception:
            pass

        try:
            company_name = (
                page.locator("a[href*='/company/']").first.text_content() or ""
            )
            print("Scraping linkedin job...")
            time.sleep(3)
        except Exception:
            pass

        try:
            location = (
                page.locator("span:has-text('location')").first.text_content()
            )
            print("Getting Xpath...")
            time.sleep(2)
        except Exception:
            try: #topcard__flavor topcard__flavor--bullet
                location = (
                    page.locator("span[class*='main-job-card__location']")
                    .first.text_content()
                )
            except Exception:
                location = ""

        return {
            "job_title": job_title.strip(),
            "company_name": company_name.strip(),
            "location": (location or "").strip(),
            "source": "linkedin",
        }

    def _scrape_glassdoor_job(self, page: Page) -> Dict[str, Any]:
        page.wait_for_timeout(2000)

        job_title = ""
        company_name = ""
        location = ""

        try:
            job_title = page.locator("h1").first.text_content() or ""
        except Exception:
            pass

        try:
            company_name = (
                page.locator("div:has-text('Company') >> .. >> a").first.text_content()
            )
        except Exception:
            try:
                company_name = (
                    page.locator("div[data-test='employerName']").first.text_content()
                )
            except Exception:
                pass

        try:
            location = (
                page.locator("div[data-test='location']").first.text_content()
            )
        except Exception:
            location = ""

        return {
            "job_title": job_title.strip(),
            "company_name": company_name.strip(),
            "location": (location or "").strip(),
            "source": "glassdoor",
        }

    def _scrape_ziprecruiter_job(self, page: Page) -> Dict[str, Any]:
        page.wait_for_timeout(2000)

        job_title = ""
        company_name = ""
        location = ""

        try:
            job_title = page.locator("h1").first.text_content() or ""
        except Exception:
            pass

        try:
            company_name = (
                page.locator("a[class*='job-company']").first.text_content()
            )
        except Exception:
            pass

        try:
            location = (
                page.locator("span[class*='location']").first.text_content()
            )
        except Exception:
            location = ""

        return {
            "job_title": job_title.strip(),
            "company_name": company_name.strip(),
            "location": (location or "").strip(),
            "source": "ziprecruiter",
        }

    def _scrape_generic_job(self, page: Page, hostname: str) -> Dict[str, Any]:
        page.wait_for_timeout(2000)
        title = page.locator("h1").first.text_content() or ""
        return {
            "job_title": title.strip(),
            "company_name": "",
            "location": "",
            "source": hostname,
        }

    def get_job_info(self, job_url: str) -> Dict[str, Any]:
        parsed = urlparse(job_url)
        hostname = parsed.hostname or ""

        with sync_playwright() as p:
            print("Attempting to scrape linkedin job...")
            time.sleep(4)
            print("Scraping linkedin job...")
            time.sleep(4)
            browser: Browser = p.chromium.launch(headless=self.headless)
            context: BrowserContext = browser.new_context()
            page: Page = context.new_page()
            page.goto(job_url, wait_until="networkidle")

            if "linkedin.com" in hostname:
                info = self._scrape_linkedin_job(page)
            elif "glassdoor" in hostname:
                info = self._scrape_glassdoor_job(page)
            elif "ziprecruiter" in hostname:
                info = self._scrape_ziprecruiter_job(page)
            else:
                info = self._scrape_generic_job(page, hostname)

            browser.close()

        info["job_url"] = job_url
        return info


# Backward compatibility function
def get_job_info(job_url: str) -> Dict[str, Any]:
    scraper = JobScraper()
    return scraper.get_job_info(job_url)
