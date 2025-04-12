"""
Data processing functions for the Venture-Watch dashboard
"""

from datetime import datetime, timedelta

def apply_filters(startup_data, filters):
    """
    Apply filters to the startup data
    
    Args:
        startup_data: List of startup dictionaries
        filters: Dictionary of filter criteria
        
    Returns:
        Filtered list of startup dictionaries
    """
    if not startup_data:
        return []
        
    filtered_data = startup_data.copy()
    
    # Extract filter criteria
    industry = filters.get("industry")
    funding_round = filters.get("round")
    time_period = filters.get("time_period")
    min_funding = filters.get("min_funding", 0)
    location = filters.get("location")
    
    # Apply industry filter
    if industry:
        filtered_data = [item for item in filtered_data if item.get("industry") == industry]
    
    # Apply funding round filter
    if funding_round:
        filtered_data = [item for item in filtered_data if item.get("funding_round") == funding_round]
    
    # Apply minimum funding filter
    if min_funding > 0:
        filtered_data = [item for item in filtered_data if item.get("funding_amount") and float(item.get("funding_amount", 0)) >= min_funding]
    
    # Apply location filter
    if location:
        filtered_data = [item for item in filtered_data if item.get("location") and location in item.get("location")]
    
    # Apply time period filter
    if time_period and time_period != "All time":
        # Extract days from time period string
        days = 7  # Default to 7 days
        if "30" in time_period:
            days = 30
        elif "90" in time_period:
            days = 90
            
        # Calculate cutoff date
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Filter by discovery date or published date
        filtered_data = [
            item for item in filtered_data 
            if (item.get("discovery_date") and item.get("discovery_date") >= cutoff_date) or 
               (item.get("published_date") and item.get("published_date") >= cutoff_date)
        ]
    
    return filtered_data

def get_date_range(data):
    """
    Get the minimum and maximum dates from the startup data
    
    Args:
        data: List of startup dictionaries
        
    Returns:
        Tuple of (min_date, max_date) as datetime objects
    """
    if not data:
        # Default to last 90 days if no data
        today = datetime.now().date()
        return (today - timedelta(days=90), today)
    
    dates = []
    
    # Extract dates from discovery_date and published_date fields
    for item in data:
        if item.get("discovery_date"):
            try:
                date = datetime.strptime(item["discovery_date"], "%Y-%m-%d").date()
                dates.append(date)
            except (ValueError, TypeError):
                pass
                
        if item.get("published_date"):
            try:
                date = datetime.strptime(item["published_date"], "%Y-%m-%d").date()
                dates.append(date)
            except (ValueError, TypeError):
                pass
    
    if not dates:
        # Default to last 90 days if no valid dates found
        today = datetime.now().date()
        return (today - timedelta(days=90), today)
    
    # Return min and max dates
    return (min(dates), max(dates))

def get_unique_values(data, field_name):
    """
    Get unique values for a specific field from the data
    
    Args:
        data: List of startup dictionaries
        field_name: The field to extract unique values from
        
    Returns:
        List of unique values for the specified field
    """
    if not data:
        return []
    
    # Extract values from the specified field
    values = []
    for item in data:
        value = item.get(field_name)
        if value and value not in values:
            values.append(value)
    
    # Sort values for consistent display
    return sorted(values)

def get_funding_range(data):
    """
    Get the minimum and maximum funding amounts from the data
    
    Args:
        data: List of startup dictionaries
        
    Returns:
        Tuple of (min_funding, max_funding) in millions
    """
    if not data:
        return (0, 100)  # Default range if no data
    
    # Extract funding amounts
    amounts = []
    for item in data:
        amount = item.get("funding_amount")
        if amount:
            try:
                amount = float(amount)
                amounts.append(amount)
            except (ValueError, TypeError):
                pass
    
    if not amounts:
        return (0, 100)  # Default range if no valid amounts
    
    # Return min and max amounts, ensuring min is at least 0
    return (max(0, min(amounts)), max(amounts))

def normalize_company_data(data):
    """
    Normalize and clean company data to ensure consistent formats
    
    Args:
        data: List of company data dictionaries
        
    Returns:
        Normalized list of company dictionaries
    """
    if not data:
        return []
    
    normalized_data = []
    
    for company in data:
        normalized_company = company.copy()
        
        # Ensure company_name exists
        if "name" in normalized_company and "company_name" not in normalized_company:
            normalized_company["company_name"] = normalized_company["name"]
        
        # Ensure funding_amount is float
        if "funding_amount" in normalized_company:
            try:
                normalized_company["funding_amount"] = float(normalized_company["funding_amount"])
            except (ValueError, TypeError):
                # If conversion fails, default to 0
                normalized_company["funding_amount"] = 0.0
        
        # Ensure discovery_date exists
        if "discovery_date" not in normalized_company and "date_funded" in normalized_company:
            normalized_company["discovery_date"] = normalized_company["date_funded"]
        elif "discovery_date" not in normalized_company:
            normalized_company["discovery_date"] = datetime.now().strftime("%Y-%m-%d")
        
        # Ensure tech_stack is a list
        if "tech_stack" in normalized_company:
            if isinstance(normalized_company["tech_stack"], str):
                try:
                    # Try to evaluate it as a literal
                    import ast
                    normalized_company["tech_stack"] = ast.literal_eval(normalized_company["tech_stack"])
                except (ValueError, SyntaxError):
                    # If evaluation fails, split by comma
                    normalized_company["tech_stack"] = [t.strip() for t in normalized_company["tech_stack"].split(",")]
        
        normalized_data.append(normalized_company)
    
    return normalized_data

def merge_data_sources(primary_data, secondary_data, key_field="company_name"):
    """
    Merge data from different sources, prioritizing primary data
    
    Args:
        primary_data: Primary list of company dictionaries
        secondary_data: Secondary list of company dictionaries to merge in
        key_field: Field to use as key for matching records
        
    Returns:
        Merged list of company dictionaries
    """
    if not primary_data:
        return secondary_data
    
    if not secondary_data:
        return primary_data
    
    # Create a dictionary of primary data keyed by company_name
    primary_dict = {company.get(key_field, "").lower(): company for company in primary_data if company.get(key_field)}
    
    # Merge in secondary data
    for company in secondary_data:
        key = company.get(key_field, "").lower()
        if key and key in primary_dict:
            # Update primary data with non-null values from secondary
            for field, value in company.items():
                if value and field not in primary_dict[key]:
                    primary_dict[key][field] = value
        elif key:
            # Add new company to merged data
            primary_dict[key] = company
    
    return list(primary_dict.values()) 