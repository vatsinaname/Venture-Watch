# Venture Watch Dashboard

A real-time dashboard for analyzing startup funding data.

## Features

- **Interactive Data Visualization**: Charts and graphs for analyzing startup funding by industry, round, location, and time
- **Real-time Data Collection**: Automated web scraping from multiple sources
- **Advanced Filtering**: Filter startups by multiple criteria
- **Responsive Design**: Works on desktop and mobile devices

## Components

The dashboard is built with the following components:

- **data.py**: Data loading and processing utilities
- **filters.py**: Filter components and logic
- **charts.py**: Chart creation functions
- **app.py**: Main dashboard application
- **visualization.py**: Additional visualization utilities
- **ui_components.py**: Reusable UI components

## Running the Dashboard

To run the dashboard:

```bash
cd Venture-Watch
python -m startup_agent.run_dashboard
```

### Command Line Options

- `--port PORT`: Specify the port to run the dashboard on (default: 8050)
- `--debug`: Run in debug mode
- `--no-browser`: Don't open browser automatically

## Dependencies

- Dash
- Dash Bootstrap Components
- Plotly
- Pandas
- Python 3.7+ 