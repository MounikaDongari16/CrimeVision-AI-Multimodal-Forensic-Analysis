import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_groq_client():
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found in environment. Please set it in .env")
    return Groq(api_key=GROQ_API_KEY)

def get_config():
    return {
        "groq_model": "llama-3.3-70b-versatile",
        "whisper_model_fast": "tiny",
        "whisper_model_accurate": "small",
        "languages": ["Telugu", "Hindi", "French"],
        "detection_model": "hustvl/yolos-tiny",
        "caption_model": "Salesforce/blip-image-captioning-base"
    }
