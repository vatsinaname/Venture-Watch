"""
Data loading and processing utilities for the Venture-Watch dashboard
"""

import json
import os
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

def load_startup_data(data_dir=None):
    """
    Load startup data from JSON files
    
    Args:
        data_dir: Directory containing startup data files
        
    Returns:
        list: List of startup dictionaries
    """
    if data_dir is None:
        # Use default data directory from parent directory structure
        data_dir = Path(__file__).parents[2] / "data"
    
    # Make sure data directory exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        return []
    
    all_data = []
    
    # List all JSON files in data directory
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    
    for filename in json_files:
        try:
            with open(os.path.join(data_dir, filename), 'r') as f:
                file_data = json.load(f)
                
                # If file contains a list, extend our data
                if isinstance(file_data, list):
                    all_data.extend(file_data)
                # If file contains a single object, append it
                elif isinstance(file_data, dict):
                    all_data.append(file_data)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    
    # Fill in missing fields and standardize data
    standardized_data = standardize_data(all_data)
    
    return standardized_data

def standardize_data(data):
    """
    Fill in missing fields and standardize data format
    
    Args:
        data: List of startup dictionaries
        
    Returns:
        list: List of standardized startup dictionaries
    """
    standardized = []
    
    for item in data:
        # Create a copy of the item
        std_item = item.copy()
        
        # Ensure required fields exist
        std_item["company_name"] = item.get("company_name", "Unknown")
        std_item["description"] = item.get("description", "No description available")
        std_item["industry"] = item.get("industry", "Other")
        std_item["funding_amount"] = item.get("funding_amount", 0)
        std_item["funding_round"] = item.get("funding_round", "Unknown")
        std_item["location"] = item.get("location", "Unknown")
        std_item["company_url"] = item.get("company_url", "")
        std_item["tech_stack"] = item.get("tech_stack", [])
        
        # Handle discovery date
        if "discovery_date" not in item:
            std_item["discovery_date"] = datetime.now().strftime("%Y-%m-%d")
        
        # Standardize funding amount (ensure it's a float)
        if isinstance(std_item["funding_amount"], str):
            try:
                # Remove $ and M indicators
                clean_amount = std_item["funding_amount"].replace("$", "").replace("M", "")
                std_item["funding_amount"] = float(clean_amount)
            except (ValueError, AttributeError):
                std_item["funding_amount"] = 0.0
        
        standardized.append(std_item)
    
    return standardized

def filter_startups(data, industry=None, funding_round=None, time_period=None, min_funding=None, location=None):
    """
    Filter startup data based on criteria
    
    Args:
        data: List of startup dictionaries
        industry: Industry to filter by
        funding_round: Funding round to filter by
        time_period: Time period to filter by (days)
        min_funding: Minimum funding amount
        location: Location to filter by
        
    Returns:
        list: Filtered list of startup dictionaries
    """
    filtered_data = data.copy()
    
    # Filter by industry
    if industry and industry != "All":
        filtered_data = [item for item in filtered_data if item.get("industry") == industry]
    
    # Filter by funding round
    if funding_round and funding_round != "All":
        filtered_data = [item for item in filtered_data if item.get("funding_round") == funding_round]
    
    # Filter by minimum funding
    if min_funding is not None:
        filtered_data = [item for item in filtered_data if item.get("funding_amount", 0) >= min_funding]
    
    # Filter by location
    if location and location != "All":
        filtered_data = [item for item in filtered_data if item.get("location") == location]
    
    # Filter by time period
    if time_period:
        cutoff_date = datetime.now() - timedelta(days=time_period)
        cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
        
        filtered_data = [
            item for item in filtered_data 
            if "discovery_date" in item and item["discovery_date"] >= cutoff_date_str
        ]
    
    return filtered_data

def get_unique_values(data, field):
    """
    Get unique values for a specific field in the data
    
    Args:
        data: List of startup dictionaries
        field: Field to get unique values for
        
    Returns:
        list: List of unique values
    """
    values = set()
    
    for item in data:
        value = item.get(field)
        if value:
            values.add(value)
    
    return sorted(list(values)) 