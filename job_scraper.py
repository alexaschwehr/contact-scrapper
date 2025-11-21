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
        page.wait_for_timeout(3000)  # Give more time for dynamic content
        print("Scraping glassdoor job...")
        job_title = ""
        company_name = ""
        location = ""

        # Try multiple selectors for job title
        try:
            job_title = page.locator("heading_Heading__aomVx heading_Level1__w42c9").first.text_content() or ""
        except Exception:
            try:
                job_title = page.locator("h1[data-test='jobTitle']").first.text_content() or ""
            except Exception:
                try:
                    job_title = page.locator("[data-test='jobTitle']").first.text_content() or ""
                except Exception:
                    pass

        # Try multiple selectors for company name
        try:
            company_name = (
                page.locator("div.EmployerProfile_employerNameHeading__bXBYr").first.text_content()
            )
        except Exception:
            try:
                company_name = (
                    page.locator("div:has-text('Company') >> .. >> a").first.text_content()
                )
            except Exception:
                try:
                    company_name = (
                        page.locator("a[data-test='employerName']").first.text_content()
                    )
                except Exception:
                    try:
                        # Fallback: look for any link near "Company" text
                        company_name = (
                            page.locator("text=Company >> .. >> a").first.text_content()
                        )
                    except Exception:
                        pass

        # Try multiple selectors for location
        try:
            location = (
                page.locator("div[data-test='location']").first.text_content()
            )
        except Exception:
            try:
                location = (
                    page.locator("span[data-test='location']").first.text_content()
                )
            except Exception:
                try:
                    location = (
                        page.locator("div:has-text('Location') >> .. >> span").first.text_content()
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
        page.wait_for_timeout(3000)  # Give more time for dynamic content
        print("Scraping ziprecruiter job...")
        job_title = ""
        company_name = ""
        location = ""

        # Try multiple selectors for job title
        try:
            job_title = page.locator("h1").first.text_content() or ""
        except Exception:
            try:
                job_title = page.locator("h1.job_title").first.text_content() or ""
            except Exception:
                try:
                    job_title = page.locator("[class*='job-title']").first.text_content() or ""
                except Exception:
                    pass

        # Try multiple selectors for company name
        try:
            company_name = (
                page.locator("a[class*='job-company']").first.text_content()
            )
        except Exception:
            try:
                company_name = (
                    page.locator("a[class*='company']").first.text_content()
                )
            except Exception:
                try:
                    company_name = (
                        page.locator("div[class*='company'] a").first.text_content()
                    )
                except Exception:
                    try:
                        # Look for company link near job details
                        company_name = (
                            page.locator("div.job_company a").first.text_content()
                        )
                    except Exception:
                        pass

        # Try multiple selectors for location
        try:
            location = (
                page.locator("span[class*='location']").first.text_content()
            )
        except Exception:
            try:
                location = (
                    page.locator("div[class*='location']").first.text_content()
                )
            except Exception:
                try:
                    location = (
                        page.locator("[class*='job-location']").first.text_content()
                    )
                except Exception:
                    try:
                        location = (
                            page.locator("span.job_location").first.text_content()
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

        # Try up to 2 times with different strategies
        for attempt in range(2):
            try:
                with sync_playwright() as p:
                    print("Attempting to scrape job...")
                    browser: Browser = p.chromium.launch(headless=self.headless)
                    context: BrowserContext = browser.new_context(
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        viewport={"width": 1920, "height": 1080}
                    )
                    page: Page = context.new_page()
                    
                    # Try different wait strategies based on attempt
                    wait_strategy = "load" if attempt == 0 else "domcontentloaded"
                    timeout = 60000 if attempt == 0 else 30000
                    
                    try:
                        print(f"Loading page (attempt {attempt + 1})...")
                        page.goto(job_url, wait_until=wait_strategy, timeout=timeout)
                        print("Page loaded, waiting for content...")
                        page.wait_for_timeout(3000)  # Give page time to render dynamic content
                    except Exception as e:
                        print(f"  Warning: Page load issue: {str(e)}")
                        # Try to continue anyway - page might have loaded partially
                        try:
                            page.wait_for_timeout(5000)  # Wait a bit longer
                        except:
                            pass

                    try:
                        if "linkedin.com" in hostname:
                            info = self._scrape_linkedin_job(page)
                        elif "glassdoor.com" in hostname:
                            info = self._scrape_glassdoor_job(page)
                        elif "ziprecruiter.com" in hostname:
                            info = self._scrape_ziprecruiter_job(page)
                        else:
                            info = self._scrape_generic_job(page, hostname)
                    except Exception as e:
                        print(f" Error during scraping: {str(e)}")
                        # Return minimal info instead of failing completely
                        info = {
                            "job_title": "",
                            "company_name": "",
                            "location": "",
                            "source": hostname.replace(".com", ""),
                        }

                    browser.close()
                    
                    # If we got any data, return it
                    if info.get("job_title") or info.get("company_name"):
                        info["job_url"] = job_url
                        return info
                    elif attempt == 0:
                        # Try again with different strategy
                        print(" No data extracted, retrying with different strategy...")
                        break  # Exit context manager and retry
                    else:
                        # Return what we have
                        info["job_url"] = job_url
                        return info
                        
            except Exception as e:
                print(f" Attempt {attempt + 1} failed: {str(e)}")
                if attempt == 1:
                    # Last attempt failed, return minimal info
                    return {
                        "job_title": "",
                        "company_name": "",
                        "location": "",
                        "source": hostname.replace(".com", ""),
                        "job_url": job_url,
                    }
                # Try again
                continue
        
        # Fallback if all attempts failed
        return {
            "job_title": "",
            "company_name": "",
            "location": "",
            "source": hostname.replace(".com", ""),
            "job_url": job_url,
        }


# Backward compatibility function
def get_job_info(job_url: str) -> Dict[str, Any]:
    scraper = JobScraper()
    return scraper.get_job_info(job_url)
