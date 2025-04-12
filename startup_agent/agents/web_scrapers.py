import os
import re
import logging
import requests
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from random import uniform

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# User agent for requests
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

def get_random_user_agent():
    """Return a random user agent to avoid being blocked"""
    return USER_AGENTS[int(uniform(0, len(USER_AGENTS)))]

def safe_request(url: str, max_retries: int = 3, backoff_factor: float = 0.5) -> Optional[requests.Response]:
    """Make a request with retry logic and random user agent rotation"""
    headers = {'User-Agent': get_random_user_agent()}
    
    for i in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                # Add a small delay to be respectful
                time.sleep(uniform(1, 3))
                return response
            elif response.status_code == 429:  # Too Many Requests
                logger.warning(f"Rate limited on {url}. Backing off...")
                time.sleep(backoff_factor * (2 ** i))
            else:
                logger.warning(f"Request failed with status code {response.status_code} for {url}")
                return None
        except requests.RequestException as e:
            logger.warning(f"Request error for {url}: {str(e)}")
            if i < max_retries - 1:
                time.sleep(backoff_factor * (2 ** i))
    
    return None

def ninja_techcrunch_dance(days_back: int = 7) -> List[Dict[str, Any]]:
    """
    Dance with TechCrunch ninjas for startup funding news
    
    Args:
        days_back: Number of days to look back
        
    Returns:
        List of startup funding data dictionaries
    """
    logger.info("Doing the TechCrunch ninja dance for startup funding news")
    
    base_url = "https://techcrunch.com/category/venture/"
    results = []
    
    response = safe_request(base_url)
    if not response:
        logger.error("Failed to fetch TechCrunch venture page")
        return results
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for article cards/links
    articles = soup.select('article')
    logger.info(f"Found {len(articles)} articles on TechCrunch venture page")
    
    for article in articles:
        try:
            # Extract article URL
            article_link = article.select_one('a[href*="techcrunch.com"]')
            if not article_link:
                continue
                
            article_url = article_link.get('href')
            
            # Check if it's a funding article
            title_elem = article.select_one('h2, h3, h4')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            
            # Only process articles that look like funding news
            funding_keywords = ['raise', 'raises', 'raised', 'funding', 'investment', 'million', 'billion', 'seed', 'series']
            if not any(keyword in title.lower() for keyword in funding_keywords):
                continue
            
            # Extract date if available
            date_elem = article.select_one('time')
            article_date = None
            if date_elem:
                date_str = date_elem.get('datetime', '')
                if date_str:
                    try:
                        article_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        # Skip if article is older than days_back
                        if article_date < datetime.now() - timedelta(days=days_back):
                            continue
                    except ValueError:
                        pass
            
            # Fetch and parse the full article
            article_response = safe_request(article_url)
            if not article_response:
                continue
                
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            
            # Extract article content
            article_content = article_soup.select_one('article')
            if not article_content:
                continue
                
            text_content = article_content.get_text()
            
            # Extract funding info using regex
            funding_info = extract_funding_info(text_content, title)
            
            if funding_info and funding_info.get('company_name') and funding_info.get('funding_amount'):
                funding_info['url'] = article_url
                funding_info['title'] = title
                funding_info['source'] = 'TechCrunch'
                funding_info['published_date'] = article_date.strftime('%Y-%m-%d') if article_date else datetime.now().strftime('%Y-%m-%d')
                funding_info['discovery_date'] = datetime.now().strftime('%Y-%m-%d')
                results.append(funding_info)
                logger.info(f"Extracted funding info for {funding_info.get('company_name')}")
        
        except Exception as e:
            logger.error(f"Error processing TechCrunch article: {str(e)}")
    
    logger.info(f"Found {len(results)} funding announcements on TechCrunch")
    return results

