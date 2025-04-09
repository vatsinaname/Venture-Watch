import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# API Keys and credentials
CRUNCHBASE_API_KEY = os.getenv('CRUNCHBASE_API_KEY', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GOOGLE_NEWS_API_KEY = os.getenv('GOOGLE_NEWS_API_KEY', '')

# Email settings
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT', '')
EMAIL_SENDER = os.getenv('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))

# Application settings
MAX_STARTUPS_PER_REPORT = 5
DAYS_TO_LOOK_BACK = 7
REPORT_FREQUENCY = os.getenv('REPORT_FREQUENCY', 'daily')  # 'daily' or 'weekly' 