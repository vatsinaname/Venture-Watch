"""
Main dashboard application for Venture-Watch
"""

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Add parent directory to path to ensure imports work
parent_dir = str(Path(__file__).parents[2])
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import dashboard components
from startup_agent.dashboard.charts import (
    create_funding_by_industry_chart,
    create_funding_by_round_chart,
    create_funding_timeline_chart,
    create_location_chart,
    create_funding_distribution_chart
)
from startup_agent.dashboard.filters import (
    create_filter_sidebar
)
from startup_agent.dashboard.controller import (
    filter_startup_data
)
from startup_agent.dashboard.data import (
    load_startup_data,
    convert_to_dataframe
)

# Import config
from startup_agent.config import DATA_DIR, WEB_SCRAPING_ENABLED

# Initialize the Dash app with Bootstrap
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)
app.title = "Venture Watch Dashboard"
server = app.server

# Load initial data
startup_data = load_startup_data()
df = convert_to_dataframe(startup_data)

# App layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Venture Watch Dashboard", className="mt-4 mb-2"),
            html.P("Track and analyze startup funding data in real-time", className="lead")
        ], width=12)
    ]),
    
    html.Hr(),
    
    # Main content
    dbc.Row([
        # Sidebar with filters
        dbc.Col([
            create_filter_sidebar(df)
        ], width=3, className="sidebar-col"),
        
        # Main dashboard area
        dbc.Col([
            # Metrics row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(f"{len(df)}", className="card-title text-center"),
                            html.P("Total Startups", className="card-text text-center")
                        ])
                    ], className="metric-card")
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(f"${df['funding_amount'].sum() / 1000000:.1f}M", className="card-title text-center"),
                            html.P("Total Funding", className="card-text text-center")
                        ])
                    ], className="metric-card")
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(f"${df['funding_amount'].mean() / 1000000:.1f}M", className="card-title text-center"),
                            html.P("Average Funding", className="card-text text-center")
                        ])
                    ], className="metric-card")
                ], width=4)
            ], className="mb-4"),
            
            # Charts
            dbc.Tabs([
                dbc.Tab([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Graph(
                                        id="industry-chart",
                                        figure=create_funding_by_industry_chart(df),
                                        config={"displayModeBar": False}
                                    )
                                ])
                            ])
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Graph(
                                        id="round-chart",
                                        figure=create_funding_by_round_chart(df),
                                        config={"displayModeBar": False}
                                    )
                                ])
                            ])
                        ], width=6)
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Graph(
                                        id="timeline-chart",
                                        figure=create_funding_timeline_chart(df),
                                        config={"displayModeBar": False}
                                    )
                                ])
                            ])
                        ], width=12)
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Graph(
                                        id="location-chart",
                                        figure=create_location_chart(df),
                                        config={"displayModeBar": False}
                                    )
                                ])
                            ])
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Graph(
                                        id="distribution-chart",
                                        figure=create_funding_distribution_chart(df),
                                        config={"displayModeBar": False}
                                    )
                                ])
                            ])
                        ], width=6)
                    ])
                ], label="Overview"),
                
                dbc.Tab([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id="startup-table")
                        ])
                    ])
                ], label="Startup List"),
                
                dbc.Tab([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3("Data Collection Settings"),
                            html.Hr(),
                            dbc.Form([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Web Scraping Enabled"),
                                        dbc.Switch(
                                            id="web-scraping-switch",
                                            value=WEB_SCRAPING_ENABLED,
                                            className="mb-3"
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Button(
                                            "Collect New Data Now",
                                            id="collect-data-button",
                                            color="primary",
                                            className="mb-3"
                                        )
                                    ], width=6)
                                ])
                            ])
                        ])
                    ])
                ], label="Settings")
            ])
        ], width=9)
    ]),
    
    # Footer
    html.Footer([
        html.Hr(),
        html.P("© 2023 Venture Watch. Powered by AI-Enhanced Web Scrapers", className="text-center")
    ], className="mt-4"),
    
    # Interval component for periodic updates
    dcc.Interval(
        id="update-interval",
        interval=300000,  # 5 minutes (in milliseconds)
        n_intervals=0
    ),
    
    # Store components for sharing data between callbacks
    dcc.Store(id="filtered-data"),
], fluid=True)

