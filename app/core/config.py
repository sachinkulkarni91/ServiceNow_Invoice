
from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel
import os


class Settings(BaseModel):
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8080"))

settings = Settings()

# Debug print to check if the Google API key is loaded
import sys
print(f"[DEBUG] GOOGLE_API_KEY loaded: '{settings.google_api_key}'", file=sys.stderr)
