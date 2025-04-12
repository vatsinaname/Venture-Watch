"""
UI components for the Venture-Watch dashboard
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

def create_navbar():
    """
    Create the navigation bar for the dashboard
    
    Returns:
        dbc.Navbar: Dash Bootstrap Components Navbar
    """
    # Create navbar
    navbar = dbc.Navbar(
        dbc.Container(
            [
                # Brand on the left
                dbc.NavbarBrand(
                    [
                        html.Img(src="/assets/logo.png", height="30px", className="me-2"),
                        "Venture Watch"
                    ],
                    href="#",
                    className="ms-2",
                ),
                # Navigation items on the right
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("Dashboard", href="#", active=True)),
                        dbc.NavItem(dbc.NavLink("Startups", href="#")),
                        dbc.NavItem(dbc.NavLink("Analytics", href="#")),
                        dbc.NavItem(dbc.NavLink("About", href="#")),
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
            ]
        ),
        color="dark",
        dark=True,
        className="mb-4",
    )
    
    return navbar

def create_header():
    """
    Create the header section with title and description
    
    Returns:
        dbc.Container: Dash Bootstrap Components Container
    """
    header = dbc.Container(
        [
            html.H1("Startup Funding Dashboard", className="display-4"),
            html.P(
                "Track and analyze startup funding data with interactive visualizations and insights.",
                className="lead",
            ),
            html.Hr(className="my-4"),
        ],
        fluid=True,
        className="py-3",
    )
    
    return header

def create_filters(unique_industries, unique_rounds, unique_locations):
    """
    Create filter components for the dashboard
    
    Args:
        unique_industries: List of unique industries
        unique_rounds: List of unique funding rounds
        unique_locations: List of unique locations
        
    Returns:
        dbc.Card: Dash Bootstrap Components Card
    """
    # Create filter options
    industry_options = [{"label": industry, "value": industry} for industry in sorted(unique_industries)]
    round_options = [{"label": round, "value": round} for round in sorted(unique_rounds)]
    location_options = [{"label": location, "value": location} for location in sorted(unique_locations)]
    
    # Time period options
    time_options = [
        {"label": "All Time", "value": "all"},
        {"label": "Last 7 Days", "value": "7days"},
        {"label": "Last 30 Days", "value": "30days"},
        {"label": "Last 90 Days", "value": "90days"},
        {"label": "Last 365 Days", "value": "365days"},
    ]
    
    # Create filter components
    filters = dbc.Card(
        dbc.CardBody(
            [
                html.H4("Filters", className="card-title"),
                html.Hr(),
                
                html.Label("Industry"),
                dcc.Dropdown(
                    id="industry-filter",
                    options=industry_options,
                    placeholder="Select Industry",
                    multi=True,
                    className="mb-3",
                ),
                
                html.Label("Funding Round"),
                dcc.Dropdown(
                    id="round-filter",
                    options=round_options,
                    placeholder="Select Funding Round",
                    multi=True,
                    className="mb-3",
                ),
                
                html.Label("Location"),
                dcc.Dropdown(
                    id="location-filter",
                    options=location_options,
                    placeholder="Select Location",
                    multi=True,
                    className="mb-3",
                ),
                
                html.Label("Time Period"),
                dcc.Dropdown(
                    id="time-filter",
                    options=time_options,
                    value="all",
                    clearable=False,
                    className="mb-3",
                ),
                
                html.Label("Minimum Funding ($M)"),
                dcc.Slider(
                    id="funding-filter",
                    min=0,
                    max=100,
                    step=1,
                    value=0,
                    marks={i: str(i) for i in range(0, 101, 20)},
                    className="mb-3",
                ),
                
                dbc.Button(
                    "Apply Filters",
                    id="apply-filters-button",
                    color="primary",
                    className="mt-3 w-100",
                ),
                
                dbc.Button(
                    "Reset Filters",
                    id="reset-filters-button",
                    color="secondary",
                    className="mt-2 w-100",
                ),
            ]
        ),
        className="mb-4",
    )
    
    return filters

def create_metrics_cards(metrics):
    """
    Create metric cards displaying key stats
    
    Args:
        metrics: Dictionary of metrics
        
    Returns:
        dbc.Row: Dash Bootstrap Components Row
    """
    metrics_cards = dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4(f"{metrics['total_startups']}", className="card-title text-center"),
                            html.P("Total Startups", className="card-text text-center"),
                        ]
                    ),
                    className="mb-4 bg-light",
                ),
                width=3,
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4(f"${metrics['total_funding']}M", className="card-title text-center"),
                            html.P("Total Funding", className="card-text text-center"),
                        ]
                    ),
                    className="mb-4 bg-light",
                ),
                width=3,
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4(f"${metrics['avg_funding']}M", className="card-title text-center"),
                            html.P("Average Funding", className="card-text text-center"),
                        ]
                    ),
                    className="mb-4 bg-light",
                ),
                width=3,
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4(f"{metrics['recent_startups']}", className="card-title text-center"),
                            html.P("Recent Startups (7d)", className="card-text text-center"),
                        ]
                    ),
                    className="mb-4 bg-light",
                ),
                width=3,
            ),
        ],
        className="mb-4",
    )
    
    return metrics_cards

def create_chart_card(title, chart_id):
    """
    Create a card containing a chart
    
    Args:
        title: Chart title
        chart_id: ID for the chart component
        
    Returns:
        dbc.Card: Dash Bootstrap Components Card
    """
    chart_card = dbc.Card(
        dbc.CardBody(
            [
                html.H4(title, className="card-title"),
                dcc.Graph(id=chart_id, className="mt-3"),
            ]
        ),
        className="mb-4",
    )
    
    return chart_card

def create_startups_table():
    """
    Create a table to display startup data
    
    Returns:
        dbc.Card: Dash Bootstrap Components Card
    """
    startups_table = dbc.Card(
        dbc.CardBody(
            [
                html.H4("Recent Startup Fundings", className="card-title"),
                html.Div(id="startups-table", className="mt-3"),
            ]
        ),
        className="mb-4",
    )
    
    return startups_table

def create_footer():
    """
    Create footer with credits and links
    
    Returns:
        dbc.Container: Dash Bootstrap Components Container
    """
    footer = dbc.Container(
        [
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        html.P(
                            [
                                "Venture Watch Dashboard © 2023 | ",
                                html.A("Data", href="#", className="text-decoration-none"),
                                " | ",
                                html.A("API", href="#", className="text-decoration-none"),
                                " | ",
                                html.A("GitHub", href="#", className="text-decoration-none"),
                            ],
                            className="text-center text-muted",
                        )
                    )
                ]
            ),
        ],
        fluid=True,
        className="py-3",
    )
    
    return footer 