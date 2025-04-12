"""
Data loading and processing functions for the Venture-Watch dashboard
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

from startup_agent.config import DATA_DIR

def load_startup_data():
    """
    Load startup data from JSON files in the data directory
    
    Returns:
        list: List of startup dictionaries
    """
    startups = []
    company_names = set()  # Track unique company names to avoid duplicates
    
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Get JSON files in data directory
    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    
    for file in json_files:
        try:
            with open(os.path.join(DATA_DIR, file), "r", encoding="utf-8") as f:
                startup_data = json.load(f)
                
                # Process the data based on file type
                if isinstance(startup_data, list):
                    # File contains a list of startups
                    for startup in startup_data:
                        if isinstance(startup, dict) and "company_name" in startup:
                            # Only add if company name doesn't already exist
                            if startup["company_name"] not in company_names:
                                startups.append(startup)
                                company_names.add(startup["company_name"])
                elif isinstance(startup_data, dict) and "company_name" in startup_data:
                    # File contains a single startup
                    if startup_data["company_name"] not in company_names:
                        startups.append(startup_data)
                        company_names.add(startup_data["company_name"])
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    return startups

def prepare_data_for_dashboard(startups):
    """
    Prepare startup data for dashboard display
    
    Args:
        startups: List of startup dictionaries
        
    Returns:
        tuple: (
            processed_data (list),
            unique_industries (list),
            unique_rounds (list),
            unique_locations (list)
        )
    """
    # Process and clean data
    processed_data = []
    for startup in startups:
        # Skip startups without essential information
        if not all(key in startup for key in ["company_name", "funding_amount"]):
            continue
            
        # Process funding amount (ensure it's a float)
        try:
            funding_amount = float(startup.get("funding_amount", 0))
        except (ValueError, TypeError):
            funding_amount = 0
            
        # Process discovery date
        discovery_date = startup.get("discovery_date")
        if discovery_date:
            try:
                # Try to parse as ISO format
                discovery_date = datetime.fromisoformat(discovery_date.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                discovery_date = datetime.now()
        else:
            discovery_date = datetime.now()
            
        # Create processed startup entry
        processed_startup = {
            "company_name": startup.get("company_name", "Unknown"),
            "funding_amount": funding_amount,
            "funding_round": startup.get("funding_round", "Unknown"),
            "industry": startup.get("industry", "Other"),
            "location": startup.get("location", "Unknown"),
            "description": startup.get("description", ""),
            "website": startup.get("website", ""),
            "discovery_date": discovery_date,
            "investors": startup.get("investors", []),
            "people": startup.get("people", []),
        }
        
        processed_data.append(processed_startup)
    
    # Extract unique values for filters
    unique_industries = list(set(startup["industry"] for startup in processed_data))
    unique_rounds = list(set(startup["funding_round"] for startup in processed_data))
    unique_locations = list(set(startup["location"] for startup in processed_data))
    
    return processed_data, unique_industries, unique_rounds, unique_locations

def filter_startups(startups_df, industry_filter, round_filter, location_filter, time_filter, funding_filter):
    """
    Filter startups based on selected criteria
    
    Args:
        startups_df: Pandas DataFrame of startups
        industry_filter: List of selected industries
        round_filter: List of selected funding rounds
        location_filter: List of selected locations
        time_filter: Selected time period
        funding_filter: Minimum funding amount
        
    Returns:
        pandas.DataFrame: Filtered DataFrame
    """
    filtered_df = startups_df.copy()
    
    # Apply industry filter
    if industry_filter and len(industry_filter) > 0:
        filtered_df = filtered_df[filtered_df["industry"].isin(industry_filter)]
    
    # Apply round filter
    if round_filter and len(round_filter) > 0:
        filtered_df = filtered_df[filtered_df["funding_round"].isin(round_filter)]
    
    # Apply location filter
    if location_filter and len(location_filter) > 0:
        filtered_df = filtered_df[filtered_df["location"].isin(location_filter)]
    
    # Apply time filter
    now = datetime.now()
    if time_filter == "7days":
        filtered_df = filtered_df[filtered_df["discovery_date"] >= (now - timedelta(days=7))]
    elif time_filter == "30days":
        filtered_df = filtered_df[filtered_df["discovery_date"] >= (now - timedelta(days=30))]
    elif time_filter == "90days":
        filtered_df = filtered_df[filtered_df["discovery_date"] >= (now - timedelta(days=90))]
    elif time_filter == "365days":
        filtered_df = filtered_df[filtered_df["discovery_date"] >= (now - timedelta(days=365))]
    
    # Apply funding filter
    filtered_df = filtered_df[filtered_df["funding_amount"] >= funding_filter]
    
    return filtered_df

def convert_to_dataframe(startups):
    """
    Convert startup list to pandas DataFrame
    
    Args:
        startups: List of startup dictionaries
        
    Returns:
        pandas.DataFrame: DataFrame with startups data
    """
    df = pd.DataFrame(startups)
    
    # Ensure funding_amount is numeric
    df["funding_amount"] = pd.to_numeric(df["funding_amount"], errors="coerce").fillna(0)
    
    # Ensure discovery_date is datetime
    if "discovery_date" in df.columns:
        df["discovery_date"] = pd.to_datetime(df["discovery_date"], errors="coerce")
    else:
        df["discovery_date"] = pd.to_datetime("now")
    
    return df 