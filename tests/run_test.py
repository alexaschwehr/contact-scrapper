
import os
import json
import sys
from dotenv import load_dotenv
from agent import RecruiterFinderAgent

load_dotenv()



def print_results(result: dict):
    """Pretty print the executive profile and recruiter search results."""
    print("\n" + "="*60)
    print("EXECUTIVE PROFILE & RECRUITER SEARCH RESULTS")
    print("="*60)
    
    if "error" in result:
        print(f"\n Error: {result.get('error')}")
        if "error_message" in result:
            print(f"   Details: {result['error_message']}")
        if "parse_error" in result:
            print(f"   Parse Error: {result['parse_error']}")
        if "raw_content" in result:
            print(f"\n   Raw Content (first 500 chars):\n   {result['raw_content']}")
        return
    
    # Display job information
    print(f"\n Job Information:")
    print(f"   Company: {result.get('company', 'N/A')}")
    print(f"   Location: {result.get('location', 'N/A')}")
    print(f"   Job Title: {result.get('job_title', 'N/A')}")
    print(f"   Source: {result.get('source', 'N/A')}")
    print(f"   URL: {result.get('job_url', 'N/A')}")
    
    # Display executives
    print(f"\n Executive Profiles:")
    print("-" * 60)
    
    ceo = result.get('ceo')
    if ceo:
        print(f"\n CEO:")
        print(f"   Name: {ceo.get('name', 'N/A')}")
        print(f"   Title: {ceo.get('title', 'N/A')}")
        linkedin = ceo.get('linkedin')
        if linkedin:
            print(f"   🔗 LinkedIn: {linkedin}")
        else:
            print(f"   🔗 LinkedIn: Not available")
    else:
        print(f"\n CEO: Not found")
    
    cto = result.get('cto')
    if cto:
        print(f"\n CTO:")
        print(f"   Name: {cto.get('name', 'N/A')}")
        print(f"   Title: {cto.get('title', 'N/A')}")
        linkedin = cto.get('linkedin')
        if linkedin:
            print(f"  LinkedIn: {linkedin}")
        else:
            print(f"  LinkedIn: Not available")
    else:
        print(f"\n CTO: Not found")
    
    cfo = result.get('cfo')
    if cfo:
        print(f"\n CFO:")
        print(f"   Name: {cfo.get('name', 'N/A')}")
        print(f"   Title: {cfo.get('title', 'N/A')}")
        linkedin = cfo.get('linkedin')
        if linkedin:
            print(f"  LinkedIn: {linkedin}")
        else:
            print(f"  LinkedIn: Not available")
    else:
        print(f"\n CFO: Not found")
    
    # Display HR
    hr_list = result.get('hr', [])
    if hr_list:
        print(f"\n HR Staff ({len(hr_list)}):")
        print("-" * 60)
        for i, hr in enumerate(hr_list, 1):
            print(f"\n{i}. {hr.get('name', 'Unknown')}")
            print(f"   Title: {hr.get('title', 'N/A')}")
            linkedin = hr.get('linkedin')
            if linkedin:
                print(f"   LinkedIn: {linkedin}")
            else:
                print(f"   LinkedIn: Not available")
    else:
        print(f"\n HR Staff: Not found")
    
    # Display recruiters
    recruiters = result.get('recruiters', [])
    if recruiters:
        print(f"\n Recruiters ({len(recruiters)}):")
        print("-" * 60)
        for i, recruiter in enumerate(recruiters, 1):
            print(f"\n{i}. {recruiter.get('name', 'Unknown')}")
            print(f"   Title: {recruiter.get('title', 'N/A')}")
            email = recruiter.get('email')
            if email:
                print(f"   Email: {email}")
            else:
                print(f"   Email: Not available")
            linkedin = recruiter.get('linkedin')
            if linkedin:
                print(f"   LinkedIn: {linkedin}")
            else:
                print(f"   LinkedIn: Not available")
    else:
        print(f"\n Recruiters: Not found")
    
    print("\n" + "="*60)


def main():
    """Main function to run the recruiter finder."""
    print(" LinkedIn/Glassdoor/ZipRecruiter Recruiter Finder")
    print("="*60)
    
    # Get job URL
    if len(sys.argv) > 1:
        job_url = sys.argv[1].strip()
    else:
        job_url = input("\nPaste job URL (LinkedIn / Glassdoor / ZipRecruiter): ").strip()

    if not job_url:
        print(" No URL provided. Exiting.")
        return

    print(f"\n Processing job URL: {job_url}")
    print(" This may take a moment...\n")

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
        print(f"\n Results saved to: {output_file}")
        
    except KeyboardInterrupt:
        print("\n\n Interrupted by user.")
    except Exception as e:
        print(f"\n Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
