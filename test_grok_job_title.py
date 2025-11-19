import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def test_grok_job_title_extraction(job_url: str):
    print("="*60)
    print("Testing Grok Plus Job Title Extraction")
    print("="*60)
    print(f"\nJob URL: {job_url}\n")
    
    # Check for API key
    grok_api_key = os.getenv("GROK_API_KEY")
    if not grok_api_key:
        print("Error: GROK_API_KEY is not set in environment.")
        print("   Please add it to your .env file.")
        return False
    
    try:
        # Initialize Grok model
        print("⏳ Initializing Grok Plus model...")
        model = ChatOpenAI(
            model="grok-3",
            temperature=0,
            api_key=grok_api_key,
            base_url="https://api.x.ai/v1",
        )
        
        # Create a prompt to extract job title
        prompt = f"""Please visit this job posting URL and extract the job title.

            URL: {job_url}
            
            Please provide:
            1. The job title
            2. The company name (if available)
            3. A brief confirmation that you can access the page
            
            Format your response clearly."""
        
        print("Sending request to Grok Plus...")
        print("(This may take a moment as Grok processes the URL)\n")
        
        response = model.invoke(prompt)
        
        # Extract content
        content = response.content if hasattr(response, 'content') else str(response)
        
        print("Response from Grok Plus:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        
        # Check if response contains useful information
        if content and len(content) > 10:
            print("\nTest completed successfully!")
            print("   Grok Plus was able to process the URL and return a response.")
            return True
        else:
            print("\n⚠️  Warning: Response seems empty or too short.")
            return False
            
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to run the test."""
    print("\nGrok Plus Job Title Extraction Test\n")
    
    # Get job URL
    if len(sys.argv) > 1:
        job_url = sys.argv[1].strip()
    else:
        job_url = input("Paste job URL to test: ").strip()
    
    if not job_url:
        print("No URL provided. Exiting.")
        return
    
    # Run test
    success = test_grok_job_title_extraction(job_url)
    
    if success:
        print("\nYou can proceed with full testing once you receive your Scrapin API key!")
    else:
        print("\nPlease check your GROK_API_KEY and try again.")


if __name__ == "__main__":
    main()

