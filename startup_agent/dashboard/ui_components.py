"""
UI components for the Venture-Watch dashboard
"""

import streamlit as st
from datetime import datetime
import pandas as pd

def create_sidebar_filters(data):
    """
    Create sidebar filters for the dashboard
    
    Args:
        data: List of startup dictionaries
        
    Returns:
        dict: Selected filter values
    """
    st.sidebar.header("Filter Startups")
    
    # Extract unique values for filters
    industries = ["All"] + sorted(list(set(item.get("industry", "") for item in data if item.get("industry"))))
    funding_rounds = ["All"] + sorted(list(set(item.get("funding_round", "") for item in data if item.get("funding_round"))))
    locations = ["All"] + sorted(list(set(item.get("location", "") for item in data if item.get("location"))))
    
    # Create filters
    industry = st.sidebar.selectbox("Industry", industries)
    funding_round = st.sidebar.selectbox("Funding Round", funding_rounds)
    time_period = st.sidebar.selectbox("Time Period", ["All time", "Last 7 days", "Last 30 days", "Last 90 days"])
    min_funding = st.sidebar.slider("Minimum Funding (in millions)", 0.0, 100.0, 0.0)
    location = st.sidebar.selectbox("Location", locations)
    
    # Return selected values
    return {
        "industry": industry,
        "funding_round": funding_round,
        "time_period": time_period,
        "min_funding": min_funding,
        "location": location
    }

def create_startup_card(startup):
    """
    Create a card displaying information about a startup
    
    Args:
        startup: Dictionary containing startup information
    """
    # Create card container
    with st.container():
        st.markdown("---")
        
        # Company name and description
        st.markdown(f"### {startup.get('company_name', 'Unknown Company')}")
        if startup.get("description"):
            st.markdown(f"*{startup.get('description')}*")
        
        # Two columns for details
        col1, col2 = st.columns(2)
        
        with col1:
            if startup.get("industry"):
                st.markdown(f"**Industry:** {startup.get('industry')}")
            
            if startup.get("funding_amount"):
                amount = startup.get("funding_amount")
                if isinstance(amount, (int, float)):
                    amount = f"${amount:.1f}M"
                st.markdown(f"**Funding:** {amount}")
            
            if startup.get("funding_round"):
                st.markdown(f"**Round:** {startup.get('funding_round')}")
            
            if startup.get("location"):
                st.markdown(f"**Location:** {startup.get('location')}")
        
        with col2:
            # Display discovery date
            discovery_date = startup.get("discovery_date") or startup.get("published_date")
            if discovery_date:
                try:
                    date_obj = datetime.strptime(discovery_date, "%Y-%m-%d")
                    st.markdown(f"**Discovered:** {date_obj.strftime('%b %d, %Y')}")
                except ValueError:
                    st.markdown(f"**Discovered:** {discovery_date}")
            
            # Display tech stack
            if startup.get("tech_stack") and isinstance(startup.get("tech_stack"), list):
                st.markdown("**Tech Stack:**")
                tech_stack = startup.get("tech_stack")[:5]  # Limit to 5 for display
                for tech in tech_stack:
                    st.markdown(f"- {tech}")
        
        # Display links
        if startup.get("website") or startup.get("article_url"):
            st.markdown("**Links:**")
            cols = st.columns(2)
            
            if startup.get("website"):
                cols[0].markdown(f"[Company Website]({startup.get('website')})")
            
            if startup.get("article_url"):
                cols[1].markdown(f"[Funding Article]({startup.get('article_url')})")

def display_startup_list(filtered_data):
    """
    Display a list of startups as cards
    
    Args:
        filtered_data: List of filtered startup dictionaries
    """
    if not filtered_data:
        st.warning("No startups match the selected filters.")
        return
    
    # Sort by discovery date (newest first)
    sorted_data = sorted(
        filtered_data,
        key=lambda x: x.get("discovery_date", "0000-00-00"),
        reverse=True
    )
    
    # Display count
    st.markdown(f"## Showing {len(sorted_data)} startups")
    
    # Display each startup
    for startup in sorted_data:
        create_startup_card(startup)

def create_header():
    """Create the dashboard header"""
    st.markdown("# 🚀 Venture Watch Dashboard")
    st.markdown("Monitor startup funding and acquisitions")
    st.markdown("---")

def create_dashboard_tabs():
    """Create the main dashboard tabs"""
    return st.tabs(["Startups", "Analytics", "Settings"])

def create_footer():
    """Create the dashboard footer"""
    st.markdown("---")
    st.markdown("© 2023 Venture Watch | Your AI-powered startup intelligence platform") 