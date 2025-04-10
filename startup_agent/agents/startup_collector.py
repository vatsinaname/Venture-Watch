import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import requests
from dotenv import load_dotenv
import gnews
from bs4 import BeautifulSoup
from googleapiclient.discovery import build

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load configuration
from startup_agent.config import DATA_DIR

class StartupCollector:
    """
    Agent responsible for collecting startup funding data using Google News API
    and Google Custom Search API.
    """
    
    def __init__(self):
        """Initialize the StartupCollector with API configurations."""
        load_dotenv()
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        self.data_dir = DATA_DIR
        self.output_file = self.data_dir / "funding_data.json"
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"StartupCollector initialized. Data will be saved to {self.output_file}")
    
    def collect_from_google_news(self, days=7):
        """
        Collect startup funding news from Google News API.
        
        Args:
            days (int): Number of days to look back for news
            
        Returns:
            list: List of startup funding news items
        """
        logger.info(f"Collecting funding news from the past {days} days")
        
        # Create a Google News client
        google_news = gnews.GNews()
        
        # Set the time period
        google_news.period = f"{days}d"
        
        # Search terms for startup funding
        search_terms = [
            "startup funding announced",
            "startup raises series",
            "seed funding announced",
            "venture capital investment",
            "startup secures funding"
        ]
        
        all_results = []
        
        for term in search_terms:
            try:
                # Get news results
                news_results = google_news.get_news(term)
                logger.info(f"Found {len(news_results)} results for '{term}'")
                
                # Process each news item
                for item in news_results:
                    # Extract additional information from the article
                    article_info = self._extract_article_info(item["url"])
                    
                    if article_info and article_info.get("funding_amount"):
                        news_item = {
                            "title": item["title"],
                            "url": item["url"],
                            "published_date": item["published date"],
                            "description": item["description"],
                            "source": item["publisher"]["title"],
                            "funding_amount": article_info.get("funding_amount"),
                            "funding_round": article_info.get("funding_round"),
                            "company_name": article_info.get("company_name"),
                            "industry": article_info.get("industry"),
                            "location": article_info.get("location"),
                            "investors": article_info.get("investors", [])
                        }
                        all_results.append(news_item)
            
            except Exception as e:
                logger.error(f"Error collecting news for term '{term}': {str(e)}")
        
        return all_results
    
    def collect_from_custom_search(self):
        """
        Collect startup funding information using Google Custom Search API.
        
        Returns:
            list: List of startup funding details
        """
        logger.info("Collecting startup funding data from Google Custom Search")
        
        if not self.google_api_key or not self.google_cse_id:
            logger.warning("Google API key or CSE ID not provided. Skipping custom search.")
            return []
            
        # Create a service client for the Google Custom Search API
        service = build("customsearch", "v1", developerKey=self.google_api_key)
        
        # Search terms
        search_terms = [
            "startup funding announcement",
            "series A funding",
            "series B funding",
            "seed funding startup",
            "venture capital investment"
        ]
        
        all_results = []
        
        for term in search_terms:
            try:
                # Execute the search
                result = service.cse().list(
                    q=term,
                    cx=self.google_cse_id,
                    num=10  # Number of results per query
                ).execute()
                
                # Process search results
                if "items" in result:
                    logger.info(f"Found {len(result['items'])} results for '{term}'")
                    
                    for item in result["items"]:
                        # Extract details from search result
                        search_data = {
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                            "source": item.get("displayLink", "")
                        }
                        
                        # Extract additional information
                        article_info = self._extract_article_info(search_data["url"])
                        
                        if article_info and article_info.get("funding_amount"):
                            search_data.update(article_info)
                            all_results.append(search_data)
            
            except Exception as e:
                logger.error(f"Error in custom search for term '{term}': {str(e)}")
        
        return all_results
    
    def _extract_article_info(self, url):
        """
        Extract startup and funding information from the article URL.
        
        Args:
            url (str): The URL of the article
            
        Returns:
            dict: Extracted information including funding amount, company name, etc.
        """
        try:
            # Fetch the article content
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
                
            # Parse the HTML content
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract text content
            text_content = soup.get_text()
            
            # Extract funding information using simple heuristics
            info = {}
            
            # Extract company name (simple heuristic)
            title = soup.title.string if soup.title else ""
            company_name = None
            
            if title:
                # Try to extract company name from title
                if "announces" in title.lower() and "funding" in title.lower():
                    company_name = title.split("announces")[0].strip()
                elif "raises" in title.lower():
                    company_name = title.split("raises")[0].strip()
                elif "secures" in title.lower() and "funding" in title.lower():
                    company_name = title.split("secures")[0].strip()
            
            if company_name:
                info["company_name"] = company_name
            
            # Extract funding amount (look for dollar amounts)
            import re
            funding_patterns = [
                r'\$\s?(\d+(?:\.\d+)?)\s?(?:million|M)',
                r'\$\s?(\d+(?:\.\d+)?)\s?(?:billion|B)',
                r'raised\s?\$\s?(\d+(?:\.\d+)?)',
                r'secured\s?\$\s?(\d+(?:\.\d+)?)'
            ]
            
            for pattern in funding_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    amount = float(match.group(1))
                    # Convert to millions if in billions
                    if "billion" in pattern or "B" in pattern:
                        amount *= 1000
                    info["funding_amount"] = amount
                    break
            
            # Extract funding round
            round_patterns = {
                "seed": r'seed\s?(?:round|funding)',
                "series a": r'series\s?a',
                "series b": r'series\s?b',
                "series c": r'series\s?c',
                "series d": r'series\s?d'
            }
            
            for round_name, pattern in round_patterns.items():
                if re.search(pattern, text_content, re.IGNORECASE):
                    info["funding_round"] = round_name.title()
                    break
            
            # Extract industry (simple keyword matching)
            industries = {
                "AI": ["artificial intelligence", "machine learning", "AI"],
                "Fintech": ["fintech", "financial technology", "banking", "finance"],
                "Healthcare": ["healthcare", "health tech", "medical", "biotech"],
                "Cybersecurity": ["cybersecurity", "security", "infosec"],
                "EdTech": ["education technology", "edtech", "learning platform"],
                "Cloud": ["cloud computing", "saas", "platform as a service"],
                "E-commerce": ["e-commerce", "ecommerce", "online retail"],
                "Mobile": ["mobile app", "smartphone", "ios", "android"]
            }
            
            for industry, keywords in industries.items():
                for keyword in keywords:
                    if keyword.lower() in text_content.lower():
                        info["industry"] = industry
                        break
                if "industry" in info:
                    break
            
            # Extract location (basic regex for city, state/country patterns)
            location_pattern = r'(?:based in|headquartered in|located in)\s([A-Za-z\s,]+)'
            location_match = re.search(location_pattern, text_content, re.IGNORECASE)
            
            if location_match:
                info["location"] = location_match.group(1).strip()
            
            return info
            
        except Exception as e:
            logger.error(f"Error extracting information from {url}: {str(e)}")
            return None
    
    def deduplicate_results(self, news_results, search_results):
        """
        Deduplicate results from multiple sources based on company name and URL.
        
        Args:
            news_results (list): Results from Google News
            search_results (list): Results from Google Custom Search
            
        Returns:
            list: Deduplicated combined results
        """
        combined_results = news_results + search_results
        
        # Create a dictionary to track unique entries
        unique_entries = {}
        
        for result in combined_results:
            company_name = result.get("company_name")
            url = result.get("url")
            
            # Skip entries without company name
            if not company_name:
                continue
                
            # Create a unique key
            key = f"{company_name}_{url}"
            
            # Only keep the entry with the most complete information
            if key not in unique_entries or len(result.keys()) > len(unique_entries[key].keys()):
                unique_entries[key] = result
        
        return list(unique_entries.values())
    
    def run(self):
        """
        Run the startup collection process.
        
        Returns:
            list: Collected and processed startup funding data
        """
        logger.info("Starting startup data collection")
        
        # Collect data from Google News
        news_results = self.collect_from_google_news()
        logger.info(f"Collected {len(news_results)} results from Google News")
        
        # Collect data from Google Custom Search
        search_results = self.collect_from_custom_search()
        logger.info(f"Collected {len(search_results)} results from Google Custom Search")
        
        # Deduplicate and combine results
        combined_results = self.deduplicate_results(news_results, search_results)
        logger.info(f"After deduplication: {len(combined_results)} unique startup funding events")
        
        # Generate sample data if no results were found (for development/testing)
        if not combined_results:
            logger.warning("No results found. Generating sample data for testing.")
            combined_results = self._generate_sample_data()
        
        # Save the results
        self._save_results(combined_results)
        
        return combined_results
    
    def _save_results(self, results):
        """
        Save the collected results to a JSON file.
        
        Args:
            results (list): The startup funding data to save
        """
        try:
            with open(self.output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Saved {len(results)} startup funding entries to {self.output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
    
    def _generate_sample_data(self):
        """
        Generate sample startup funding data for testing purposes.
        
        Returns:
            list: Sample startup funding data
        """
        return [
            {
                "company_name": "AI Assistant Technologies",
                "funding_amount": 15.5,
                "funding_round": "Series A",
                "industry": "AI",
                "location": "San Francisco, CA",
                "description": "AI-powered virtual assistants for business automation",
                "url": "https://example.com/ai-assistant-funding",
                "published_date": datetime.now().strftime("%Y-%m-%d"),
                "source": "TechCrunch",
                "investors": ["Andreessen Horowitz", "Sequoia Capital"]
            },
            {
                "company_name": "Quantum Cloud Systems",
                "funding_amount": 8.2,
                "funding_round": "Seed",
                "industry": "Cloud",
                "location": "Boston, MA",
                "description": "Quantum computing infrastructure for cloud applications",
                "url": "https://example.com/quantum-cloud-funding",
                "published_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "source": "VentureBeat",
                "investors": ["Y Combinator", "First Round Capital"]
            },
            {
                "company_name": "HealthAI Labs",
                "funding_amount": 22.0,
                "funding_round": "Series B",
                "industry": "Healthcare",
                "location": "Austin, TX",
                "description": "AI diagnostics platform for early disease detection",
                "url": "https://example.com/healthai-funding",
                "published_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                "source": "Forbes",
                "investors": ["Khosla Ventures", "GV"]
            },
            {
                "company_name": "SecureChain",
                "funding_amount": 12.8,
                "funding_round": "Series A",
                "industry": "Cybersecurity",
                "location": "New York, NY",
                "description": "Blockchain-based cybersecurity solutions for enterprises",
                "url": "https://example.com/securechain-funding",
                "published_date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                "source": "Business Insider",
                "investors": ["Accel", "Lightspeed Venture Partners"]
            },
            {
                "company_name": "EcoLogistics",
                "funding_amount": 5.5,
                "funding_round": "Seed",
                "industry": "E-commerce",
                "location": "Seattle, WA",
                "description": "Sustainable last-mile delivery for e-commerce companies",
                "url": "https://example.com/ecologistics-funding",
                "published_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "source": "TechCrunch",
                "investors": ["Founders Fund", "SV Angel"]
            }
        ]

if __name__ == "__main__":
    collector = StartupCollector()
    results = collector.run()
    print(f"Collected {len(results)} startup funding entries") 