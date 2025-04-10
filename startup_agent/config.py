"""
Configuration file for the Venture-Watch project
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# LLM Provider settings
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # Options: openai, groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "deepseek-r1-distill-llama-70b")

# Google News API settings
GOOGLE_NEWS_DAYS_LOOKBACK = 7  # Number of days to look back for news

# User profile settings
USER_SKILLS = os.getenv("USER_SKILLS", "").split(",")
USER_EXPERIENCE = int(os.getenv("USER_EXPERIENCE", "0"))
USER_INDUSTRY_PREFERENCES = os.getenv("USER_INDUSTRY_PREFERENCES", "").split(",")

# Email settings
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# LLM settings
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-3.5-turbo")

# Base directories
ROOT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = DATA_DIR / "reports"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# API Keys and credentials
CRUNCHBASE_API_KEY = os.getenv('CRUNCHBASE_API_KEY', '')
REPORT_FREQUENCY = os.getenv('REPORT_FREQUENCY', 'daily')  # 'daily' or 'weekly'

# Application settings
MAX_STARTUPS_PER_REPORT = 100
DAYS_TO_LOOK_BACK = 7

# Additional application settings
FUNDING_DATA_FILENAME = "funding_data.json"
ANALYSIS_DATA_FILENAME = "analysis_data.json" 