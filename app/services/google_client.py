import httpx
from ..core.config import settings

GOOGLE_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

async def google_generate_content(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": settings.google_api_key
    }
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(GOOGLE_API_URL, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        # Extract the generated text from the response
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return ""
