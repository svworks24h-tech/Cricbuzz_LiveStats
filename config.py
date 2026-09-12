import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

DB_PATH = os.getenv("DB_PATH", str(ROOT / "cricbuzz.db"))
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "cricbuzz-cricket.p.rapidapi.com")
RAPIDAPI_BASE_URL = os.getenv("RAPIDAPI_BASE_URL", "https://cricbuzz-cricket.p.rapidapi.com")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "12"))