def squirrel_venturebeat_feast(days_back: int = 7) -> List[Dict[str, Any]]:
    """
    Send squirrels to VentureBeat to feast on startup funding news
    
    Args:
        days_back: Number of days to look back
        
    Returns:
        List of startup funding data dictionaries
    """
    logger.info("Releasing squirrels on VentureBeat for startup funding news")
    
    base_url = "https://venturebeat.com/category/venture/"
    results = []
    
    response = safe_request(base_url)
    if not response:
        logger.error("Failed to fetch VentureBeat page")
        return results
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for article cards
    articles = soup.select('article')
    logger.info(f"Found {len(articles)} articles on VentureBeat page")
    
    for article in articles:
        try:
            # Extract article URL
            article_link = article.select_one('a[href*="venturebeat.com"]')
            if not article_link:
                continue
                
            article_url = article_link.get('href')
            
            # Check if it's a funding article
            title_elem = article.select_one('h2, h3')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            
            # Only process articles that look like funding news
            funding_keywords = ['raise', 'raises', 'raised', 'funding', 'investment', 'million', 'billion', 'seed', 'series']
            if not any(keyword in title.lower() for keyword in funding_keywords):
                continue
            
            # Fetch and parse the full article
            article_response = safe_request(article_url)
            if not article_response:
                continue
                
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            
            # Extract article content
            article_content = article_soup.select_one('article')
            if not article_content:
                continue
                
            text_content = article_content.get_text()
            
            # Extract funding info using regex
            funding_info = extract_funding_info(text_content, title)
            
            if funding_info and funding_info.get('company_name') and funding_info.get('funding_amount'):
                funding_info['url'] = article_url
                funding_info['title'] = title
                funding_info['source'] = 'VentureBeat'
                funding_info['published_date'] = datetime.now().strftime('%Y-%m-%d')
                funding_info['discovery_date'] = datetime.now().strftime('%Y-%m-%d')
                results.append(funding_info)
                logger.info(f"Extracted funding info for {funding_info.get('company_name')}")
        
        except Exception as e:
            logger.error(f"Error processing VentureBeat article: {str(e)}")
    
    logger.info(f"Found {len(results)} funding announcements on VentureBeat")
    return results

