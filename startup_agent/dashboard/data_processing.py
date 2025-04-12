"""
Data processing functions for the Venture-Watch dashboard
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_startup_data(data_dir):
    """
    Load startup data from JSON files in the data directory
    
    Args:
        data_dir: Path to the data directory
        
    Returns:
        list: List of startup dictionaries
    """
    data_dir = Path(data_dir)
    all_data = []
    
    # Ensure directory exists
    if not data_dir.exists():
        logger.warning(f"Data directory {data_dir} does not exist.")
        return all_data
        
    try:
        # Get all JSON files in the directory
        json_files = list(data_dir.glob("*.json"))
        
        # Load each file
        for file_path in json_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    
                    # Handle both individual records and lists
                    if isinstance(file_data, list):
                        all_data.extend(file_data)
                    else:
                        all_data.append(file_data)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"Error loading {file_path}: {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Error loading startup data: {str(e)}")
    
    # Deduplicate by company name if present
    if all_data:
        unique_data = {}
        for item in all_data:
            company_name = item.get("company_name")
            if company_name:
                # Keep most recent entry
                if company_name not in unique_data or (
                    "discovery_date" in item and 
                    item["discovery_date"] > unique_data[company_name].get("discovery_date", "")
                ):
                    unique_data[company_name] = item
            else:
                # Add items without company name as is
                unique_data[f"unknown_{len(unique_data)}"] = item
        
        all_data = list(unique_data.values())
    
    return all_data

def filter_startups(data, filters):
    """
    Filter startup data based on user selections
    
    Args:
        data: List of startup dictionaries
        filters: Dictionary of filter selections
        
    Returns:
        list: Filtered list of startup dictionaries
    """
    filtered_data = data.copy()
    
    # Filter by industry
    if filters.get("industry") and filters["industry"] != "All":
        filtered_data = [item for item in filtered_data if item.get("industry") == filters["industry"]]
    
    # Filter by funding round
    if filters.get("funding_round") and filters["funding_round"] != "All":
        filtered_data = [item for item in filtered_data if item.get("funding_round") == filters["funding_round"]]
    
    # Filter by time period
    if filters.get("time_period") and filters["time_period"] != "All time":
        days_map = {
            "Last 7 days": 7,
            "Last 30 days": 30,
            "Last 90 days": 90
        }
        if filters["time_period"] in days_map:
            days = days_map[filters["time_period"]]
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            filtered_data = [
                item for item in filtered_data if 
                (item.get("discovery_date") and item["discovery_date"] >= cutoff_date) or
                (item.get("published_date") and item["published_date"] >= cutoff_date)
            ]
    
    # Filter by minimum funding
    if "min_funding" in filters:
        filtered_data = [
            item for item in filtered_data if 
            (
                item.get("funding_amount") and 
                isinstance(item["funding_amount"], (int, float, str)) and
                (
                    # Try to convert string to float if it's a string
                    (isinstance(item["funding_amount"], str) and float(item["funding_amount"]) >= filters["min_funding"]) or
                    # Directly compare if it's already a number
                    (isinstance(item["funding_amount"], (int, float)) and item["funding_amount"] >= filters["min_funding"])
                )
            )
        ]
    
    # Filter by location
    if filters.get("location") and filters["location"] != "All":
        filtered_data = [item for item in filtered_data if item.get("location") == filters["location"]]
    
    return filtered_data

def normalize_startup_data(data):
    """
    Normalize and clean startup data
    
    Args:
        data: List of startup dictionaries
        
    Returns:
        list: Normalized list of startup dictionaries
    """
    normalized_data = []
    
    for item in data:
        normalized_item = item.copy()
        
        # Normalize funding amount
        if "funding_amount" in normalized_item:
            try:
                # Convert string to float if it's a string
                if isinstance(normalized_item["funding_amount"], str):
                    normalized_item["funding_amount"] = float(normalized_item["funding_amount"].replace("$", "").replace("M", ""))
                # Ensure funding is a float
                normalized_item["funding_amount"] = float(normalized_item["funding_amount"])
            except (ValueError, TypeError):
                normalized_item["funding_amount"] = None
        
        # Normalize tech stack
        if "tech_stack" in normalized_item:
            tech_stack = normalized_item["tech_stack"]
            
            # Convert string to list if needed
            if isinstance(tech_stack, str):
                try:
                    # Try to evaluate as literal
                    import ast
                    tech_stack = ast.literal_eval(tech_stack)
                except (ValueError, SyntaxError):
                    # Split by comma if evaluation fails
                    tech_stack = [t.strip() for t in tech_stack.split(",")]
            
            # Ensure it's a list
            if not isinstance(tech_stack, list):
                tech_stack = []
                
            normalized_item["tech_stack"] = tech_stack
        
        normalized_data.append(normalized_item)
    
    return normalized_data 