import os
from dotenv import load_dotenv

# Load .env file on startup
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smartagri-secret-2024')

    # ── Weather (free: https://openweathermap.org/api) ──────────────────
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'demo_key')
    WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5'

    # ── Google Gemini AI (free: https://aistudio.google.com/apikey) ─────
    GEMINI_API_KEY  = os.environ.get('GEMINI_API_KEY', '')

    # ── Hugging Face (free: https://huggingface.co/settings/tokens) ─────
    HF_API_KEY      = os.environ.get('HF_API_KEY', '')

    MAX_UPLOAD_SIZE    = 5 * 1024 * 1024
    UPLOAD_FOLDER      = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    DATABASE           = os.path.join(os.path.dirname(__file__), 'agri.db')
    WEATHER_CACHE_MINUTES = 30
    ENV_FILE           = os.path.join(os.path.dirname(__file__), '.env')