def extract_funding_info(text_content: str, title: str = None) -> Dict[str, Any]:
    """
    Extract funding information from article text using advanced regex patterns
    
    Args:
        text_content: The full article text content
        title: The article title (optional)
        
    Returns:
        Dictionary with extracted funding information
    """
    info = {}
    
    # Extract company name from title (if provided)
    if title:
        company_name = None
        
        # Common patterns in funding headlines
        if "announces" in title.lower() and "funding" in title.lower():
            company_name = title.split("announces")[0].strip()
        elif " raises " in title.lower():
            company_name = title.split(" raises ")[0].strip()
        elif " secures " in title.lower() and "funding" in title.lower():
            company_name = title.split(" secures ")[0].strip()
        elif " gets " in title.lower() and "funding" in title.lower():
            company_name = title.split(" gets ")[0].strip()
        elif " closes " in title.lower() and ("round" in title.lower() or "funding" in title.lower()):
            company_name = title.split(" closes ")[0].strip()
        
        # Clean up company name - remove common prefixes like "Exclusive:"
        if company_name:
            prefixes_to_remove = ["Exclusive:", "Breaking:", "Just in:"]
            for prefix in prefixes_to_remove:
                if company_name.startswith(prefix):
                    company_name = company_name[len(prefix):].strip()
            
            info["company_name"] = company_name
    
    # Extract funding amount (look for dollar amounts with more varied patterns)
    funding_patterns = [
        r'\$\s?(\d+(?:\.\d+)?)\s?(?:million|M)',
        r'\$\s?(\d+(?:\.\d+)?)\s?(?:billion|B)',
        r'raised\s?\$\s?(\d+(?:\.\d+)?)\s?(?:million|M)',
        r'raised\s?\$\s?(\d+(?:\.\d+)?)\s?(?:billion|B)',
        r'secured\s?\$\s?(\d+(?:\.\d+)?)\s?(?:million|M)',
        r'secured\s?\$\s?(\d+(?:\.\d+)?)\s?(?:billion|B)',
        r'(\d+(?:\.\d+)?)\s?(?:million|M)\s?(?:dollars|USD|\$)',
        r'(\d+(?:\.\d+)?)\s?(?:billion|B)\s?(?:dollars|USD|\$)'
    ]
    
    for pattern in funding_patterns:
        match = re.search(pattern, text_content, re.IGNORECASE)
        if match:
            amount = float(match.group(1))
            # Convert to millions if in billions
            if "billion" in pattern.lower() or "b" in pattern.lower():
                amount *= 1000
            info["funding_amount"] = amount
            break
    
    # Extract funding round with more comprehensive patterns
    round_patterns = {
        "Seed": [r'seed\s?(?:round|funding)', r'seed\s?investment', r'seed\s?capital'],
        "Series A": [r'series\s?a', r'series\s?a\s?round', r'series\s?a\s?funding'],
        "Series B": [r'series\s?b', r'series\s?b\s?round', r'series\s?b\s?funding'],
        "Series C": [r'series\s?c', r'series\s?c\s?round', r'series\s?c\s?funding'],
        "Series D": [r'series\s?d', r'series\s?d\s?round', r'series\s?d\s?funding'],
        "Pre-seed": [r'pre-?seed', r'pre-?seed\s?round', r'pre-?seed\s?funding'],
        "Angel": [r'angel\s?(?:round|funding|investment)', r'angel\s?investor']
    }
    
    for round_name, patterns in round_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_content, re.IGNORECASE):
                info["funding_round"] = round_name
                break
        if "funding_round" in info:
            break
    
    # Extract industry with expanded keywords
    industries = {
        "AI": ["artificial intelligence", "machine learning", "AI", "deep learning", "neural networks", "NLP", "computer vision"],
        "Fintech": ["fintech", "financial technology", "banking", "finance", "payments", "insurance tech", "insurtech", "regtech"],
        "Healthcare": ["healthcare", "health tech", "medical", "biotech", "healthtech", "life sciences", "pharma", "telemedicine"],
        "Cybersecurity": ["cybersecurity", "security", "infosec", "data protection", "encryption", "cyber defense"],
        "EdTech": ["education technology", "edtech", "learning platform", "e-learning", "online education"],
        "Cloud": ["cloud computing", "saas", "platform as a service", "paas", "iaas", "cloud infrastructure", "cloud services"],
        "E-commerce": ["e-commerce", "ecommerce", "online retail", "d2c", "direct-to-consumer", "retail tech"],
        "Mobile": ["mobile app", "smartphone", "ios", "android", "mobile technology", "mobile platform"],
        "Web3": ["web3", "blockchain", "crypto", "nft", "defi", "decentralized", "token", "cryptocurrency"],
        "Enterprise": ["enterprise software", "b2b", "business software", "enterprise solution"],
        "Clean Tech": ["clean tech", "cleantech", "clean energy", "renewable", "sustainability", "climate tech"],
        "Gaming": ["gaming", "video games", "game development", "esports"],
        "Robotics": ["robotics", "automation", "robots", "autonomous systems"]
    }
    
    for industry, keywords in industries.items():
        for keyword in keywords:
            if keyword.lower() in text_content.lower():
                info["industry"] = industry
                break
        if "industry" in info:
            break
    
    # Extract location with more comprehensive patterns
    location_patterns = [
        r'(?:based in|headquartered in|located in)\s([A-Za-z\s,]+)',
        r'([A-Za-z]+(?:,\s*[A-Za-z]+)?(?:-based))',
        r'from\s([A-Za-z]+(?:,\s*[A-Za-z]+)?)'
    ]
    
    for pattern in location_patterns:
        location_match = re.search(pattern, text_content, re.IGNORECASE)
        if location_match:
            location = location_match.group(1).strip()
            # Clean up location
            if location.endswith('-based'):
                location = location[:-6]
            info["location"] = location
            break
    
    # Extract investors list
    investor_section = None
    investor_keywords = [
        r'led by ([^\.]+)',
        r'investors include ([^\.]+)',
        r'round was led by ([^\.]+)',
        r'funding was led by ([^\.]+)',
        r'investment from ([^\.]+)',
        r'with participation from ([^\.]+)'
    ]
    
    for pattern in investor_keywords:
        match = re.search(pattern, text_content, re.IGNORECASE)
        if match:
            investor_section = match.group(1)
            break
    
    if investor_section:
        # Split by common separators
        investors = re.split(r',|and', investor_section)
        # Clean up each investor name
        cleaned_investors = [inv.strip() for inv in investors if len(inv.strip()) > 0]
        if cleaned_investors:
            info["investors"] = cleaned_investors
    
    return info

