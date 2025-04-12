"""
Analytics and visualization functions for the Venture-Watch dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

def convert_to_dataframe(data):
    """
    Convert list of startup dictionaries to pandas DataFrame
    
    Args:
        data: List of startup dictionaries
        
    Returns:
        pd.DataFrame: DataFrame of startup data
    """
    if not data:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Convert funding_amount to float if it's not already
    if 'funding_amount' in df.columns:
        df['funding_amount'] = pd.to_numeric(df['funding_amount'], errors='coerce').fillna(0)
    
    # Convert discovery_date to datetime if it exists
    if 'discovery_date' in df.columns:
        df['discovery_date'] = pd.to_datetime(df['discovery_date'], errors='coerce')
        # Sort by discovery date
        df = df.sort_values('discovery_date')
    
    return df

def funding_over_time(df):
    """
    Create a time series chart of funding amounts
    
    Args:
        df: DataFrame of startup data
        
    Returns:
        plotly.graph_objects.Figure: Time series chart
    """
    if df.empty or 'discovery_date' not in df.columns or 'funding_amount' not in df.columns:
        # Return empty figure if no data
        return go.Figure()
    
    # Group by date and sum funding
    daily_funding = df.groupby(df['discovery_date'].dt.date)['funding_amount'].sum().reset_index()
    daily_funding.columns = ['date', 'funding']
    
    # Calculate cumulative funding
    daily_funding['cumulative_funding'] = daily_funding['funding'].cumsum()
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add daily funding bars
    fig.add_trace(
        go.Bar(
            x=daily_funding['date'],
            y=daily_funding['funding'],
            name="Daily Funding ($M)",
            marker_color='rgb(55, 83, 109)'
        )
    )
    
    # Add cumulative funding line
    fig.add_trace(
        go.Scatter(
            x=daily_funding['date'],
            y=daily_funding['cumulative_funding'],
            name="Cumulative Funding ($M)",
            marker_color='rgb(26, 118, 255)',
            mode='lines+markers'
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Funding Over Time',
        xaxis_title='Date',
        yaxis_title='Funding Amount ($M)',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def funding_by_industry(df):
    """
    Create a bar chart of top industries by funding amount
    
    Args:
        df: DataFrame of startup data
        
    Returns:
        plotly.graph_objects.Figure: Bar chart
    """
    if df.empty or 'industry' not in df.columns or 'funding_amount' not in df.columns:
        # Return empty figure if no data
        return go.Figure()
    
    # Group by industry and sum funding
    industry_funding = df.groupby('industry')['funding_amount'].sum().reset_index()
    industry_funding = industry_funding.sort_values('funding_amount', ascending=False)
    
    # Get top 10 industries
    top_industries = industry_funding.head(10)
    
    # Create figure
    fig = px.bar(
        top_industries,
        x='industry',
        y='funding_amount',
        title='Top 10 Industries by Funding Amount',
        labels={'industry': 'Industry', 'funding_amount': 'Funding Amount ($M)'},
        color='funding_amount',
        color_continuous_scale='Viridis'
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Industry',
        yaxis_title='Funding Amount ($M)',
        template='plotly_white',
        xaxis={'categoryorder': 'total descending'}
    )
    
    return fig

def funding_by_round(df):
    """
    Create a pie chart of funding by round
    
    Args:
        df: DataFrame of startup data
        
    Returns:
        plotly.graph_objects.Figure: Pie chart
    """
    if df.empty or 'funding_round' not in df.columns or 'funding_amount' not in df.columns:
        # Return empty figure if no data
        return go.Figure()
    
    # Group by funding round and sum funding
    round_funding = df.groupby('funding_round')['funding_amount'].sum().reset_index()
    
    # Create figure
    fig = px.pie(
        round_funding,
        values='funding_amount',
        names='funding_round',
        title='Funding Distribution by Round',
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    
    # Update layout
    fig.update_layout(
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def funding_by_location(df):
    """
    Create a bar chart of top locations by funding amount
    
    Args:
        df: DataFrame of startup data
        
    Returns:
        plotly.graph_objects.Figure: Bar chart
    """
    if df.empty or 'location' not in df.columns or 'funding_amount' not in df.columns:
        # Return empty figure if no data
        return go.Figure()
    
    # Group by location and sum funding
    location_funding = df.groupby('location')['funding_amount'].sum().reset_index()
    location_funding = location_funding.sort_values('funding_amount', ascending=False)
    
    # Get top 10 locations
    top_locations = location_funding.head(10)
    
    # Create figure
    fig = px.bar(
        top_locations,
        x='location',
        y='funding_amount',
        title='Top 10 Locations by Funding Amount',
        labels={'location': 'Location', 'funding_amount': 'Funding Amount ($M)'},
        color='funding_amount',
        color_continuous_scale='Viridis'
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Location',
        yaxis_title='Funding Amount ($M)',
        template='plotly_white',
        xaxis={'categoryorder': 'total descending'}
    )
    
    return fig

def startup_metrics(data):
    """
    Calculate key metrics from startup data
    
    Args:
        data: List of startup dictionaries
        
    Returns:
        dict: Dictionary of metrics
    """
    if not data:
        return {
            "total_startups": 0,
            "total_funding": 0,
            "avg_funding": 0,
            "recent_startups": 0,
            "top_industries": [],
            "top_rounds": []
        }
    
    # Convert to DataFrame
    df = convert_to_dataframe(data)
    
    # Calculate metrics
    total_startups = len(df)
    total_funding = df['funding_amount'].sum()
    avg_funding = df['funding_amount'].mean() if total_startups > 0 else 0
    
    # Recent startups (last 7 days)
    if 'discovery_date' in df.columns:
        recent = df[df['discovery_date'] >= (datetime.now() - pd.Timedelta(days=7))]
        recent_startups = len(recent)
    else:
        recent_startups = 0
    
    # Top industries
    if 'industry' in df.columns:
        industry_counts = df['industry'].value_counts().head(5)
        top_industries = [{"industry": ind, "count": count} for ind, count in industry_counts.items()]
    else:
        top_industries = []
    
    # Top funding rounds
    if 'funding_round' in df.columns:
        round_counts = df['funding_round'].value_counts().head(5)
        top_rounds = [{"round": rnd, "count": count} for rnd, count in round_counts.items()]
    else:
        top_rounds = []
    
    return {
        "total_startups": total_startups,
        "total_funding": round(total_funding, 2),
        "avg_funding": round(avg_funding, 2),
        "recent_startups": recent_startups,
        "top_industries": top_industries,
        "top_rounds": top_rounds
    }
def display_analytics(data):
    """
    Display analytics dashboard with charts and metrics
    
    Args:
        data: List of startup dictionaries
    """
    if not data:
        st.warning("No data available for analytics.")
        return
    
    # Convert to DataFrame
    df = convert_to_dataframe(data)
    
    # Calculate metrics
    total_funding = df["funding_amount"].sum()
    total_startups = len(df)
    
    # Display metrics in a row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Startups", f"{total_startups:,}")
    
    with col2:
        st.metric("Total Funding", f"${total_funding / 1000000:.1f}M")
    
    with col3:
        avg_funding = total_funding / total_startups if total_startups > 0 else 0
        st.metric("Average Funding", f"${avg_funding / 1000000:.1f}M")
    
    # Create charts
    st.plotly_chart(funding_over_time(df), use_container_width=True)
    
    # Two column layout for smaller charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(funding_by_industry(df), use_container_width=True)
    
    with col2:
        st.plotly_chart(funding_by_round(df), use_container_width=True)
    
    # Location chart in full width
    st.plotly_chart(funding_by_location(df), use_container_width=True) 
