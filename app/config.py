import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = APP_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
SAMPLE_DIR = DATA_DIR / "sample_tenders"

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv(BASE_DIR / ".env")

class Settings:
    # Sarvam AI configuration
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    SARVAM_BASE_URL: str = os.getenv("SARVAM_BASE_URL", "https://api.sarvam.ai")
    SARVAM_CHAT_MODEL: str = os.getenv("SARVAM_CHAT_MODEL", "sarvam-105b")
    
    # Storage files
    COMPANY_PROFILE_PATH: Path = DATA_DIR / "company_profile.json"
    PAST_PROPOSALS_PATH: Path = DATA_DIR / "past_proposals.json"
    TEAM_PROFILES_PATH: Path = DATA_DIR / "team_profiles.json"
    
    # App settings
    APP_NAME: str = "TenderAI - Sarvam Bidding Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")

settings = Settings()

def update_api_key(new_key: str):
    """Updates runtime API key and persists to .env file"""
    settings.SARVAM_API_KEY = new_key.strip()
    env_file = BASE_DIR / ".env"
    
    # Read existing lines or create new
    existing_lines = []
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            existing_lines = f.readlines()
            
    updated = False
    new_lines = []
    for line in existing_lines:
        if line.strip().startswith("SARVAM_API_KEY="):
            new_lines.append(f"SARVAM_API_KEY={new_key.strip()}\n")
            updated = True
        else:
            new_lines.append(line)
            
    if not updated:
        new_lines.append(f"SARVAM_API_KEY={new_key.strip()}\n")
        
    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
