"""
Filter components and handling for the Venture-Watch dashboard
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

def get_available_filters(df):
    """
    Get available filter values from DataFrame
    
    Args:
        df: DataFrame of startup data
        
    Returns:
        dict: Dictionary of available filter values
    """
    available_filters = {
        "industries": sorted(df["industry"].dropna().unique().tolist()),
        "rounds": sorted(df["funding_round"].dropna().unique().tolist()),
        "locations": sorted(df["location"].dropna().unique().tolist()),
    }
    
    return available_filters

def create_filter_components(available_filters):
    """
    Create filter components based on available filter values
    
    Args:
        available_filters: Dictionary containing available filter values
        
    Returns:
        dict: Dictionary of filter components
    """
    industries = available_filters.get("industries", [])
    rounds = available_filters.get("rounds", [])
    locations = available_filters.get("locations", [])
    
    # Industry filter
    industry_filter = dbc.Card([
        dbc.CardHeader("Industry"),
        dbc.CardBody([
            dcc.Dropdown(
                id="industry-filter",
                options=[{"label": industry, "value": industry} for industry in industries],
                multi=True,
                placeholder="Select industries...",
                className="filter-dropdown"
            )
        ])
    ], className="filter-card mb-3")
    
    # Funding round filter
    round_filter = dbc.Card([
        dbc.CardHeader("Funding Round"),
        dbc.CardBody([
            dcc.Dropdown(
                id="round-filter",
                options=[{"label": round_name, "value": round_name} for round_name in rounds],
                multi=True,
                placeholder="Select funding rounds...",
                className="filter-dropdown"
            )
        ])
    ], className="filter-card mb-3")
    
    # Location filter
    location_filter = dbc.Card([
        dbc.CardHeader("Location"),
        dbc.CardBody([
            dcc.Dropdown(
                id="location-filter",
                options=[{"label": location, "value": location} for location in locations],
                multi=True,
                placeholder="Select locations...",
                className="filter-dropdown"
            )
        ])
    ], className="filter-card mb-3")
    
    # Time period filter
    time_period_filter = dbc.Card([
        dbc.CardHeader("Time Period"),
        dbc.CardBody([
            dcc.DatePickerRange(
                id="date-filter",
                start_date=None,
                end_date=None,
                display_format="MMM DD, YYYY",
                className="date-filter"
            )
        ])
    ], className="filter-card mb-3")
    
    # Funding range filter
    funding_range_filter = dbc.Card([
        dbc.CardHeader("Funding Amount (M$)"),
        dbc.CardBody([
            dcc.RangeSlider(
                id="funding-filter",
                min=0,
                max=100,
                step=5,
                marks={i: f"${i}M" for i in range(0, 101, 20)},
                value=[0, 100],
                className="funding-slider"
            )
        ])
    ], className="filter-card mb-3")
    
    # Reset filters button
    reset_button = dbc.Button(
        "Reset Filters",
        id="reset-button",
        color="secondary",
        className="w-100 mb-3"
    )
    
    filter_components = {
        "industry_filter": industry_filter,
        "round_filter": round_filter,
        "location_filter": location_filter,
        "time_period_filter": time_period_filter,
        "funding_range_filter": funding_range_filter,
        "reset_button": reset_button
    }
    
    return filter_components

def create_filter_sidebar(df):
    """
    Create the filter sidebar with all filter components
    
    Args:
        df: DataFrame of startup data
        
    Returns:
        html.Div: Filter sidebar component
    """
    # Get available filters from DataFrame
    available_filters = get_available_filters(df)
    
    # Create filter components
    filter_components = create_filter_components(available_filters)
    
    sidebar = html.Div([
        html.H4("Filters", className="filter-heading"),
        filter_components["industry_filter"],
        filter_components["round_filter"],
        filter_components["location_filter"],
        filter_components["time_period_filter"],
        filter_components["funding_range_filter"],
        filter_components["reset_button"]
    ], className="filter-sidebar")
    
    return sidebar 