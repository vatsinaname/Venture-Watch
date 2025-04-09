import json
import datetime
from pathlib import Path
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from startup_agent.config import CRUNCHBASE_API_KEY, DATA_DIR, DAYS_TO_LOOK_BACK

class StartupCollector:
    """
    Agent 1: Startup Intelligence Collector
    Collects recent funding data from Crunchbase API
    """
    
    def __init__(self):
        self.api_key = CRUNCHBASE_API_KEY
        self.base_url = "https://api.crunchbase.com/api/v4"
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_recent_funding_rounds(self, days_back=DAYS_TO_LOOK_BACK):
        """
        Get startups that received funding in the last X days
        """
        if not self.api_key:
            print("Error: CRUNCHBASE_API_KEY is not set in the environment variables")
            return []
            
        # Calculate date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days_back)
        
        # Format dates for API
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Prepare request
        endpoint = f"{self.base_url}/searches/funding_rounds"
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        
        # Query for recent funding rounds
        data = {
            "field_ids": [
                "identifier",
                "entity_id", 
                "entity_identifier",
                "announced_on",
                "investment_type",
                "money_raised",
                "money_raised_currency_code",
                "lead_investor_identifiers"
            ],
            "order": [
                {
                    "field_id": "announced_on",
                    "sort": "desc"
                }
            ],
            "query": [
                {
                    "field_id": "announced_on",
                    "operator_id": "between",
                    "values": [start_date_str, end_date_str]
                }
            ],
            "limit": 50
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=data,
                params={"user_key": self.api_key}
            )
            response.raise_for_status()
            
            # Process results
            results = response.json().get("entities", [])
            return self._process_funding_data(results)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching funding data: {e}")
            return []
    
    def _process_funding_data(self, funding_rounds):
        """Process raw funding data into a structured format"""
        processed_data = []
        
        for round_data in funding_rounds:
            properties = round_data.get("properties", {})
            
            # Get company identifier
            entity_identifier = properties.get("entity_identifier", {}).get("value", "")
            
            # Skip if we don't have a company identifier
            if not entity_identifier:
                continue
                
            # Get company details
            company_data = self._get_organization_details(entity_identifier)
            
            # Skip if we couldn't get company details
            if not company_data:
                continue
                
            # Structure the data
            funding_info = {
                "company_name": company_data.get("name", "Unknown"),
                "description": company_data.get("description", ""),
                "website": company_data.get("website", ""),
                "location": company_data.get("location", ""),
                "funding_date": properties.get("announced_on", {}).get("value", ""),
                "funding_amount": properties.get("money_raised", {}).get("value", 0),
                "funding_currency": properties.get("money_raised_currency_code", {}).get("value", "USD"),
                "funding_round": properties.get("investment_type", {}).get("value", ""),
                "categories": company_data.get("categories", []),
                "company_size": company_data.get("company_size", ""),
                "founded_year": company_data.get("founded_year", ""),
            }
            
            processed_data.append(funding_info)
            
        return processed_data
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _get_organization_details(self, identifier):
        """Get detailed information about an organization"""
        if not self.api_key:
            return {}
            
        endpoint = f"{self.base_url}/entities/organizations/{identifier}"
        headers = {"accept": "application/json"}
        
        try:
            response = requests.get(
                endpoint,
                headers=headers,
                params={"user_key": self.api_key, "card_ids": "fields"}
            )
            response.raise_for_status()
            
            data = response.json()
            properties = data.get("properties", {})
            
            # Extract relevant information
            org_data = {
                "name": properties.get("name", ""),
                "description": properties.get("short_description", ""),
                "website": properties.get("website", {}).get("value", ""),
                "location": self._extract_location(properties),
                "categories": self._extract_categories(properties),
                "company_size": properties.get("num_employees_enum", ""),
                "founded_year": properties.get("founded_on", {}).get("value", {}).get("year", "")
            }
            
            return org_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching organization details for {identifier}: {e}")
            return {}
    
    def _extract_location(self, properties):
        """Extract headquarters location from properties"""
        hq = properties.get("headquarters", [])
        if hq and len(hq) > 0:
            location_data = hq[0].get("value", {})
            country = location_data.get("country", "")
            region = location_data.get("region", "")
            city = location_data.get("city", "")
            
            location_parts = [part for part in [city, region, country] if part]
            return ", ".join(location_parts)
        return ""
    
    def _extract_categories(self, properties):
        """Extract categories from properties"""
        categories = properties.get("categories", [])
        return [cat.get("value", {}).get("name", "") for cat in categories if cat.get("value", {}).get("name")]
    
    def collect_and_save(self):
        """Collect startup data and save to JSON file"""
        print("Collecting recent startup funding data...")
        startup_data = self.get_recent_funding_rounds()
        
        if not startup_data:
            print("No startup funding data found or error occurred")
            return []
            
        # Create timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"funding_data_{timestamp}.json"
        filepath = DATA_DIR / filename
        
        # Save the data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(startup_data, f, indent=2)
            
        print(f"Saved {len(startup_data)} startup records to {filepath}")
        return startup_data


if __name__ == "__main__":
    # Test the agent
    collector = StartupCollector()
    collector.collect_and_save() 