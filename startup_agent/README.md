# Startup AI Agent

An AI-powered agent system that helps job seekers discover newly funded startups before they post job openings. This agent automatically collects data about startups that recently received funding, analyzes their tech stacks and potential hiring needs, and delivers personalized reports to your inbox.

## Project Overview

This multi-agent system consists of:

1. **Startup Intelligence Collector**: Identifies funded startups using Crunchbase API
2. **Company Researcher**: Uses LLMs to analyze startups' products, tech stack, and likely hiring needs
3. **Report Generator**: Creates beautiful HTML reports with startup insights

## Features

- Daily or weekly email reports with newly funded startups
- AI-powered analysis of company tech stacks and potential roles
- Beautiful HTML reports with detailed company information
- Scheduling system to automate the entire pipeline

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/startup-agent.git
cd startup-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up API keys

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit the `.env` file with your API keys and configuration:

- **CRUNCHBASE_API_KEY**: Get from [Crunchbase](https://data.crunchbase.com/docs)
- **OPENAI_API_KEY**: Get from [OpenAI](https://platform.openai.com/)
- **GOOGLE_NEWS_API_KEY**: Get from [News API](https://newsapi.org/) (optional for future enhancements)
- **Email settings**: Configure your email sending preferences

### 4. Run the pipeline

```bash
python -m startup_agent.main
```

This will:
1. Collect startup funding data
2. Analyze companies with AI
3. Generate and send a report

### 5. Schedule automatic runs

To run the pipeline on a schedule:

```bash
python -m startup_agent.schedule_pipeline
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
├── utils/                    # Utility functions
├── tests/                    # Unit tests
├── scripts/                  # Standalone scripts
├── config.py                 # Configuration settings
├── main.py                   # Main orchestrator
├── requirements.txt          # Dependencies
└── .env.example              # Example environment variables
```

## License

MIT License 