def data_disco_crunchbase(days_back: int = 7) -> List[Dict[str, Any]]:
    """
    Do the data disco dance with Crunchbase substitute to find funding news
    
    Args:
        days_back: Number of days to look back
        
    Returns:
        List of startup funding data dictionaries
    """
    logger.info("Dancing the data disco with Crunchbase substitute")
    
    # Currently scraping from public deal announcements lists
    # This is just an example and should be updated with real targets
    target_url = "https://news.crunchbase.com/venture/"
    results = []
    
    response = safe_request(target_url)
    if not response:
        logger.error("Failed to fetch Crunchbase news page")
        return results
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract deal announcements (specific implementation depends on site structure)
    # This is a simplified example
    articles = soup.select('article')
    logger.info(f"Found {len(articles)} articles on Crunchbase news page")
    
    for article in articles:
        try:
            # Extract article link
            link_elem = article.select_one('a')
            if not link_elem or not link_elem.get('href'):
                continue
                
            article_url = link_elem['href']
            if not article_url.startswith('http'):
                article_url = 'https://news.crunchbase.com' + article_url
            
            # Extract title
            title_elem = article.select_one('h2, h3')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            
            # Only process relevant articles
            funding_keywords = ['funding', 'raises', 'million', 'investment', 'capital', 'series']
            if not any(keyword in title.lower() for keyword in funding_keywords):
                continue
            
            # Process the individual article
            article_response = safe_request(article_url)
            if not article_response:
                continue
                
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            text_content = article_soup.get_text()
            
            funding_info = extract_funding_info(text_content, title)
            
            if funding_info and funding_info.get('company_name') and funding_info.get('funding_amount'):
                funding_info['url'] = article_url
                funding_info['title'] = title
                funding_info['source'] = 'Crunchbase News'
                funding_info['published_date'] = datetime.now().strftime('%Y-%m-%d')
                funding_info['discovery_date'] = datetime.now().strftime('%Y-%m-%d')
                results.append(funding_info)
                logger.info(f"Extracted funding info for {funding_info.get('company_name')}")
            
        except Exception as e:
            logger.error(f"Error processing Crunchbase news article: {str(e)}")
    
    logger.info(f"Found {len(results)} funding announcements from Crunchbase news")
    return results

def unleash_the_dancing_ninjas(days_back: int = 7) -> List[Dict[str, Any]]:
    """
    Send out all the dancing ninjas and squirrels to gather startup funding data
    
    Args:
        days_back: Number of days to look back
        
    Returns:
        Combined list of startup funding data dictionaries
    """
    logger.info(f"Unleashing all the dancing ninjas and data squirrels to gather startup data from past {days_back} days!")
    
    all_results = []
    
    # Run TechCrunch ninja dance
    techcrunch_results = ninja_techcrunch_dance(days_back)
    all_results.extend(techcrunch_results)
    
    # Run VentureBeat squirrel feast
    venturebeat_results = squirrel_venturebeat_feast(days_back)
    all_results.extend(venturebeat_results)
    
    # Run Crunchbase data disco
    crunchbase_results = data_disco_crunchbase(days_back)
    all_results.extend(crunchbase_results)
    
    logger.info(f"Ninja-squirrel team collected a total of {len(all_results)} funding announcements!")
    return all_results

# Alias for compatibility with existing code
run_all_scrapers = unleash_the_dancing_ninjas 