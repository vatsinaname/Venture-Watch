"""
Visualization functions for the Venture-Watch dashboard
"""

import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

def create_startup_count_chart(data):
    """
    Create a bar chart showing the count of startups by industry
    
    Args:
        data: List of startup dictionaries
        
    Returns:
        Plotly figure object
    """
    # Count startups by industry
    industry_counts = Counter([item.get("industry", "Unknown") for item in data])
    
    # Prepare data for chart
    industries = list(industry_counts.keys())
    counts = list(industry_counts.values())
    
    # Sort by count
    sorted_data = sorted(zip(industries, counts), key=lambda x: x[1], reverse=True)
    industries, counts = zip(*sorted_data) if sorted_data else ([], [])
    
    fig = px.bar(
        x=industries,
        y=counts,
        title="Startups by Industry",
        labels={"x": "Industry", "y": "Number of Startups"},
        color=counts,
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    
    return fig

def create_funding_by_round_chart(data):
    """
    Create a pie chart showing funding distribution by round
    
    Args:
        data: List of startup dictionaries
        
    Returns:
        Plotly figure object
    """
    # Extract funding rounds and amounts
    funding_data = {}
    for item in data:
        round_type = item.get("funding_round", "Unknown")
        amount = item.get("funding_amount", 0)
        
        if round_type not in funding_data:
            funding_data[round_type] = 0
            
        try:
            funding_data[round_type] += float(amount)
        except (ValueError, TypeError):
            pass
    
    # Prepare data for chart
    rounds = list(funding_data.keys())
    amounts = list(funding_data.values())
    
    fig = px.pie(
        values=amounts,
        names=rounds,
        title="Funding Distribution by Round",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    
    return fig

def create_time_series_chart(data):
    """
    Create a time series chart showing funding over time
    
    Args:
        data: List of startup dictionaries
        
    Returns:
        Plotly figure object
    """
    import pandas as pd
    from datetime import datetime
    
    # Extract dates and amounts
    chart_data = []
    for item in data:
        date = item.get("discovery_date") or item.get("published_date")
        amount = item.get("funding_amount", 0)
        
        if date and amount:
            try:
                date = pd.to_datetime(date)
                amount = float(amount)
                chart_data.append({"date": date, "amount": amount})
            except (ValueError, TypeError):
                pass
    
    if not chart_data:
        # Return empty chart if no data
        fig = go.Figure()
        fig.update_layout(
            title="Funding Over Time",
            xaxis_title="Date",
            yaxis_title="Funding Amount (USD)",
            height=400
        )
        return fig
    
    # Convert to DataFrame
    df = pd.DataFrame(chart_data)
    
    # Group by date
    df = df.sort_values("date")
    df["date"] = df["date"].dt.date
    grouped = df.groupby("date").sum().reset_index()
    
    fig = px.line(
        grouped,
        x="date",
        y="amount",
        title="Funding Over Time",
        labels={"date": "Date", "amount": "Funding Amount (USD)"},
        markers=True
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    
    return fig

def create_location_chart(data):
    """
    Create a bar chart showing startup counts by location
    
    Args:
        data: List of startup dictionaries
        
    Returns:
        Plotly figure object
    """
    # Count startups by location
    location_counts = Counter([item.get("location", "Unknown") for item in data])
    
    # Sort and take top 10
    locations = [loc for loc, count in location_counts.most_common(10)]
    counts = [location_counts[loc] for loc in locations]
    
    fig = px.bar(
        x=locations,
        y=counts,
        title="Top Startup Locations",
        labels={"x": "Location", "y": "Number of Startups"},
        color=counts,
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    
    return fig

def create_tech_stack_chart(data):
    """
    Create a horizontal bar chart showing most common technologies
    
    Args:
        data: List of startup dictionaries
        
    Returns:
        Plotly figure object
    """
    # Extract tech stack data
    tech_stack_data = []
    for item in data:
        tech_stack = item.get("tech_stack", [])
        if isinstance(tech_stack, str):
            try:
                # Try to evaluate as literal
                import ast
                tech_stack = ast.literal_eval(tech_stack)
            except (ValueError, SyntaxError):
                # Split by comma if evaluation fails
                tech_stack = [t.strip() for t in tech_stack.split(",")]
                
        if isinstance(tech_stack, list):
            tech_stack_data.extend(tech_stack)
    
    # Count occurrences
    tech_counts = Counter(tech_stack_data)
    
    # Sort and take top 15
    top_tech = [tech for tech, count in tech_counts.most_common(15)]
    counts = [tech_counts[tech] for tech in top_tech]
    
    fig = px.bar(
        y=top_tech,
        x=counts,
        title="Top Technologies Used",
        labels={"y": "Technology", "x": "Number of Startups"},
        orientation="h",
        color=counts,
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=500
    )
    
    return fig 