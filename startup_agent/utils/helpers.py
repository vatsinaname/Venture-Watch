import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import datetime
import re

from startup_agent.config import DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_latest_data_file(prefix: str = "funding_data_", suffix: str = ".json") -> Optional[Path]:
    """
    Get the most recent data file with the given prefix and suffix
    
    Args:
        prefix: File prefix to match
        suffix: File suffix to match
        
    Returns:
        Path to the most recent file, or None if no matching files exist
    """
    pattern = f"{prefix}*{suffix}"
    data_files = list(DATA_DIR.glob(pattern))
    
    if not data_files:
        return None
        
    # Sort by modification time (most recent first)
    return max(data_files, key=os.path.getmtime)

def load_json_data(file_path: Path) -> List[Dict[str, Any]]:
    """
    Load JSON data from a file
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of dictionaries containing the data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON data from {file_path}: {e}")
        return []

def save_json_data(data: List[Dict[str, Any]], file_path: Path) -> bool:
    """
    Save data to a JSON file
    
    Args:
        data: List of dictionaries to save
        file_path: Path to save the data to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON data to {file_path}: {e}")
        return False

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format a currency amount with the appropriate symbol
    
    Args:
        amount: The amount to format
        currency: The currency code
        
    Returns:
        Formatted currency string
    """
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CNY": "¥",
        "INR": "₹"
    }
    
    symbol = currency_symbols.get(currency, currency + " ")
    
    if currency in ["JPY", "CNY"]:
        # No decimal places for these currencies
        return f"{symbol}{amount:,.0f}"
    else:
        return f"{symbol}{amount:,.2f}"

def get_date_range(days_back: int) -> tuple:
    """
    Get start and end dates for a range of days
    
    Args:
        days_back: Number of days to look back
        
    Returns:
        Tuple of (start_date, end_date) as strings in YYYY-MM-DD format
    """
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days_back)
    
    return (
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )

def load_json_file(filepath):
    """
    Load data from a JSON file.
    
    Args:
        filepath (str or Path): Path to the JSON file
        
    Returns:
        dict or list: The loaded JSON data, or an empty list if the file doesn't exist
    """
    filepath = Path(filepath)
    if not filepath.exists():
        logger.warning(f"File not found: {filepath}")
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded data from {filepath}")
        return data
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {str(e)}")
        return []

def save_json_file(data, filepath):
    """
    Save data to a JSON file.
    
    Args:
        data (dict or list): The data to save
        filepath (str or Path): Path to the JSON file
    """
    filepath = Path(filepath)
    
    # Ensure the directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved data to {filepath}")
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {str(e)}")

def extract_funding_amount(text):
    """
    Extract a funding amount from text.
    
    Args:
        text (str): Text to search for funding amount
        
    Returns:
        float or None: The funding amount in millions, or None if not found
    """
    if not text:
        return None
    
    # Pattern: $X million or $X.Y million
    pattern = r'\$\s*(\d+(?:\.\d+)?)\s*(million|M|billion|B)'
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        amount = float(match.group(1))
        unit = match.group(2).lower()
        
        # Convert to millions
        if unit in ('billion', 'b'):
            amount *= 1000
        
        return amount
    
    return None

def extract_funding_round(text):
    """
    Extract the funding round from text.
    
    Args:
        text (str): Text to search for funding round
        
    Returns:
        str or None: The funding round, or None if not found
    """
    if not text:
        return None
    
    round_patterns = {
        "Seed": r'\bseed\b',
        "Series A": r'\bseries\s*a\b',
        "Series B": r'\bseries\s*b\b',
        "Series C": r'\bseries\s*c\b',
        "Series D": r'\bseries\s*d\b',
        "Series E": r'\bseries\s*e\b'
    }
    
    for round_name, pattern in round_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            return round_name
    
    return None

def format_date(date_str, input_format="%Y-%m-%d", output_format="%B %d, %Y"):
    """
    Format a date string.
    
    Args:
        date_str (str): Date string to format
        input_format (str): Format of the input date string
        output_format (str): Desired output format
        
    Returns:
        str: Formatted date string, or the original string if formatting fails
    """
    if not date_str:
        return ""
    
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except Exception:
        return date_str
    
def clean_text(text):
    """
    Clean text by removing extra whitespace and normalizing line breaks.
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)
    
    return text.strip() 