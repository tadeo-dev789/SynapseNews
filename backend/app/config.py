import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'

load_dotenv(dotenv_path = ENV_PATH)

class Settings:
    
    PROJECT_NAME : str = "SynapseNews"
    VERSION: str = "1.0.0"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    _keys_str = os.getenv("GEMINI_API_KEYS","")
    
    GEMINI_API_KEYS: list = [k.strip() for k in _keys_str.split(",") if k.strip()]
    
    EODHD_API_KEY = os.getenv("EODHD_API_KEY")
    
    TOP_STOCK_SYMBOLS = [
        s.strip()
        for s in os.getenv("TOP_STOCK_SYMBOLS", "").split(",")
        if s.strip()
    ]
    
    SELENIUM_URL: str = os.getenv("SELENIUM_URL", "http://selenium:4444/wd/hub")
    
    SMTP_SERVER: str = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")

settings = Settings()