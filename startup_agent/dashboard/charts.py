"""
Chart creation functions for the Venture-Watch dashboard
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_funding_by_industry_chart(df):
    """
    Create a bar chart showing funding by industry
    
    Args:
        df: DataFrame containing startup data
    
    Returns:
        Figure: Plotly figure object
    """
    # Group by industry and sum funding
    industry_funding = df.groupby("industry")["funding_amount"].sum().reset_index()
    industry_funding = industry_funding.sort_values("funding_amount", ascending=False)
    
    # Create bar chart
    fig = px.bar(
        industry_funding, 
        x="industry", 
        y="funding_amount",
        title="Total Funding by Industry (Millions USD)",
        labels={"industry": "Industry", "funding_amount": "Funding (Millions USD)"},
        color="funding_amount",
        color_continuous_scale="Viridis"
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Industry",
        yaxis_title="Funding (Millions USD)",
        coloraxis_showscale=False,
        margin=dict(l=40, r=40, t=40, b=80),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2c3e50")
    )
    
    return fig

def create_funding_by_round_chart(df):
    """
    Create a pie chart showing funding by round
    
    Args:
        df: DataFrame containing startup data
    
    Returns:
        Figure: Plotly figure object
    """
    # Group by funding round and sum funding
    round_funding = df.groupby("funding_round")["funding_amount"].sum().reset_index()
    
    # Create pie chart
    fig = px.pie(
        round_funding, 
        values="funding_amount", 
        names="funding_round",
        title="Funding Distribution by Round",
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    
    # Update layout
    fig.update_layout(
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2c3e50")
    )
    
    # Update traces
    fig.update_traces(
        textposition="inside", 
        textinfo="percent+label",
        hoverinfo="label+percent+value",
        marker=dict(line=dict(color="#FFFFFF", width=1))
    )
    
    return fig

def create_funding_timeline_chart(df):
    """
    Create a line chart showing funding over time
    
    Args:
        df: DataFrame containing startup data
    
    Returns:
        Figure: Plotly figure object
    """
    # Ensure date column exists and has values
    if "date" not in df.columns or df["date"].isna().all():
        # Create empty figure if no date data
        fig = go.Figure()
        fig.update_layout(
            title="Funding Timeline (No Date Data Available)",
            xaxis_title="Date",
            yaxis_title="Funding (Millions USD)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#2c3e50")
        )
        return fig
    
    # Group by date (month) and sum funding
    df_with_date = df.dropna(subset=["date"]).copy()
    df_with_date["month"] = df_with_date["date"].dt.to_period("M").astype(str)
    monthly_funding = df_with_date.groupby("month")["funding_amount"].sum().reset_index()
    monthly_funding = monthly_funding.sort_values("month")
    
    # Create line chart
    fig = px.line(
        monthly_funding, 
        x="month", 
        y="funding_amount",
        title="Funding Timeline",
        labels={"month": "Month", "funding_amount": "Funding (Millions USD)"},
        markers=True
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Funding (Millions USD)",
        margin=dict(l=40, r=40, t=40, b=80),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2c3e50")
    )
    
    # Update traces
    fig.update_traces(
        line=dict(color="#1e88e5", width=3),
        marker=dict(size=8, color="#1e88e5")
    )
    
    return fig

def create_location_chart(df):
    """
    Create a bar chart showing startup count by location
    
    Args:
        df: DataFrame containing startup data
    
    Returns:
        Figure: Plotly figure object
    """
    # Group by location and count startups
    location_counts = df.groupby("location").size().reset_index(name="count")
    location_counts = location_counts.sort_values("count", ascending=False).head(10)
    
    # Create bar chart
    fig = px.bar(
        location_counts, 
        x="location", 
        y="count",
        title="Top 10 Startup Locations",
        labels={"location": "Location", "count": "Number of Startups"},
        color="count",
        color_continuous_scale="Viridis"
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Location",
        yaxis_title="Number of Startups",
        coloraxis_showscale=False,
        margin=dict(l=40, r=40, t=40, b=80),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2c3e50")
    )
    
    return fig

def create_funding_distribution_chart(df):
    """
    Create a histogram showing the distribution of funding amounts
    
    Args:
        df: DataFrame containing startup data
    
    Returns:
        Figure: Plotly figure object
    """
    # Create histogram
    fig = px.histogram(
        df, 
        x="funding_amount",
        title="Distribution of Funding Amounts",
        labels={"funding_amount": "Funding (Millions USD)", "count": "Number of Startups"},
        nbins=20,
        color_discrete_sequence=["#1e88e5"]
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Funding (Millions USD)",
        yaxis_title="Number of Startups",
        margin=dict(l=40, r=40, t=40, b=80),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2c3e50")
    )
    
    return fig 