# Callback for updating charts when filters change
@app.callback(
    [
        Output('industry-chart', 'figure'),
        Output('round-chart', 'figure'),
        Output('timeline-chart', 'figure'),
        Output('location-chart', 'figure'),
        Output('distribution-chart', 'figure'),
        Output('startup-table', 'children'),
        Output('filtered-data', 'data')
    ],
    [
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date'),
        Input('funding-filter', 'value'),
        Input('industry-filter', 'value'),
        Input('round-filter', 'value'),
        Input('location-filter', 'value'),
        Input('reset-button', 'n_clicks')
    ]
)
def update_dashboard(start_date, end_date, funding_range, industries, rounds, locations, reset_clicks):
    """Update dashboard based on filter changes"""
    # Load the data
    startup_data = load_startup_data()
    df = convert_to_dataframe(startup_data)
    
    # Apply filters
    filters = {
        'start_date': start_date,
        'end_date': end_date,
        'min_funding': funding_range[0] if funding_range else 0,
        'max_funding': funding_range[1] if funding_range else 100,
        'industry': industries,
        'funding_round': rounds,
        'location': locations
    }
    
    filtered_df = filter_startup_data(df, filters)
    
    # Create updated charts
    industry_chart = create_funding_by_industry_chart(filtered_df)
    round_chart = create_funding_by_round_chart(filtered_df)
    timeline_chart = create_funding_timeline_chart(filtered_df)
    location_chart = create_location_chart(filtered_df)
    distribution_chart = create_funding_distribution_chart(filtered_df)
    
    # Create startup cards
    startup_cards = create_startup_cards(filtered_df)
    
    # Return all outputs
    return industry_chart, round_chart, timeline_chart, location_chart, distribution_chart, startup_cards, filtered_df.to_dict('records')

# Callback for data collection
@app.callback(
    Output('collect-data-button', 'children'),
    [Input('collect-data-button', 'n_clicks')]
)
def collect_data(n_clicks):
    """Trigger data collection process"""
    if n_clicks is None:
        return "Collect New Data Now"
    
    # Import controller
    from startup_agent.dashboard.controller import run_data_collection
    
    # Run data collection in background
    run_data_collection(days_back=7)
    
    return "Data Collection Started"

# Helper function to create startup cards
def create_startup_cards(df):
    """Create cards for each startup with detailed information"""
    if df.empty:
        return html.Div("No startups match the current filters.", className="text-center p-5")
    
    # Create cards for each startup
    cards = []
    for _, row in df.iterrows():
        # Create a card with more detailed information
        card = dbc.Card(
            [
                dbc.CardHeader(
                    html.H4(row.get('company_name', 'Unknown'), className="card-title")
                ),
                dbc.CardBody(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.H5("Industry", className="text-muted"),
                                html.P(row.get('industry', 'Unknown'))
                            ], width=4),
                            dbc.Col([
                                html.H5("Funding", className="text-muted"),
                                html.P(f"${row.get('funding_amount', 0) / 1000000:.1f}M")
                            ], width=4),
                            dbc.Col([
                                html.H5("Round", className="text-muted"),
                                html.P(row.get('funding_round', 'Unknown'))
                            ], width=4)
                        ]),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([
                                html.H5("Location", className="text-muted"),
                                html.P(row.get('location', 'Unknown'))
                            ], width=6),
                            dbc.Col([
                                html.H5("Description", className="text-muted"),
                                html.P(row.get('description', 'No description available'))
                            ], width=6)
                        ]),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([
                                html.H5("Investors", className="text-muted"),
                                html.P(", ".join(row.get('investors', [])) if row.get('investors') else "Not available")
                            ], width=12)
                        ])
                    ]
                ),
                dbc.CardFooter(
                    [
                        html.Small(f"Source: {row.get('source', 'Unknown')}"),
                        html.Div([
                            dbc.Button("View Details", color="primary", size="sm", className="mt-2"),
                            dbc.Button("Visit Website", color="secondary", size="sm", className="ml-2 mt-2")
                        ], className="d-flex justify-content-between mt-2")
                    ]
                )
            ],
            className="mb-4"
        )
        cards.append(card)
    
    # Arrange cards in a responsive grid layout
    return html.Div(
        [
            dbc.Row(
                [dbc.Col(card, md=6) for card in cards],
                className="g-4"  # Add gap between cards
            )
        ]
    )

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True) 