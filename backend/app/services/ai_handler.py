import google.generativeai as genai
import os

from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def configure_ai():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR FALTA LA GEMINI_API_KEY en el .env")
        return False
    genai.configure(api_key=api_key)
    return True