import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import datetime

from startup_agent.config import DATA_DIR

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