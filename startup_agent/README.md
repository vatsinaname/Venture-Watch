# Startup AI Agent

An AI-powered agent system that helps job seekers discover newly funded startups before they post job openings. This agent automatically collects data about startups that recently received funding, analyzes their tech stacks and potential hiring needs, and delivers personalized reports to your inbox.

## Project Overview

This multi-agent system consists of:

1. **Startup Intelligence Collector**: Identifies funded startups using Crunchbase API
2. **Company Researcher**: Uses LLMs to analyze startups' products, tech stack, and likely hiring needs
3. **Report Generator**: Creates beautiful reports in multiple formats (HTML, PDF)
4. **Interactive Dashboard**: Streamlit-based UI for exploring startup data

## Features

- Daily or weekly email reports with newly funded startups
- AI-powered analysis of company tech stacks and potential roles
- Multiple report formats (HTML, PDF, CSV)
- Interactive dashboard for data exploration
- Scheduling system to automate the entire pipeline
- Docker containerization for easy deployment

## Setup Instructions

### Option 1: Using Docker (Recommended)

The easiest way to run the system is with Docker:

```bash
# From the root directory (Venture-Watch)
cp startup_agent/.env.example .env
# Edit .env with your API keys

# Run everything
docker-compose up -d
```

This will start three services:
- Agent for data collection
- Dashboard for data exploration (available at http://localhost:8501)
- Scheduler for automated runs

### Option 2: Manual Installation

```bash
git clone https://github.com/vatsinaname/Venture-Watch.git
cd Venture-Watch

# Install dependencies
pip install -r startup_agent/requirements.txt

# Configure your API keys
cp startup_agent/.env.example startup_agent/.env
# Edit the .env file with your API keys

# Run the pipeline
python run.py
```

## Using the Dashboard

To explore the data interactively:

```bash
# With Docker:
docker-compose up -d dashboard

# Without Docker:
python -m startup_agent.run_dashboard
```

This will start a Streamlit server at http://localhost:8501 where you can:
- Filter startups by category, tech stack, and funding round
- View detailed company profiles
- Generate custom PDF reports
- Export data to CSV

## Data Collection

To run the data collection pipeline:

```bash
# With Docker:
docker-compose run --rm agent

# Without Docker:
python run.py
```

## Scheduling Data Collection

To run the pipeline on a schedule:

```bash
# With Docker:
docker-compose up -d scheduler

# Without Docker:
python -m startup_agent.main --schedule
```

## Testing

Run the tests with:

```bash
# Without Docker:
python -m startup_agent.tests.run_tests

# With Docker:
docker-compose run --rm agent python -m startup_agent.tests.run_tests
```

## Project Structure

```
startup_agent/
├── agents/
│   ├── startup_collector.py  # Agent 1: Collects funding data
│   ├── company_researcher.py # Agent 2: LLM analysis of companies
│   └── report_generator.py   # Agent 5: Creates reports
├── data/                     # Storage for collected and processed data
├── utils/
│   ├── helpers.py            # Utility functions
│   └── pdf_generator.py      # PDF report generation
├── tests/                    # Unit tests
├── scripts/                  # Standalone scripts
├── dashboard.py              # Streamlit dashboard
├── run_dashboard.py          # Dashboard launcher
├── config.py                 # Configuration settings
├── main.py                   # Main orchestrator
├── requirements.txt          # Dependencies
└── .env.example              # Example environment variables
```

## Docker Configuration

The Docker setup includes:

- **Dockerfile**: Builds the application image
- **docker-compose.yml**: Defines three services (agent, dashboard, scheduler)
- **docker-start.sh/ps1**: Helper scripts for common Docker operations
- **Volume**: Shared data storage between services

## License

MIT License 