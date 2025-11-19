import sys
import json
from job_scraper import JobScraper
import time

def test_job_scraping(job_url: str, headless: bool = True):
    print("="*60)
    print("Testing Job Scraping (No API Keys Required)")
    print("="*60)
    print(f"\nJob URL: {job_url}\n")

    
    try:
        scraper = JobScraper(headless=headless)
        
        job_info = scraper.get_job_info(job_url)

        print("Finalizing...")
        time.sleep(2)
        # Display results
        print(" Scraping completed successfully!")
        print("-" * 60)
        print("\nExtracted Job Information:")
        print(f"   Job Title: {job_info.get('job_title', 'N/A')}")
        print(f"   Company: {job_info.get('company_name', 'N/A')}")
        print(f"   Location: {job_info.get('location', 'N/A')}")
        print(f"   Source: {job_info.get('source', 'N/A')}")
        print(f"   URL: {job_info.get('job_url', 'N/A')}")
        print("-" * 60)
        
        # Save to JSON file
        output_file = "job_scraping_test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(job_info, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
        
        # Validate results
        if not job_info.get('job_title'):
            print("\n  Warning: Job title was not extracted.")
        if not job_info.get('company_name'):
            print(" Warning: Company name was not extracted.")
        
        return job_info
        
    except Exception as e:
        print(f"\n Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function to run the test."""
    print("\n Job Scraping Test (LinkedIn/Glassdoor)")
    print("="*60)
    print("This test only requires Playwright - no API keys needed!\n")
    
    # Get job URL
    if len(sys.argv) > 1:
        job_url = sys.argv[1].strip()
    else:
        job_url = input("Paste job URL (LinkedIn or Glassdoor): ").strip()
    
    if not job_url:
        print("No URL provided. Exiting.")
        return
    
    # Check if headless mode should be disabled
    headless = True
    if "--visible" in sys.argv or "-v" in sys.argv:
        headless = False
        print("Running browser in visible mode (not headless)\n")
    
    # Run test

    result = test_job_scraping(job_url, headless=headless)

    if result:
        print("\n Test completed successfully!")
        print("   You can now use this job information for further processing.")
    else:
        print("\n Test failed. Please check:")
        print("   1. The URL is valid and accessible")
        print("   2. Playwright is installed: playwright install chromium")
        print("   3. You have internet connection")


if __name__ == "__main__":
    main()

