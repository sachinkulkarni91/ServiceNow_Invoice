
from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel
import os
import base64
SERVICENOW_INSTANCE_URL = os.getenv("SERVICENOW_INSTANCE_URL", "https://your_instance.service-now.com")
SERVICENOW_USERNAME = os.getenv("SERVICENOW_USERNAME", "your_username")
SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD", "your_password")

# Base64-encoded HTTP Basic Auth string for ServiceNow
SERVICENOW_AUTH = base64.b64encode(f"{SERVICENOW_USERNAME}:{SERVICENOW_PASSWORD}".encode()).decode()


class Settings(BaseModel):
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8080"))

settings = Settings()

# Debug print to check if the Google API key is loaded
import sys
print(f"[DEBUG] GOOGLE_API_KEY loaded: '{settings.google_api_key}'", file=sys.stderr)
