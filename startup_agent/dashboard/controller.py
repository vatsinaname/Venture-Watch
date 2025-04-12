"""
Controller module for dashboard callbacks
"""

import os
from pathlib import Path
import threading
import json
import pandas as pd
from datetime import datetime

def run_data_collection(days_back=7):
    """
    Run data collection in a background thread
    
    Args:
        days_back: Number of days to look back
        
    Returns:
        thread: Background thread running the collection
    """
    def collection_task(days_back):
        try:
            # Import the necessary functions
            from startup_agent.agents.web_scrapers import unleash_the_dancing_ninjas
            
            # Run the collection
            results = unleash_the_dancing_ninjas(
                days_back=days_back,
                verbose=True
            )
            
            # Save a timestamp for the latest collection
            timestamp_file = Path(__file__).parent / "last_collection.txt"
            with open(timestamp_file, "w") as f:
                f.write(datetime.now().isoformat())
            
            return results
            
        except Exception as e:
            print(f"Error in collection task: {e}")
            return []
    
    # Start collection in a background thread
    thread = threading.Thread(
        target=collection_task,
        args=(days_back,),
        daemon=True
    )
    thread.start()
    
    return thread

def get_last_collection_time():
    """
    Get the timestamp of the last data collection
    
    Returns:
        str: Formatted timestamp or "Never" if not available
    """
    timestamp_file = Path(__file__).parent / "last_collection.txt"
    
    if not timestamp_file.exists():
        return "Never"
    
    try:
        with open(timestamp_file, "r") as f:
            timestamp = f.read().strip()
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return "Unknown"

def filter_startup_data(df, filters):
    """
    Apply filters to the startup data
    
    Args:
        df: DataFrame of startup data
        filters: Dictionary of filter criteria
        
    Returns:
        DataFrame: Filtered data
    """
    if df.empty:
        return df
    
    filtered_df = df.copy()
    
    # Apply industry filter
    if 'industry' in filters and filters['industry']:
        if isinstance(filters['industry'], list):
            if filters['industry']:  # Only filter if the list is not empty
                filtered_df = filtered_df[filtered_df['industry'].isin(filters['industry'])]
        else:
            filtered_df = filtered_df[filtered_df['industry'] == filters['industry']]
    
    # Apply round filter
    if 'funding_round' in filters and filters['funding_round']:
        if isinstance(filters['funding_round'], list):
            if filters['funding_round']:  # Only filter if the list is not empty
                filtered_df = filtered_df[filtered_df['funding_round'].isin(filters['funding_round'])]
        else:
            filtered_df = filtered_df[filtered_df['funding_round'] == filters['funding_round']]
    
    # Apply location filter
    if 'location' in filters and filters['location']:
        if isinstance(filters['location'], list):
            if filters['location']:  # Only filter if the list is not empty
                filtered_df = filtered_df[filtered_df['location'].isin(filters['location'])]
        else:
            filtered_df = filtered_df[filtered_df['location'] == filters['location']]
    
    # Apply date filter
    if 'start_date' in filters and 'end_date' in filters:
        start_date = pd.to_datetime(filters['start_date'])
        end_date = pd.to_datetime(filters['end_date'])
        
        # Ensure the date column exists
        if 'date' in filtered_df.columns:
            filtered_df['date'] = pd.to_datetime(filtered_df['date'])
            filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]
    
    # Apply funding range filter
    if 'min_funding' in filters and 'max_funding' in filters:
        min_funding = filters['min_funding']
        max_funding = filters['max_funding']
        
        filtered_df = filtered_df[(filtered_df['funding_amount'] >= min_funding) & 
                                (filtered_df['funding_amount'] <= max_funding)]
    
    return filtered_df

def calculate_dashboard_metrics(df):
    """
    Calculate key metrics for the dashboard
    
    Args:
        df: DataFrame of startup data
        
    Returns:
        dict: Dictionary of metrics
    """
    if df.empty:
        return {
            'total_startups': 0,
            'total_funding': 0,
            'avg_funding': 0,
            'top_industry': 'N/A',
            'top_round': 'N/A',
            'recent_startups': 0
        }
    
    # Calculate metrics
    total_startups = len(df)
    total_funding = df['funding_amount'].sum()
    avg_funding = df['funding_amount'].mean()
    
    # Get top industry
    industry_counts = df['industry'].value_counts()
    top_industry = industry_counts.index[0] if not industry_counts.empty else 'N/A'
    
    # Get top funding round
    round_counts = df['funding_round'].value_counts()
    top_round = round_counts.index[0] if not round_counts.empty else 'N/A'
    
    # Count recent startups (within last 7 days)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        recent_startups = len(df[df['date'] >= (pd.Timestamp.now() - pd.Timedelta(days=7))])
    else:
        recent_startups = 0
    
    return {
        'total_startups': total_startups,
        'total_funding': round(total_funding, 2),
        'avg_funding': round(avg_funding, 2),
        'top_industry': top_industry,
        'top_round': top_round,
        'recent_startups': recent_startups
    }

def get_startup_details(company_name):
    """
    Get detailed information about a specific startup
    
    Args:
        company_name: Name of the company
        
    Returns:
        dict: Startup details
    """
    from startup_agent.dashboard.data import load_startup_data
    
    # Load all startup data
    startups = load_startup_data()
    
    # Find the specific startup
    startup = None
    for s in startups:
        if s.get('company_name', '').lower() == company_name.lower():
            startup = s
            break
    
    return startup 