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

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/vatsinaname/Venture-Watch.git
cd Venture-Watch
```

### 2. Install dependencies

```bash
pip install -r startup_agent/requirements.txt
```

### 3. Set up API keys

Copy the example environment file and fill in your API keys:

```bash
cp startup_agent/.env.example startup_agent/.env
```

Edit the `.env` file with your API keys and configuration:

- **CRUNCHBASE_API_KEY**: Get from [Crunchbase](https://data.crunchbase.com/docs)
- **OPENAI_API_KEY**: Get from [OpenAI](https://platform.openai.com/)
- **GOOGLE_NEWS_API_KEY**: Get from [News API](https://newsapi.org/) (optional for future enhancements)
- **Email settings**: Configure your email sending preferences

### 4. Run the pipeline

```bash
python run.py
```

This will:
1. Collect startup funding data
2. Analyze companies with AI
3. Generate and send a report

### 5. Launch the dashboard

To explore the data interactively:

```bash
python -m startup_agent.run_dashboard
```

This will start a Streamlit server at http://localhost:8501 where you can:
- Filter startups by category, tech stack, and funding round
- View detailed company profiles
- Generate custom PDF reports
- Export data to CSV

### 6. Schedule automatic runs

To run the pipeline on a schedule:

```bash
python -m startup_agent.main --schedule
```

## Testing

Run the tests with:

```bash
python -m startup_agent.tests.run_tests
```

Or run an individual test:

```bash
python -m unittest startup_agent.tests.test_startup_collector
```

## Extending the Project

### Adding a Skill Matcher

A future enhancement will include a Skill Matcher agent that compares your skills with startup needs.

### Adding a Contribution Strategist

Another planned agent will suggest specific ways you could contribute to each startup.

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

## License

MIT License 