import os
import json
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

SALESQL_API_BASE_URL = "https://api-public.salesql.com/v1/persons/enrich/"
SALESQL_API_KEY_ENV = "SALESQL_API_KEY"


class SalesQLEnricher:
    def __init__(self, api_key: Optional[str] = None, enabled: bool = True):

        self.api_key = api_key or os.getenv(SALESQL_API_KEY_ENV)
        self.enabled = enabled and bool(self.api_key)
        
        if enabled and not self.api_key:
            print("    Warning: SalesQL API key not found. Email enrichment will be disabled.")
            print(f"   Set {SALESQL_API_KEY_ENV} in your .env file to enable email enrichment.")
    
    def enrich_person(self, linkedin_url: str) -> Dict[str, Any]:

        if not self.enabled:
            return {
                "error": "Email enrichment is disabled or API key not available"
            }
        
        if not linkedin_url:
            return {
                "error": "LinkedIn URL is required"
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "accept": "application/json"
            }
            
            params = {
                "linkedin_url": linkedin_url,
                "match_if_direct_email": "true",
                "match_if_direct_phone": "true"
            }
            
            # SalesQL API endpoint
            response = requests.get(
                SALESQL_API_BASE_URL,
                headers=headers,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "error": f"SalesQL API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "error": f"Unexpected error during enrichment: {str(e)}"
            }
    
    def extract_email_from_response(self, enrichment_data: Dict[str, Any]) -> Optional[str]:
        if "error" in enrichment_data:
            return None

        if "email" in enrichment_data:
            email = enrichment_data["email"]
            if isinstance(email, str) and email.strip():
                return email.strip()
        
        # Try 'emails' field (list of emails)
        if "emails" in enrichment_data:
            emails = enrichment_data["emails"]
            if isinstance(emails, list) and len(emails) > 0:
                # Get the first email (usually the primary one)
                first_email = emails[0]
                if isinstance(first_email, dict):
                    # If it's a dict, look for 'email' or 'address' key
                    email = first_email.get("email") or first_email.get("address")
                    if email and isinstance(email, str) and email.strip():
                        return email.strip()
                elif isinstance(first_email, str) and first_email.strip():
                    return first_email.strip()
        
        # Try nested data structure (some APIs return data in a 'data' or 'person' field)
        if "data" in enrichment_data:
            return self.extract_email_from_response(enrichment_data["data"])
        
        if "person" in enrichment_data:
            return self.extract_email_from_response(enrichment_data["person"])
        
        return None
    
    def enrich_profiles_from_json(
        self, 
        input_json_path: str, 
        output_json_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:

        if not self.enabled:
            print("  Email enrichment is disabled. Skipping...")
            return []
        
        # Read input JSON
        try:
            with open(input_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f" Error: File not found: {input_json_path}")
            return []
        except json.JSONDecodeError as e:
            print(f" Error: Invalid JSON in {input_json_path}: {str(e)}")
            return []
        
        # Process each entry
        enriched_results = []
        
        for entry in data:
            if "error" in entry:
                # Skip error entries
                continue
            
            company = entry.get("company", "Unknown")
            enriched_entry = {
                "company": company,
                "profiles": []
            }
            
            # Process CEO
            if entry.get("ceo") and entry["ceo"].get("linkedin"):
                email = self._enrich_single_profile(
                    entry["ceo"]["name"],
                    entry["ceo"]["title"],
                    entry["ceo"]["linkedin"],
                    company
                )
                if email:
                    enriched_entry["profiles"].append(email)
            
            # Process CTO
            if entry.get("cto") and entry["cto"].get("linkedin"):
                email = self._enrich_single_profile(
                    entry["cto"]["name"],
                    entry["cto"]["title"],
                    entry["cto"]["linkedin"],
                    company
                )
                if email:
                    enriched_entry["profiles"].append(email)
            
            # Process CFO
            if entry.get("cfo") and entry["cfo"].get("linkedin"):
                email = self._enrich_single_profile(
                    entry["cfo"]["name"],
                    entry["cfo"]["title"],
                    entry["cfo"]["linkedin"],
                    company
                )
                if email:
                    enriched_entry["profiles"].append(email)
            
            # Process HR
            for hr in entry.get("hr", []):
                if hr.get("linkedin"):
                    email = self._enrich_single_profile(
                        hr["name"],
                        hr["title"],
                        hr["linkedin"],
                        company
                    )
                    if email:
                        enriched_entry["profiles"].append(email)
            
            # Process Recruiters
            for recruiter in entry.get("recruiters", []):
                if recruiter.get("linkedin"):
                    email = self._enrich_single_profile(
                        recruiter["name"],
                        recruiter["title"],
                        recruiter["linkedin"],
                        company
                    )
                    if email:
                        enriched_entry["profiles"].append(email)
            
            if enriched_entry["profiles"]:
                enriched_results.append(enriched_entry)
        
        # Save results
        if output_json_path is None:
            # Generate output filename based on input filename
            base_name = os.path.splitext(os.path.basename(input_json_path))[0]
            output_json_path = f"{base_name}_enriched_emails.json"
        
        try:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(enriched_results, f, indent=2, ensure_ascii=False)
            print(f" Enriched profiles saved to: {output_json_path}")
        except Exception as e:
            print(f"  Warning: Could not save enriched results: {str(e)}")
        
        return enriched_results
    
    def _enrich_single_profile(
        self, 
        name: str, 
        title: str, 
        linkedin_url: str, 
        company: str
    ) -> Optional[Dict[str, Any]]:
        print(f"🔍 Enriching: {name} ({title}) at {company}...")
        
        enrichment_data = self.enrich_person(linkedin_url)
        email = self.extract_email_from_response(enrichment_data)
        
        if email:
            print(f"   ✅ Found email: {email}")
            return {
                "name": name,
                "title": title,
                "company": company,
                "linkedin": linkedin_url,
                "email": email
            }
        else:
            print(f"   ⚠️  Email not found")
            if "error" in enrichment_data:
                print(f"      Error: {enrichment_data['error']}")
            return None


def enrich_executive_profiles(
    input_json_path: str = "executive_profiles_results.json",
    output_json_path: Optional[str] = None,
    enabled: bool = True,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:

    enricher = SalesQLEnricher(api_key=api_key, enabled=enabled)
    return enricher.enrich_profiles_from_json(input_json_path, output_json_path)


if __name__ == "__main__":
    import sys
    
    input_file = sys.argv[1] if len(sys.argv) > 1 else "executive_profiles_results.json"
    enabled = os.getenv("SALESQL_ENABLED", "true").lower() == "true"
    
    print(" SalesQL Email Enrichment")
    print("=" * 60)
    
    results = enrich_executive_profiles(
        input_json_path=input_file,
        enabled=enabled
    )
    
    print(f"\n Enrichment complete. Found emails for {sum(len(r['profiles']) for r in results)} profiles.")

