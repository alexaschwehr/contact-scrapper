"""
Main entry point for testing the recruiter finder tool.
"""
import os
import json
import sys
from dotenv import load_dotenv
from agent import RecruiterFinderAgent

load_dotenv()



def print_results(result: dict):
    """Pretty print the recruiter search results."""
    print("\n" + "="*60)
    print("RECRUITER SEARCH RESULTS")
    print("="*60)
    
    if "error" in result:
        print(f"\n❌ Error: {result.get('error')}")
        if "error_message" in result:
            print(f"   Details: {result['error_message']}")
        if "parse_error" in result:
            print(f"   Parse Error: {result['parse_error']}")
        if "raw_content" in result:
            print(f"\n   Raw Content (first 500 chars):\n   {result['raw_content']}")
        return
    
    # Display job information
    print(f"\n📋 Job Information:")
    print(f"   Company: {result.get('company', 'N/A')}")
    print(f"   Job Title: {result.get('job_title', 'N/A')}")
    print(f"   Source: {result.get('source', 'N/A')}")
    print(f"   URL: {result.get('job_url', 'N/A')}")
    
    # Display recruiters
    recruiters = result.get('recruiters', [])
    if not recruiters:
        print(f"\n⚠️  No recruiters found for this company.")
        return
    
    print(f"\n👥 Found {len(recruiters)} Recruiter(s):")
    print("-" * 60)
    
    for i, recruiter in enumerate(recruiters, 1):
        print(f"\n{i}. {recruiter.get('name', 'Unknown')}")
        print(f"   Title: {recruiter.get('title', 'N/A')}")
        email = recruiter.get('email')
        if email:
            print(f"   📧 Email: {email}")
        else:
            print(f"   📧 Email: Not available")
        linkedin = recruiter.get('linkedin')
        if linkedin:
            print(f"   🔗 LinkedIn: {linkedin}")
        else:
            print(f"   🔗 LinkedIn: Not available")
    
    print("\n" + "="*60)


def main():
    """Main function to run the recruiter finder."""
    print("🔍 LinkedIn/Glassdoor/ZipRecruiter Recruiter Finder")
    print("="*60)
    
    # Get job URL
    if len(sys.argv) > 1:
        job_url = sys.argv[1].strip()
    else:
        job_url = input("\nPaste job URL (LinkedIn / Glassdoor / ZipRecruiter): ").strip()

    if not job_url:
        print("❌ No URL provided. Exiting.")
        return

    print(f"\n🔎 Processing job URL: {job_url}")
    print("⏳ This may take a moment...\n")

    try:
        # Initialize agent and find recruiters
        agent = RecruiterFinderAgent()
        result = agent.find_recruiters_for_job(job_url)
        
        # Display results
        print_results(result)
        
        # Optionally save to JSON file
        output_file = "recruiter_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to: {output_file}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
