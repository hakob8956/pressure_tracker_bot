import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Database configuration
DB_PATH = 'blood_pressure.db'

# AI Model configuration
AI_MODEL = "gpt-4o"

# Application configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
CACHE_EXPIRY = 3600  # Cache expiry in seconds