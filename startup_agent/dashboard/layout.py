"""
Layout components for the Venture-Watch dashboard
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

def create_header():
    """
    Create the dashboard header with logo and title
    
    Returns:
        dash component: Header component
    """
    return html.Div(
        className="header",
        children=[
            html.Img(
                src="/assets/logo.png",
                className="logo"
            ),
            html.H1("Venture Watch Dashboard"),
            html.P("Track and analyze startup funding data in real-time")
        ]
    )

def create_filters(industries, rounds, locations):
    """
    Create the filter panel for the dashboard
    
    Args:
        industries: List of available industries
        rounds: List of available funding rounds
        locations: List of available locations
        
    Returns:
        dash component: Filters component
    """
    return html.Div(
        className="filters-panel",
        children=[
            html.H3("Filters"),
            
            html.Label("Industry:"),
            dcc.Dropdown(
                id="industry-filter",
                options=[{"label": industry, "value": industry} for industry in sorted(industries)],
                value=[],
                multi=True,
                placeholder="Select Industries"
            ),
            
            html.Label("Funding Round:"),
            dcc.Dropdown(
                id="round-filter",
                options=[{"label": round_name, "value": round_name} for round_name in sorted(rounds)],
                value=[],
                multi=True,
                placeholder="Select Funding Rounds"
            ),
            
            html.Label("Location:"),
            dcc.Dropdown(
                id="location-filter",
                options=[{"label": location, "value": location} for location in sorted(locations)],
                value=[],
                multi=True,
                placeholder="Select Locations"
            ),
            
            html.Label("Time Period:"),
            dcc.Dropdown(
                id="time-filter",
                options=[
                    {"label": "Last 30 days", "value": "30_days"},
                    {"label": "Last 90 days", "value": "90_days"},
                    {"label": "Last 6 months", "value": "6_months"},
                    {"label": "Last year", "value": "1_year"},
                    {"label": "All time", "value": "all_time"},
                ],
                value="all_time",
                placeholder="Select Time Period"
            ),
            
            html.Label("Funding Amount:"),
            dcc.RangeSlider(
                id="funding-filter",
                min=0,
                max=100,
                step=5,
                marks={i: f"${i}M" for i in range(0, 101, 20)},
                value=[0, 100]
            ),
            
            html.Button("Apply Filters", id="apply-filters", className="filter-button")
        ]
    )

def create_summary_metrics(total_startups, total_funding, avg_funding):
    """
    Create summary metrics cards
    
    Args:
        total_startups: Total number of startups
        total_funding: Total funding amount
        avg_funding: Average funding amount
        
    Returns:
        dash component: Summary metrics component
    """
    return html.Div(
        className="metrics-container",
        children=[
            html.Div(
                className="metric-card",
                children=[
                    html.H3("Total Startups"),
                    html.H2(f"{total_startups}")
                ]
            ),
            html.Div(
                className="metric-card",
                children=[
                    html.H3("Total Funding"),
                    html.H2(f"${total_funding:.2f}M")
                ]
            ),
            html.Div(
                className="metric-card",
                children=[
                    html.H3("Avg. Funding"),
                    html.H2(f"${avg_funding:.2f}M")
                ]
            )
        ]
    )

def create_chart_layout():
    """
    Create the layout for charts
    
    Returns:
        dash component: Charts layout component
    """
    return html.Div(
        className="charts-container",
        children=[
            html.Div(
                className="chart-row",
                children=[
                    html.Div(
                        className="chart-container",
                        children=[
                            dcc.Graph(id="funding-by-industry-chart")
                        ]
                    ),
                    html.Div(
                        className="chart-container",
                        children=[
                            dcc.Graph(id="funding-by-round-chart")
                        ]
                    )
                ]
            ),
            html.Div(
                className="chart-row",
                children=[
                    html.Div(
                        className="chart-container",
                        children=[
                            dcc.Graph(id="funding-timeline-chart")
                        ]
                    ),
                    html.Div(
                        className="chart-container",
                        children=[
                            dcc.Graph(id="funding-by-location-chart")
                        ]
                    )
                ]
            ),
            html.Div(
                className="chart-row full-width",
                children=[
                    html.Div(
                        className="chart-container",
                        children=[
                            dcc.Graph(id="startup-count-chart")
                        ]
                    )
                ]
            )
        ]
    )

def create_startup_table():
    """
    Create the startup data table
    
    Returns:
        dash component: Startup table component
    """
    return html.Div(
        className="table-container",
        children=[
            html.H3("Startup Data"),
            dbc.Table(id="startup-table", striped=True, bordered=True, hover=True)
        ]
    )

def create_footer():
    """
    Create the dashboard footer
    
    Returns:
        dash component: Footer component
    """
    return html.Div(
        className="footer",
        children=[
            html.P(f"© {datetime.now().year} Venture Watch. All rights reserved."),
            html.P("Powered by the Dancing Ninjas Web Scrapers")
        ]
    )

def create_main_layout(industries, rounds, locations, total_startups, total_funding, avg_funding):
    """
    Create the main dashboard layout
    
    Args:
        industries: List of available industries
        rounds: List of available funding rounds
        locations: List of available locations
        total_startups: Total number of startups
        total_funding: Total funding amount
        avg_funding: Average funding amount
        
    Returns:
        dash component: Main layout component
    """
    return html.Div(
        className="dashboard-container",
        children=[
            create_header(),
            html.Div(
                className="dashboard-content",
                children=[
                    html.Div(
                        className="sidebar",
                        children=[
                            create_filters(industries, rounds, locations)
                        ]
                    ),
                    html.Div(
                        className="main-content",
                        children=[
                            create_summary_metrics(total_startups, total_funding, avg_funding),
                            create_chart_layout(),
                            create_startup_table()
                        ]
                    )
                ]
            ),
            create_footer()
        ]
    )

from datetime import datetime 