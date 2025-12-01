import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
#OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Validate keys are present
def validate_config():
    missing = []
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    #if not OPENWEATHER_API_KEY:
    #    missing.append("OPENWEATHER_API_KEY")
    if not UNSPLASH_ACCESS_KEY:
        missing.append("UNSPLASH_ACCESS_KEY")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    
    if missing:
        raise ValueError(f"Missing API keys: {', '.join(missing)}")
    return True