# Venture-Watch

AI agent that identifies recently funded startups and aligns them with your skills.

## Overview

Venture-Watch is an intelligent agent system that helps job seekers discover promising startup opportunities before they're widely advertised. It collects data on recently funded startups, analyzes their technology stacks and needs, and matches them with your skills and experience.

## Features

- **Startup Collection**: Gathers data on recently funded startups from Google News and Google Custom Search APIs
- **Company Research**: Uses LLMs to analyze startup products, tech stacks, and hiring needs
- **Skill Matching**: Compares your skillset with startup needs for targeted matching
- **Interactive Dashboard**: Visualize and filter startup opportunities
- **Customizable Reports**: Generate PDF reports of matched startups

## API Requirements

This project uses the following APIs:
- **Google API Key**: For accessing Google Custom Search
- **Google Custom Search Engine ID**: A custom search engine configured for startup funding news
- **OpenAI API Key**: For the LLM-based analysis components

You can get these keys by following these steps:
1. [Google API Key](https://console.cloud.google.com/apis/credentials) - Create a project and generate an API key
2. [Custom Search Engine](https://programmablesearchengine.google.com/controlpanel/create) - Create a search engine and get the CSE ID
3. [OpenAI API Key](https://platform.openai.com/account/api-keys) - Sign up and generate an API key

## Installation

```powershell
# Clone the repository
git clone https://github.com/vatsinaname/Venture-Watch.git
cd Venture-Watch

# Install dependencies
pip install -e .

# Set up environment variables
Copy-Item startup_agent\.env.example startup_agent\.env
# Edit .env with your API keys
```

## Usage

### Start the Dashboard

```powershell
# Run the Streamlit dashboard
streamlit run simple_dashboard.py
```

### Run the Data Collection Agent

```powershell
# Collect recent startup data
python -m startup_agent.agents.startup_collector
```

## Docker Support

The project includes Docker support for easy deployment:

```powershell
# Start all services
docker-compose up

# Or just the dashboard
docker-compose up dashboard
```

### Using the Docker Helper Scripts

For Windows users:
```powershell
# Run the batch file helper
.\docker-start.bat
```

For PowerShell users:
```powershell
# Run the PowerShell helper
.\docker-start.ps1
```

These scripts provide an interactive menu for common Docker operations.

## License

MIT License 